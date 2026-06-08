from sqlalchemy import select
from sqlalchemy.orm import joinedload

from app.extensions import db
from app.models import Student, StudentRemark
from app.repositories.base import BaseRepository


class StudentRepository(BaseRepository[Student]):
    model = Student

    def list_by_entity(self, entity_id: int) -> list[Student]:
        return db.session.scalars(
            select(Student)
            .options(joinedload(Student.user))
            .where(Student.entity_id == entity_id)
            .order_by(Student.full_name)
        ).all()

    def get_by_id(self, student_id: int) -> Student | None:
        return db.session.scalar(
            select(Student).options(joinedload(Student.user)).where(Student.id == student_id)
        )

    def get_by_usn(self, usn: str) -> Student | None:
        return db.session.scalar(select(Student).where(Student.usn == usn))

    def get_by_user_id(self, user_id: int) -> Student | None:
        return db.session.scalar(
            select(Student).options(joinedload(Student.user)).where(Student.user_id == user_id)
        )

    def count_by_entity(self, entity_id: int) -> int:
        return db.session.scalar(
            select(db.func.count()).select_from(Student).where(Student.entity_id == entity_id)
        ) or 0


class StudentRemarkRepository(BaseRepository[StudentRemark]):
    model = StudentRemark

    def list_by_student(self, student_id: int) -> list[StudentRemark]:
        return db.session.scalars(
            select(StudentRemark)
            .where(StudentRemark.student_id == student_id)
            .order_by(StudentRemark.created_at.desc())
        ).all()
