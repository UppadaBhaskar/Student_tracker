from app.models.enums import AttemptStatus
from app.repositories.question_repository import QuestionAttemptRepository, QuestionRepository
from app.repositories.student_repository import StudentRepository
from app.services.entity_service import EntityService
from app.services.rank_service import RankService


class QuestionStatsService:
    def __init__(self):
        self.question_repo = QuestionRepository()
        self.attempt_repo = QuestionAttemptRepository()
        self.student_repo = StudentRepository()
        self.entity_service = EntityService()
        self.rank_service = RankService()

    def stats_for_entity(self, entity_id: int) -> list[dict]:
        self.entity_service.get_entity(entity_id)
        questions = self.question_repo.list_by_entity(entity_id)
        return [self._stats_for_question(q) for q in questions]

    def stats_for_question(self, question_id: int) -> dict:
        question = self.question_repo.get_by_id(question_id)
        if not question:
            from app.exceptions import NotFoundException
            raise NotFoundException("Question not found")
        return self._stats_for_question(question)

    def _stats_for_question(self, question) -> dict:
        total_students = self.student_repo.count_by_entity(question.entity_id)
        attempts = self.attempt_repo.list_by_question(question.id)
        approved = [a for a in attempts if a.status == AttemptStatus.APPROVED]
        pending = [a for a in attempts if a.status == AttemptStatus.PENDING]
        rejected = [a for a in attempts if a.status == AttemptStatus.REJECTED]

        attempted_students = len({a.student_id for a in attempts})
        approved_students = len({a.student_id for a in approved})

        avg_completion_time = None
        avg_points = None
        fastest_student = None
        highest_ranked_student = None

        if approved:
            times = [
                (a.clicked_at - question.revealed_at).total_seconds()
                for a in approved
                if question.revealed_at
            ]
            if times:
                avg_completion_time = sum(times) / len(times)
                fastest = min(approved, key=lambda a: a.clicked_at)
                fastest_student = {
                    "student_id": fastest.student_id,
                    "student_name": fastest.student.full_name,
                    "completion_time_seconds": (fastest.clicked_at - question.revealed_at).total_seconds(),
                }

            avg_points = sum(a.points for a in approved) / len(approved)
            rank_map = self.rank_service.get_approved_rank_map(question.id)
            top = next((a for a in approved if rank_map.get(a.id) == 1), None)
            if top:
                highest_ranked_student = {
                    "student_id": top.student_id,
                    "student_name": top.student.full_name,
                    "approved_rank": 1,
                }

        return {
            "question_id": question.id,
            "title": question.title,
            "subject": question.subject.name if question.subject else None,
            "day": question.day,
            "difficulty": question.difficulty.value,
            "max_points": question.max_points,
            "total_students": total_students,
            "attempted_students": attempted_students,
            "approved_students": approved_students,
            "rejected_attempts": len(rejected),
            "pending_attempts": len(pending),
            "avg_completion_time_seconds": avg_completion_time,
            "avg_points": avg_points,
            "fastest_student": fastest_student,
            "highest_ranked_student": highest_ranked_student,
        }
