from app.exceptions import ConflictException, NotFoundException, ValidationException
from app.models.enums import AttemptStatus, QuestionStatus
from app.models.question import QuestionAttempt
from app.repositories.question_repository import QuestionAttemptRepository, QuestionRepository
from app.services.question_service import QuestionService
from app.services.rank_service import RankService
from app.services.student_service import StudentService
from app.utils.datetime_utils import utc_now
from app.utils.points import calculate_points


class AttemptService:
    def __init__(self):
        self.attempt_repo = QuestionAttemptRepository()
        self.question_repo = QuestionRepository()
        self.question_service = QuestionService()
        self.student_service = StudentService()
        self.rank_service = RankService()

    def complete_active_question(self, user_id: int) -> dict:
        student = self.student_service.get_by_user_id(user_id)
        question = self.question_service.get_active_question()
        if not question:
            raise NotFoundException("No active question")
        if question.status != QuestionStatus.ACTIVE or not question.revealed_at:
            raise ValidationException("Question is not available for completion")

        existing_approved = self.attempt_repo.get_approved_for_student_question(
            student.id, question.id
        )
        if existing_approved:
            raise ConflictException("You already have an approved attempt for this question")

        pending = [
            a
            for a in self.attempt_repo.list_by_question(question.id)
            if a.student_id == student.id and a.status == AttemptStatus.PENDING
        ]
        if pending:
            raise ConflictException("You already have a pending attempt awaiting verification")

        clicked_at = utc_now()
        question = self.question_repo.get_by_id(question.id)

        earlier_count = self.attempt_repo.count_earlier_clicks(question.id, clicked_at)
        click_rank = earlier_count + 1
        points = calculate_points(
            question.revealed_at, clicked_at, question.timer_minutes, question.max_points
        )

        attempt = QuestionAttempt(
            question_id=question.id,
            student_id=student.id,
            clicked_at=clicked_at,
            status=AttemptStatus.PENDING,
            click_rank=click_rank,
            points=points,
        )
        self.attempt_repo.add(attempt)
        self.attempt_repo.commit()

        return self.rank_service.enrich_attempts([attempt])[0]

    def list_attempts(self, question_id: int, status: str | None = None) -> list[dict]:
        self.question_service.get_question(question_id)
        status_enum = AttemptStatus(status) if status else None
        attempts = self.attempt_repo.list_by_question(question_id, status_enum)
        return self.rank_service.enrich_attempts(attempts)

    def approve_attempt(self, attempt_id: int, trainer_notes: str | None = None) -> dict:
        attempt = self.attempt_repo.get_by_id(attempt_id)
        if not attempt:
            raise NotFoundException("Attempt not found")
        if attempt.status != AttemptStatus.PENDING:
            raise ValidationException("Only pending attempts can be approved")

        existing = self.attempt_repo.get_approved_for_student_question(
            attempt.student_id, attempt.question_id
        )
        if existing:
            raise ConflictException("Student already has an approved attempt for this question")

        attempt.status = AttemptStatus.APPROVED
        attempt.approved_at = utc_now()
        attempt.trainer_notes = trainer_notes
        self.attempt_repo.commit()
        return self.rank_service.enrich_attempts([attempt])[0]

    def reject_attempt(self, attempt_id: int, trainer_notes: str | None = None) -> dict:
        attempt = self.attempt_repo.get_by_id(attempt_id)
        if not attempt:
            raise NotFoundException("Attempt not found")
        if attempt.status != AttemptStatus.PENDING:
            raise ValidationException("Only pending attempts can be rejected")

        attempt.status = AttemptStatus.REJECTED
        attempt.trainer_notes = trainer_notes
        self.attempt_repo.commit()
        return self.rank_service.enrich_attempts([attempt])[0]

    def get_question_history(self, student_id: int) -> list[dict]:
        student = self.student_service.get_student(student_id)
        questions = self.question_repo.list_by_entity(student.entity_id)
        attempts = self.attempt_repo.list_by_student(student_id)

        by_question: dict[int, list] = {}
        for a in attempts:
            by_question.setdefault(a.question_id, []).append(a)

        history = []
        for q in questions:
            q_attempts = sorted(by_question.get(q.id, []), key=lambda x: x.clicked_at)
            if not q_attempts:
                continue

            approved = next((a for a in q_attempts if a.status == AttemptStatus.APPROVED), None)
            latest = q_attempts[-1]
            rank_map = self.rank_service.get_approved_rank_map(q.id)

            completion_time = None
            if approved and q.revealed_at:
                completion_time = (approved.clicked_at - q.revealed_at).total_seconds()

            history.append(
                {
                    "question_id": q.id,
                    "title": q.title,
                    "subject": q.subject.name if q.subject else None,
                    "day": q.day,
                    "max_points": q.max_points,
                    "attempt_count": len(q_attempts),
                    "final_status": (approved or latest).status.value,
                    "approved_rank": rank_map.get(approved.id) if approved else None,
                    "points": approved.points if approved else None,
                    "completion_time_seconds": completion_time,
                    "attempts": self.rank_service.enrich_attempts(q_attempts),
                }
            )
        return history

    def get_question_attempts_detail(self, student_id: int, question_id: int) -> list[dict]:
        self.student_service.get_student(student_id)
        self.question_service.get_question(question_id)
        attempts = [
            a
            for a in self.attempt_repo.list_by_question(question_id)
            if a.student_id == student_id
        ]
        return self.rank_service.enrich_attempts(attempts)
