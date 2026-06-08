from app.models.enums import AssignmentStatus, AttemptStatus, AttendanceStatus
from app.repositories.question_repository import QuestionAttemptRepository, QuestionRepository
from app.repositories.student_repository import StudentRepository
from app.repositories.tracking_repository import AssignmentRepository, AttendanceRepository, TestScoreRepository
from app.services.entity_service import EntityService


class StudentTrendService:
    def __init__(self):
        self.attendance_repo = AttendanceRepository()
        self.assignment_repo = AssignmentRepository()
        self.test_repo = TestScoreRepository()
        self.attempt_repo = QuestionAttemptRepository()
        self.question_repo = QuestionRepository()
        self.student_repo = StudentRepository()
        self.entity_service = EntityService()

    def get_trends(self, student_id: int) -> dict:
        student = self.student_repo.get_by_id(student_id)
        if not student:
            from app.exceptions import NotFoundException
            raise NotFoundException("Student not found")

        entity = self.entity_service.get_entity(student.entity_id)
        days = range(1, entity.total_days + 1)

        attendance_map = {r.day: r for r in self.attendance_repo.list_by_student(student_id)}
        assignment_map = {r.day: r for r in self.assignment_repo.list_by_student(student_id)}
        test_records = self.test_repo.list_by_student(student_id)
        test_by_day: dict[int, list] = {}
        for t in test_records:
            test_by_day.setdefault(t.day, []).append(t.score)

        approved = [
            a for a in self.attempt_repo.list_by_student(student_id) if a.status == AttemptStatus.APPROVED
        ]
        question_by_day: dict[int, list] = {}
        for a in approved:
            if a.question:
                normalized = a.points / a.question.max_points * 100
                question_by_day.setdefault(a.question.day, []).append(normalized)

        return {
            "student_id": student_id,
            "attendance_trend": [
                {
                    "day": d,
                    "value": 100
                    if attendance_map.get(d) and attendance_map[d].status == AttendanceStatus.PRESENT
                    else 0
                    if attendance_map.get(d)
                    else None,
                }
                for d in days
            ],
            "assignment_trend": [
                {
                    "day": d,
                    "value": 100
                    if assignment_map.get(d) and assignment_map[d].status == AssignmentStatus.COMPLETED
                    else 0
                    if assignment_map.get(d)
                    else None,
                }
                for d in days
            ],
            "test_trend": [
                {
                    "day": d,
                    "value": sum(test_by_day[d]) / len(test_by_day[d]) if d in test_by_day else None,
                }
                for d in days
            ],
            "question_performance_trend": [
                {
                    "day": d,
                    "value": sum(question_by_day[d]) / len(question_by_day[d])
                    if d in question_by_day
                    else None,
                }
                for d in days
            ],
        }
