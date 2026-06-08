from sqlalchemy import select

from app.extensions import db
from app.models import Assignment, Attendance, DailyNote, PresentationScore, TestScore
from app.repositories.base import BaseRepository


class AttendanceRepository(BaseRepository[Attendance]):
    model = Attendance

    def list_by_entity_day(self, entity_id: int, day: int) -> list[Attendance]:
        return db.session.scalars(
            select(Attendance).where(Attendance.entity_id == entity_id, Attendance.day == day)
        ).all()

    def get_record(self, entity_id: int, student_id: int, day: int) -> Attendance | None:
        return db.session.scalar(
            select(Attendance).where(
                Attendance.entity_id == entity_id,
                Attendance.student_id == student_id,
                Attendance.day == day,
            )
        )

    def list_by_entity(self, entity_id: int) -> list[Attendance]:
        return db.session.scalars(select(Attendance).where(Attendance.entity_id == entity_id)).all()

    def list_by_student(self, student_id: int) -> list[Attendance]:
        return db.session.scalars(select(Attendance).where(Attendance.student_id == student_id)).all()


class AssignmentRepository(BaseRepository[Assignment]):
    model = Assignment

    def list_by_entity_day(self, entity_id: int, day: int) -> list[Assignment]:
        return db.session.scalars(
            select(Assignment).where(Assignment.entity_id == entity_id, Assignment.day == day)
        ).all()

    def get_record(self, entity_id: int, student_id: int, day: int) -> Assignment | None:
        return db.session.scalar(
            select(Assignment).where(
                Assignment.entity_id == entity_id,
                Assignment.student_id == student_id,
                Assignment.day == day,
            )
        )

    def list_by_entity(self, entity_id: int) -> list[Assignment]:
        return db.session.scalars(select(Assignment).where(Assignment.entity_id == entity_id)).all()

    def list_by_student(self, student_id: int) -> list[Assignment]:
        return db.session.scalars(select(Assignment).where(Assignment.student_id == student_id)).all()


class PresentationScoreRepository(BaseRepository[PresentationScore]):
    model = PresentationScore

    def list_by_entity_day(self, entity_id: int, day: int | None = None) -> list[PresentationScore]:
        stmt = select(PresentationScore).where(PresentationScore.entity_id == entity_id)
        if day is not None:
            stmt = stmt.where(PresentationScore.day == day)
        return db.session.scalars(stmt).all()

    def get_record(
        self, entity_id: int, student_id: int, subject_id: int, day: int
    ) -> PresentationScore | None:
        return db.session.scalar(
            select(PresentationScore).where(
                PresentationScore.entity_id == entity_id,
                PresentationScore.student_id == student_id,
                PresentationScore.subject_id == subject_id,
                PresentationScore.day == day,
            )
        )

    def list_by_student(self, student_id: int) -> list[PresentationScore]:
        return db.session.scalars(
            select(PresentationScore).where(PresentationScore.student_id == student_id)
        ).all()


class TestScoreRepository(BaseRepository[TestScore]):
    model = TestScore

    def list_by_entity(self, entity_id: int) -> list[TestScore]:
        return db.session.scalars(select(TestScore).where(TestScore.entity_id == entity_id)).all()

    def list_by_entity_day(self, entity_id: int, day: int) -> list[TestScore]:
        return db.session.scalars(
            select(TestScore).where(TestScore.entity_id == entity_id, TestScore.day == day)
        ).all()

    def get_record(
        self, entity_id: int, student_id: int, subject_id: int, day: int
    ) -> TestScore | None:
        return db.session.scalar(
            select(TestScore).where(
                TestScore.entity_id == entity_id,
                TestScore.student_id == student_id,
                TestScore.subject_id == subject_id,
                TestScore.day == day,
            )
        )

    def list_by_student(self, student_id: int) -> list[TestScore]:
        return db.session.scalars(select(TestScore).where(TestScore.student_id == student_id)).all()


class DailyNoteRepository(BaseRepository[DailyNote]):
    model = DailyNote

    def get_by_entity_day(self, entity_id: int, day: int) -> DailyNote | None:
        return db.session.scalar(
            select(DailyNote).where(DailyNote.entity_id == entity_id, DailyNote.day == day)
        )

    def list_by_entity(self, entity_id: int) -> list[DailyNote]:
        return db.session.scalars(
            select(DailyNote).where(DailyNote.entity_id == entity_id).order_by(DailyNote.day)
        ).all()
