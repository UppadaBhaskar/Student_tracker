from app.models.enums import AssignmentStatus, AttemptStatus, AttendanceStatus
from app.repositories.question_repository import QuestionAttemptRepository, QuestionRepository
from app.repositories.student_repository import StudentRepository
from app.repositories.tracking_repository import AssignmentRepository, AttendanceRepository, TestScoreRepository
from app.services.attempt_service import AttemptService
from app.services.entity_service import EntityService
from app.services.leaderboard_service import LeaderboardService
from app.services.question_service import QuestionService
from app.services.risk_service import RiskService
from app.services.student_trend_service import StudentTrendService
from app.services.subject_performance_service import SubjectPerformanceService
from app.utils.datetime_utils import compute_workshop_day


class DashboardService:
    def __init__(self):
        self.entity_service = EntityService()
        self.student_repo = StudentRepository()
        self.attendance_repo = AttendanceRepository()
        self.assignment_repo = AssignmentRepository()
        self.test_repo = TestScoreRepository()
        self.attempt_repo = QuestionAttemptRepository()
        self.question_service = QuestionService()
        self.leaderboard_service = LeaderboardService()
        self.risk_service = RiskService()
        self.subject_performance = SubjectPerformanceService()
        self.trend_service = StudentTrendService()
        self.attempt_service = AttemptService()

    def trainer_dashboard(self, entity_id: int) -> dict:
        entity = self.entity_service.get_entity(entity_id)
        today_day = compute_workshop_day(entity.start_date, entity.total_days)
        total_students = self.student_repo.count_by_entity(entity_id)

        attendance = self.attendance_repo.list_by_entity_day(entity_id, today_day)
        assignments = self.assignment_repo.list_by_entity_day(entity_id, today_day)
        tests = self.test_repo.list_by_entity_day(entity_id, today_day)

        present = sum(1 for a in attendance if a.status == AttendanceStatus.PRESENT)
        completed = sum(1 for a in assignments if a.status == AssignmentStatus.COMPLETED)
        active_q = self.question_service.get_active_question()
        pending = self.attempt_repo.count_pending()
        risk_counts = self.risk_service.count_at_risk(entity_id)
        top_bottom = self.leaderboard_service.get_top_bottom(entity_id, 5)
        subjects = self.subject_performance.get_top_and_weakest(entity_id)
        at_risk = self.risk_service.list_at_risk_students(entity_id)
        analytics = self._dashboard_analytics(entity_id, entity.total_days, today_day)

        return {
            "today_summary": {
                "current_day": today_day,
                "total_students": total_students,
                "present_today": present,
                "attendance_pct": round(present / total_students * 100, 1) if total_students else 0,
                "assignment_completion_pct": round(completed / total_students * 100, 1)
                if total_students
                else 0,
                "avg_test_score": round(sum(t.score for t in tests) / len(tests), 2) if tests else None,
                "active_question": {
                    "id": active_q.id,
                    "title": active_q.title,
                    "subject": active_q.subject.name if active_q and active_q.subject else None,
                }
                if active_q
                else None,
                "pending_verifications": pending,
                "risk_students_count": risk_counts["yellow"] + risk_counts["red"],
            },
            "top_5_students": top_bottom["top"],
            "bottom_5_students": top_bottom["bottom"],
            "top_subject": subjects["top_subject"],
            "weakest_subject": subjects["weakest_subject"],
            "risk_distribution": risk_counts,
            "at_risk_students": at_risk[:15],
            "attendance_trend": analytics["attendance_trend"],
            "question_performance_trend": analytics["question_performance_trend"],
            "question_participation_today": analytics["question_participation_today"],
        }

    def _dashboard_analytics(self, entity_id: int, total_days: int, current_day: int) -> dict:
        from app.services.analytics_service import AnalyticsService

        analytics = AnalyticsService()
        days = list(range(1, min(current_day, total_days) + 1)) or [1]
        total_students = self.student_repo.count_by_entity(entity_id)

        participation = analytics._participation_trend(entity_id, [current_day], total_students)
        today_participation = participation[0] if participation else None

        return {
            "attendance_trend": analytics._attendance_trend(entity_id, days, total_students),
            "question_performance_trend": analytics._question_performance_trend(entity_id, days),
            "question_participation_today": today_participation,
        }

    def student_dashboard(self, student_id: int) -> dict:
        from app.repositories.tracking_repository import PresentationScoreRepository

        student = self.student_repo.get_by_id(student_id)
        if not student:
            from app.exceptions import NotFoundException
            raise NotFoundException("Student not found")

        board = self.leaderboard_service.get_leaderboard(student.entity_id)
        position = next((e["rank"] for e in board if e["student_id"] == student_id), None)

        risk = self.risk_service.assess_student(student_id)
        trends = self.trend_service.get_trends(student_id)
        history = self.attempt_service.get_question_history(student_id)

        presentation_repo = PresentationScoreRepository()
        presentations = presentation_repo.list_by_student(student_id)
        tests = self.test_repo.list_by_student(student_id)

        approved = [
            a for a in self.attempt_repo.list_by_student(student_id) if a.status == AttemptStatus.APPROVED
        ]
        from app.services.rank_service import RankService
        rank_service = RankService()
        ranks = []
        for a in approved:
            rm = rank_service.get_approved_rank_map(a.question_id)
            if a.id in rm:
                ranks.append(rm[a.id])

        completion_times = []
        for a in approved:
            q = a.question
            if q and q.revealed_at:
                completion_times.append((a.clicked_at - q.revealed_at).total_seconds())
        avg_completion = (
            round(sum(completion_times) / len(completion_times), 2) if completion_times else None
        )

        return {
            "overview": {
                "attendance_pct": risk["metrics"]["attendance_pct"],
                "assignment_pct": risk["metrics"]["assignment_pct"],
                "avg_presentation_score": round(
                    sum(p.score for p in presentations) / len(presentations), 2
                )
                if presentations
                else None,
                "avg_test_score": round(sum(t.score for t in tests) / len(tests), 2) if tests else None,
                "leaderboard_position": position,
                "risk": risk,
            },
            "question_stats": {
                "questions_solved": len(approved),
                "avg_approved_rank": round(sum(ranks) / len(ranks), 2) if ranks else None,
                "total_points": sum(a.points for a in approved),
                "avg_completion_time_seconds": avg_completion,
            },
            "performance_trends": trends,
            "question_history": history,
        }
