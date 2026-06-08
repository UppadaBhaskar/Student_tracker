from app.models.enums import AttemptStatus
from app.repositories.entity_repository import SubjectRepository
from app.repositories.question_repository import QuestionAttemptRepository, QuestionRepository
from app.repositories.student_repository import StudentRepository
from app.services.entity_service import EntityService
from app.services.rank_service import RankService


class SubjectPerformanceService:
    def __init__(self):
        self.subject_repo = SubjectRepository()
        self.question_repo = QuestionRepository()
        self.attempt_repo = QuestionAttemptRepository()
        self.student_repo = StudentRepository()
        self.entity_service = EntityService()
        self.rank_service = RankService()

    def analyze_subjects(self, entity_id: int) -> list[dict]:
        self.entity_service.get_entity(entity_id)
        subjects = self.subject_repo.list_by_entity(entity_id)
        total_students = self.student_repo.count_by_entity(entity_id)
        return [self._analyze_subject(s, total_students) for s in subjects]

    def get_top_and_weakest(self, entity_id: int) -> dict:
        analysis = self.analyze_subjects(entity_id)
        if not analysis:
            return {"top_subject": None, "weakest_subject": None}

        with_questions = [a for a in analysis if a["question_count"] > 0]
        if not with_questions:
            return {"top_subject": None, "weakest_subject": None}

        top = min(with_questions, key=lambda a: a["difficulty_score"])
        weakest = max(with_questions, key=lambda a: a["difficulty_score"])
        return {"top_subject": top, "weakest_subject": weakest}

    def _analyze_subject(self, subject, total_students: int) -> dict:
        questions = [
            q for q in self.question_repo.list_by_entity(subject.entity_id) if q.subject_id == subject.id
        ]
        question_ids = [q.id for q in questions]
        avg_max_points = (
            sum(q.max_points for q in questions) / len(questions) if questions else 10
        )

        approved_attempts = []
        for qid in question_ids:
            approved_attempts.extend(
                self.attempt_repo.list_by_question(qid, AttemptStatus.APPROVED)
            )

        avg_points = None
        avg_rank = None
        completion_rate = 0.0

        if approved_attempts:
            avg_points = sum(a.points for a in approved_attempts) / len(approved_attempts)
            ranks = []
            for a in approved_attempts:
                rank_map = self.rank_service.get_approved_rank_map(a.question_id)
                if a.id in rank_map:
                    ranks.append(rank_map[a.id])
            avg_rank = sum(ranks) / len(ranks) if ranks else None

        if total_students and question_ids:
            approved_student_ids = {a.student_id for a in approved_attempts}
            completion_rate = len(approved_student_ids) / total_students * 100

        difficulty_score = self._difficulty_score(
            avg_points, avg_max_points, avg_rank, total_students, completion_rate
        )

        return {
            "subject_id": subject.id,
            "subject_name": subject.name,
            "avg_points": round(avg_points, 2) if avg_points is not None else None,
            "avg_rank": round(avg_rank, 2) if avg_rank is not None else None,
            "completion_rate": round(completion_rate, 2),
            "question_count": len(questions),
            "difficulty_score": round(difficulty_score, 2),
        }

    @staticmethod
    def _difficulty_score(
        avg_points: float | None,
        avg_max_points: float,
        avg_rank: float | None,
        total_students: int,
        completion_rate: float,
    ) -> float:
        points_pct = (avg_points / avg_max_points * 100) if avg_points is not None else 0
        rank_pct = (avg_rank / total_students * 100) if avg_rank and total_students else 50
        return (100 - points_pct) * 0.35 + rank_pct * 0.35 + (100 - completion_rate) * 0.30
