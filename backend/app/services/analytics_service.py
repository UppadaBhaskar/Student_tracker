from app.models.enums import AssignmentStatus, AttemptStatus, AttendanceStatus
from app.repositories.question_repository import QuestionAttemptRepository, QuestionRepository
from app.repositories.student_repository import StudentRepository
from app.repositories.tracking_repository import (
    AssignmentRepository,
    AttendanceRepository,
    PresentationScoreRepository,
    TestScoreRepository,
)
from app.services.entity_service import EntityService
from app.services.leaderboard_service import LeaderboardService
from app.services.risk_service import RiskService
from app.services.subject_performance_service import SubjectPerformanceService


class AnalyticsService:
    def __init__(self):
        self.entity_service = EntityService()
        self.student_repo = StudentRepository()
        self.attendance_repo = AttendanceRepository()
        self.assignment_repo = AssignmentRepository()
        self.presentation_repo = PresentationScoreRepository()
        self.test_repo = TestScoreRepository()
        self.question_repo = QuestionRepository()
        self.attempt_repo = QuestionAttemptRepository()
        self.leaderboard_service = LeaderboardService()
        self.risk_service = RiskService()
        self.subject_performance = SubjectPerformanceService()

    def get_analytics(self, entity_id: int, day_filter: str | int = "all") -> dict:
        entity = self.entity_service.get_entity(entity_id)
        total_students = self.student_repo.count_by_entity(entity_id)
        days = self._filter_days(entity.total_days, day_filter)

        return {
            "attendance_trend": self._attendance_trend(entity_id, days, total_students),
            "assignment_trend": self._assignment_trend(entity_id, days, total_students),
            "presentation_trend": self._presentation_trend(entity_id, days),
            "test_trend": self._test_trend(entity_id, days),
            "question_performance_trend": self._question_performance_trend(entity_id, days),
            "question_participation_trend": self._participation_trend(entity_id, days, total_students),
            "subject_difficulty_analysis": self.subject_performance.analyze_subjects(entity_id),
            "risk_distribution": self.risk_service.count_at_risk(entity_id),
            "top_students_by_points": self._top_by_points(entity_id, 10),
            "top_students_by_avg_rank": self._top_by_avg_rank(entity_id, 10),
        }

    def get_daily_summary(self, entity_id: int, day_filter: str | int = "all") -> dict:
        entity = self.entity_service.get_entity(entity_id)
        total_students = self.student_repo.count_by_entity(entity_id)
        days = self._filter_days(entity.total_days, day_filter)

        from app.services.daily_notes_service import DailyNotesService
        notes_service = DailyNotesService()

        day_summaries = []
        for day in days:
            attendance = self.attendance_repo.list_by_entity_day(entity_id, day)
            assignments = self.assignment_repo.list_by_entity_day(entity_id, day)
            presentations = self.presentation_repo.list_by_entity_day(entity_id, day)
            tests = self.test_repo.list_by_entity_day(entity_id, day)
            notes = notes_service.get_notes(entity_id, day)

            present = sum(1 for a in attendance if a.status == AttendanceStatus.PRESENT)
            completed = sum(1 for a in assignments if a.status == AssignmentStatus.COMPLETED)

            questions_today = [q for q in self.question_repo.list_by_entity(entity_id) if q.day == day]
            q_points = []
            for q in questions_today:
                for a in self.attempt_repo.list_by_question(q.id, AttemptStatus.APPROVED):
                    q_points.append(a.points)

            day_summaries.append(
                {
                    "day": day,
                    "total_students": total_students,
                    "present_students": present,
                    "attendance_pct": round(present / total_students * 100, 1) if total_students else 0,
                    "assignment_completion_pct": round(completed / total_students * 100, 1)
                    if total_students
                    else 0,
                    "avg_presentation_score": round(
                        sum(p.score for p in presentations) / len(presentations), 2
                    )
                    if presentations
                    else None,
                    "avg_test_score": round(sum(t.score for t in tests) / len(tests), 2) if tests else None,
                    "avg_question_points": round(sum(q_points) / len(q_points), 2) if q_points else None,
                    "notes": notes[0].notes if notes else None,
                }
            )

        risk = self.risk_service.count_at_risk(entity_id)
        return {"days": day_summaries, "risk_counts": risk}

    def _filter_days(self, total_days: int, day_filter) -> list[int]:
        if day_filter == "all" or day_filter is None:
            return list(range(1, total_days + 1))
        return [int(day_filter)]

    def _attendance_trend(self, entity_id: int, days: list[int], total: int) -> list[dict]:
        result = []
        for day in days:
            records = self.attendance_repo.list_by_entity_day(entity_id, day)
            present = sum(1 for r in records if r.status == AttendanceStatus.PRESENT)
            result.append({"day": day, "value": round(present / total * 100, 1) if total else 0})
        return result

    def _assignment_trend(self, entity_id: int, days: list[int], total: int) -> list[dict]:
        result = []
        for day in days:
            records = self.assignment_repo.list_by_entity_day(entity_id, day)
            done = sum(1 for r in records if r.status == AssignmentStatus.COMPLETED)
            result.append({"day": day, "value": round(done / total * 100, 1) if total else 0})
        return result

    def _presentation_trend(self, entity_id: int, days: list[int]) -> list[dict]:
        result = []
        for day in days:
            scores = self.presentation_repo.list_by_entity_day(entity_id, day)
            result.append(
                {
                    "day": day,
                    "value": round(sum(s.score for s in scores) / len(scores), 2) if scores else None,
                }
            )
        return result

    def _test_trend(self, entity_id: int, days: list[int]) -> list[dict]:
        result = []
        for day in days:
            scores = self.test_repo.list_by_entity_day(entity_id, day)
            result.append(
                {
                    "day": day,
                    "value": round(sum(s.score for s in scores) / len(scores), 2) if scores else None,
                }
            )
        return result

    def _question_performance_trend(self, entity_id: int, days: list[int]) -> list[dict]:
        result = []
        questions = self.question_repo.list_by_entity(entity_id)
        for day in days:
            day_questions = [q for q in questions if q.day == day]
            normalized = []
            for q in day_questions:
                for a in self.attempt_repo.list_by_question(q.id, AttemptStatus.APPROVED):
                    normalized.append(a.points / q.max_points * 100)
            result.append(
                {"day": day, "value": round(sum(normalized) / len(normalized), 2) if normalized else None}
            )
        return result

    def _participation_trend(self, entity_id: int, days: list[int], total: int) -> list[dict]:
        result = []
        questions = self.question_repo.list_by_entity(entity_id)
        for day in days:
            day_questions = [q for q in questions if q.day == day]
            attempted = set()
            for q in day_questions:
                for a in self.attempt_repo.list_by_question(q.id):
                    attempted.add(a.student_id)
            result.append(
                {
                    "day": day,
                    "attempted": len(attempted),
                    "not_attempted": max(0, total - len(attempted)),
                }
            )
        return result

    def _top_by_points(self, entity_id: int, n: int) -> list[dict]:
        board = self.leaderboard_service.get_leaderboard(entity_id)
        sorted_board = sorted(board, key=lambda x: -x["total_points"])
        return sorted_board[:n]

    def _top_by_avg_rank(self, entity_id: int, n: int) -> list[dict]:
        board = [e for e in self.leaderboard_service.get_leaderboard(entity_id) if e["avg_approved_rank"]]
        sorted_board = sorted(board, key=lambda x: x["avg_approved_rank"])
        return sorted_board[:n]
