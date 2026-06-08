from app.models import QuestionAttempt
from app.models.enums import AttemptStatus
from app.repositories.question_repository import QuestionAttemptRepository


class RankService:
    def __init__(self):
        self.attempt_repo = QuestionAttemptRepository()

    def get_approved_rank_map(self, question_id: int) -> dict[int, int]:
        """Returns attempt_id -> approved_rank for approved attempts (gap-free)."""
        attempts = self.attempt_repo.list_by_question(question_id, AttemptStatus.APPROVED)
        return {a.id: rank for rank, a in enumerate(attempts, start=1)}

    def get_approved_rank_for_attempt(self, attempt: QuestionAttempt) -> int | None:
        if attempt.status != AttemptStatus.APPROVED:
            return None
        rank_map = self.get_approved_rank_map(attempt.question_id)
        return rank_map.get(attempt.id)

    def enrich_attempts(self, attempts: list[QuestionAttempt]) -> list[dict]:
        if not attempts:
            return []
        question_id = attempts[0].question_id
        rank_map = self.get_approved_rank_map(question_id)
        result = []
        for a in attempts:
            result.append(
                {
                    "id": a.id,
                    "question_id": a.question_id,
                    "student_id": a.student_id,
                    "student_name": a.student.full_name if a.student else None,
                    "clicked_at": a.clicked_at,
                    "approved_at": a.approved_at,
                    "status": a.status.value,
                    "click_rank": a.click_rank,
                    "approved_rank": rank_map.get(a.id),
                    "points": a.points,
                    "trainer_notes": a.trainer_notes,
                    "created_at": a.created_at,
                }
            )
        return result
