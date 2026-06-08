from app.models.enums import AssignmentStatus, AttemptStatus, AttendanceStatus
from app.repositories.question_repository import QuestionAttemptRepository
from app.repositories.student_repository import StudentRepository
from app.repositories.tracking_repository import (
    AssignmentRepository,
    AttendanceRepository,
    TestScoreRepository,
)
from app.services.rank_service import RankService


class RiskService:
    RISK_LEVELS = {"green": 0, "yellow": 1, "red": 2}

    def __init__(self):
        self.attendance_repo = AttendanceRepository()
        self.assignment_repo = AssignmentRepository()
        self.test_repo = TestScoreRepository()
        self.attempt_repo = QuestionAttemptRepository()
        self.student_repo = StudentRepository()
        self.rank_service = RankService()

    def assess_student(self, student_id: int) -> dict:
        attendance_pct = self._attendance_pct(student_id)
        assignment_pct = self._assignment_pct(student_id)
        test_pct = self._test_pct(student_id)
        question_pct = self._question_performance_pct(student_id)

        dimensions = {
            "attendance": self._level_attendance(attendance_pct),
            "assignments": self._level_assignment(assignment_pct),
            "tests": self._level_test(test_pct),
            "questions": self._level_question(question_pct),
        }
        overall = max(dimensions.values(), key=lambda d: self.RISK_LEVELS[d])

        return {
            "overall": overall,
            "dimensions": dimensions,
            "metrics": {
                "attendance_pct": round(attendance_pct, 1) if attendance_pct is not None else None,
                "assignment_pct": round(assignment_pct, 1) if assignment_pct is not None else None,
                "test_pct": round(test_pct, 1) if test_pct is not None else None,
                "question_performance_pct": round(question_pct, 1)
                if question_pct is not None
                else None,
            },
        }

    def count_at_risk(self, entity_id: int) -> dict:
        students = self.student_repo.list_by_entity(entity_id)
        counts = {"green": 0, "yellow": 0, "red": 0}
        for s in students:
            risk = self.assess_student(s.id)
            counts[risk["overall"]] += 1
        return counts

    def list_at_risk_students(
        self, entity_id: int, levels: tuple[str, ...] = ("yellow", "red")
    ) -> list[dict]:
        students = self.student_repo.list_by_entity(entity_id)
        at_risk = []
        for student in students:
            risk = self.assess_student(student.id)
            if risk["overall"] in levels:
                at_risk.append(
                    {
                        "student_id": student.id,
                        "student_name": student.full_name,
                        "usn": student.usn,
                        "overall": risk["overall"],
                        "dimensions": risk["dimensions"],
                        "metrics": risk["metrics"],
                    }
                )
        order = {"red": 0, "yellow": 1}
        at_risk.sort(key=lambda s: order.get(s["overall"], 2))
        return at_risk

    def _attendance_pct(self, student_id: int) -> float | None:
        records = self.attendance_repo.list_by_student(student_id)
        if not records:
            return None
        present = sum(1 for r in records if r.status == AttendanceStatus.PRESENT)
        return present / len(records) * 100

    def _assignment_pct(self, student_id: int) -> float | None:
        records = self.assignment_repo.list_by_student(student_id)
        if not records:
            return None
        done = sum(1 for r in records if r.status == AssignmentStatus.COMPLETED)
        return done / len(records) * 100

    def _test_pct(self, student_id: int) -> float | None:
        records = self.test_repo.list_by_student(student_id)
        if not records:
            return None
        return sum(r.score for r in records) / len(records)

    def _question_performance_pct(self, student_id: int) -> float | None:
        attempts = [
            a for a in self.attempt_repo.list_by_student(student_id) if a.status == AttemptStatus.APPROVED
        ]
        if not attempts:
            return None
        normalized = []
        for a in attempts:
            if a.question and a.question.max_points:
                normalized.append(a.points / a.question.max_points * 100)
        return sum(normalized) / len(normalized) if normalized else None

    @staticmethod
    def _level_attendance(pct: float | None) -> str:
        if pct is None:
            return "yellow"
        if pct >= 80:
            return "green"
        if pct >= 60:
            return "yellow"
        return "red"

    @staticmethod
    def _level_assignment(pct: float | None) -> str:
        return RiskService._level_attendance(pct)

    @staticmethod
    def _level_test(pct: float | None) -> str:
        if pct is None:
            return "yellow"
        if pct >= 60:
            return "green"
        if pct >= 40:
            return "yellow"
        return "red"

    @staticmethod
    def _level_question(pct: float | None) -> str:
        return RiskService._level_test(pct)
