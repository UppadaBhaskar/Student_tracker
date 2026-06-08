from app.models.enums import AttemptStatus
from app.repositories.question_repository import QuestionAttemptRepository, QuestionRepository
from app.repositories.student_repository import StudentRepository
from app.services.entity_service import EntityService
from app.services.rank_service import RankService
from app.services.risk_service import RiskService


class LeaderboardService:
    def __init__(self):
        self.student_repo = StudentRepository()
        self.question_repo = QuestionRepository()
        self.attempt_repo = QuestionAttemptRepository()
        self.entity_service = EntityService()
        self.rank_service = RankService()
        self.risk_service = RiskService()

    def get_leaderboard(self, entity_id: int, subject_id: int | None = None) -> list[dict]:
        self.entity_service.get_entity(entity_id)
        students = self.student_repo.list_by_entity(entity_id)
        questions = self.question_repo.list_by_entity(entity_id)
        if subject_id:
            questions = [q for q in questions if q.subject_id == subject_id]

        question_ids = [q.id for q in questions]
        question_map = {q.id: q for q in questions}

        entries = []
        for student in students:
            approved_attempts = [
                a
                for a in self.attempt_repo.list_by_student(student.id)
                if a.status == AttemptStatus.APPROVED and a.question_id in question_ids
            ]
            if not approved_attempts:
                risk = self.risk_service.assess_student(student.id)
                entries.append(
                    {
                        "rank": None,
                        "student_id": student.id,
                        "student_name": student.full_name,
                        "avg_approved_rank": None,
                        "total_points": 0,
                        "avg_completion_time_seconds": None,
                        "risk": risk["overall"],
                    }
                )
                continue

            approved_ranks = []
            total_points = 0
            completion_times = []
            for a in approved_attempts:
                rank_map = self.rank_service.get_approved_rank_map(a.question_id)
                ar = rank_map.get(a.id)
                if ar:
                    approved_ranks.append(ar)
                total_points += a.points
                q = question_map.get(a.question_id)
                if q and q.revealed_at:
                    completion_times.append((a.clicked_at - q.revealed_at).total_seconds())

            avg_rank = sum(approved_ranks) / len(approved_ranks) if approved_ranks else None
            avg_time = sum(completion_times) / len(completion_times) if completion_times else None
            risk = self.risk_service.assess_student(student.id)

            entries.append(
                {
                    "rank": None,
                    "student_id": student.id,
                    "student_name": student.full_name,
                    "avg_approved_rank": round(avg_rank, 2) if avg_rank else None,
                    "total_points": total_points,
                    "avg_completion_time_seconds": round(avg_time, 2) if avg_time else None,
                    "risk": risk["overall"],
                }
            )

        ranked = sorted(
            entries,
            key=lambda e: (
                e["avg_approved_rank"] if e["avg_approved_rank"] is not None else float("inf"),
                e["avg_completion_time_seconds"]
                if e["avg_completion_time_seconds"] is not None
                else float("inf"),
                -e["total_points"],
            ),
        )

        for i, entry in enumerate(ranked, start=1):
            if entry["avg_approved_rank"] is not None:
                entry["rank"] = i

        return ranked

    def get_top_bottom(self, entity_id: int, n: int = 5) -> dict:
        board = [e for e in self.get_leaderboard(entity_id) if e["avg_approved_rank"] is not None]
        return {
            "top": board[:n],
            "bottom": list(reversed(board[-n:])) if len(board) >= n else list(reversed(board)),
        }
