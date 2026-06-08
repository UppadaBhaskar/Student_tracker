from datetime import datetime

from sqlalchemy import DateTime, Enum, Float, ForeignKey, Index, Integer
from sqlalchemy.orm import Mapped, mapped_column

from app.extensions import db
from app.models.enums import AssignmentStatus, AttendanceStatus
from app.utils.datetime_utils import utc_now


class Attendance(db.Model):
    __tablename__ = "attendance"

    id: Mapped[int] = mapped_column(primary_key=True)
    entity_id: Mapped[int] = mapped_column(ForeignKey("entities.id"), nullable=False)
    student_id: Mapped[int] = mapped_column(ForeignKey("students.id"), nullable=False)
    day: Mapped[int] = mapped_column(Integer, nullable=False)
    status: Mapped[AttendanceStatus] = mapped_column(
        Enum(AttendanceStatus, native_enum=False, length=20), nullable=False
    )
    marked_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, nullable=False
    )

    __table_args__ = (
        db.UniqueConstraint("entity_id", "student_id", "day", name="uq_attendance"),
        Index("ix_attendance_entity_day", "entity_id", "day"),
    )


class Assignment(db.Model):
    __tablename__ = "assignments"

    id: Mapped[int] = mapped_column(primary_key=True)
    entity_id: Mapped[int] = mapped_column(ForeignKey("entities.id"), nullable=False)
    student_id: Mapped[int] = mapped_column(ForeignKey("students.id"), nullable=False)
    day: Mapped[int] = mapped_column(Integer, nullable=False)
    status: Mapped[AssignmentStatus] = mapped_column(
        Enum(AssignmentStatus, native_enum=False, length=20), nullable=False
    )
    marked_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, nullable=False
    )

    __table_args__ = (
        db.UniqueConstraint("entity_id", "student_id", "day", name="uq_assignment"),
        Index("ix_assignment_entity_day", "entity_id", "day"),
    )


class PresentationScore(db.Model):
    __tablename__ = "presentation_scores"

    id: Mapped[int] = mapped_column(primary_key=True)
    entity_id: Mapped[int] = mapped_column(ForeignKey("entities.id"), nullable=False)
    student_id: Mapped[int] = mapped_column(ForeignKey("students.id"), nullable=False)
    subject_id: Mapped[int] = mapped_column(ForeignKey("subjects.id"), nullable=False)
    day: Mapped[int] = mapped_column(Integer, nullable=False)
    score: Mapped[float] = mapped_column(Float, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False
    )

    __table_args__ = (
        db.UniqueConstraint(
            "entity_id", "student_id", "subject_id", "day", name="uq_presentation_score"
        ),
    )


class TestScore(db.Model):
    __tablename__ = "test_scores"

    id: Mapped[int] = mapped_column(primary_key=True)
    entity_id: Mapped[int] = mapped_column(ForeignKey("entities.id"), nullable=False)
    student_id: Mapped[int] = mapped_column(ForeignKey("students.id"), nullable=False)
    subject_id: Mapped[int] = mapped_column(ForeignKey("subjects.id"), nullable=False)
    day: Mapped[int] = mapped_column(Integer, nullable=False)
    score: Mapped[float] = mapped_column(Float, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False
    )

    __table_args__ = (
        db.UniqueConstraint(
            "entity_id", "student_id", "subject_id", "day", name="uq_test_score"
        ),
    )
