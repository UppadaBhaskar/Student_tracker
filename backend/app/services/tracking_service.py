from app.exceptions import NotFoundException, ValidationException
from app.models.enums import AssignmentStatus, AttendanceStatus
from app.models.tracking import Assignment, Attendance, PresentationScore
from app.repositories.student_repository import StudentRepository
from app.repositories.tracking_repository import (
    AssignmentRepository,
    AttendanceRepository,
    PresentationScoreRepository,
)
from app.services.entity_service import EntityService
from app.utils.datetime_utils import utc_now


class TrackingService:
    def __init__(self):
        self.attendance_repo = AttendanceRepository()
        self.assignment_repo = AssignmentRepository()
        self.presentation_repo = PresentationScoreRepository()
        self.student_repo = StudentRepository()
        self.entity_service = EntityService()

    def get_attendance(self, entity_id: int, day: int) -> list[Attendance]:
        self._validate_day(entity_id, day)
        return self.attendance_repo.list_by_entity_day(entity_id, day)

    def upsert_attendance(self, entity_id: int, day: int, records: list[dict]) -> list[Attendance]:
        self._validate_day(entity_id, day)
        result = []
        for item in records:
            self._ensure_student_in_entity(entity_id, item["student_id"])
            record = self.attendance_repo.get_record(entity_id, item["student_id"], day)
            status = AttendanceStatus(item["status"])
            if record:
                record.status = status
                record.marked_at = utc_now()
            else:
                record = Attendance(
                    entity_id=entity_id,
                    student_id=item["student_id"],
                    day=day,
                    status=status,
                )
                self.attendance_repo.add(record)
            result.append(record)
        self.attendance_repo.commit()
        return result

    def get_assignments(self, entity_id: int, day: int) -> list[Assignment]:
        self._validate_day(entity_id, day)
        return self.assignment_repo.list_by_entity_day(entity_id, day)

    def upsert_assignments(self, entity_id: int, day: int, records: list[dict]) -> list[Assignment]:
        self._validate_day(entity_id, day)
        result = []
        for item in records:
            self._ensure_student_in_entity(entity_id, item["student_id"])
            record = self.assignment_repo.get_record(entity_id, item["student_id"], day)
            status = AssignmentStatus(item["status"])
            if record:
                record.status = status
                record.marked_at = utc_now()
            else:
                record = Assignment(
                    entity_id=entity_id,
                    student_id=item["student_id"],
                    day=day,
                    status=status,
                )
                self.assignment_repo.add(record)
            result.append(record)
        self.assignment_repo.commit()
        return result

    def get_presentations(self, entity_id: int, day: int | None = None) -> list[PresentationScore]:
        self.entity_service.get_entity(entity_id)
        return self.presentation_repo.list_by_entity_day(entity_id, day)

    def upsert_presentations(self, entity_id: int, records: list[dict]) -> list[PresentationScore]:
        self.entity_service.get_entity(entity_id)
        result = []
        for item in records:
            self._ensure_student_in_entity(entity_id, item["student_id"])
            self._validate_day(entity_id, item["day"])
            record = self.presentation_repo.get_record(
                entity_id, item["student_id"], item["subject_id"], item["day"]
            )
            if record:
                record.score = item["score"]
            else:
                record = PresentationScore(
                    entity_id=entity_id,
                    student_id=item["student_id"],
                    subject_id=item["subject_id"],
                    day=item["day"],
                    score=item["score"],
                )
                self.presentation_repo.add(record)
            result.append(record)
        self.presentation_repo.commit()
        return result

    def _validate_day(self, entity_id: int, day: int) -> None:
        entity = self.entity_service.get_entity(entity_id)
        if day < 1 or day > entity.total_days:
            raise ValidationException(f"Day must be between 1 and {entity.total_days}")

    def _ensure_student_in_entity(self, entity_id: int, student_id: int) -> None:
        student = self.student_repo.get_by_id(student_id)
        if not student or student.entity_id != entity_id:
            raise NotFoundException(f"Student {student_id} not found in entity")
