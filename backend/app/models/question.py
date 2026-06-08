from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, Index, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.extensions import db
from app.models.enums import AttemptStatus, QuestionDifficulty, QuestionStatus
from app.utils.datetime_utils import utc_now


class Question(db.Model):
    __tablename__ = "questions"

    id: Mapped[int] = mapped_column(primary_key=True)
    entity_id: Mapped[int] = mapped_column(ForeignKey("entities.id"), nullable=False)
    question_number: Mapped[int] = mapped_column(Integer, nullable=False)
    subject_id: Mapped[int] = mapped_column(ForeignKey("subjects.id"), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    day: Mapped[int] = mapped_column(Integer, nullable=False)
    timer_minutes: Mapped[int] = mapped_column(Integer, nullable=False)
    difficulty: Mapped[QuestionDifficulty] = mapped_column(
        Enum(QuestionDifficulty, native_enum=False, length=20),
        default=QuestionDifficulty.MEDIUM,
        nullable=False,
    )
    max_points: Mapped[int] = mapped_column(Integer, nullable=False, default=10)
    status: Mapped[QuestionStatus] = mapped_column(
        Enum(QuestionStatus, native_enum=False, length=20),
        default=QuestionStatus.DRAFT,
        nullable=False,
    )
    revealed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False
    )

    entity = relationship("WorkshopEntity", back_populates="questions")
    subject = relationship("Subject", back_populates="questions")
    attempts = relationship("QuestionAttempt", back_populates="question", cascade="all, delete-orphan")

    __table_args__ = (
        db.UniqueConstraint("entity_id", "question_number", name="uq_question_entity_number"),
        Index("ix_questions_entity_subject", "entity_id", "subject_id"),
    )


class QuestionAttempt(db.Model):
    __tablename__ = "question_attempts"

    id: Mapped[int] = mapped_column(primary_key=True)
    question_id: Mapped[int] = mapped_column(
        ForeignKey("questions.id", ondelete="CASCADE"), nullable=False
    )
    student_id: Mapped[int] = mapped_column(ForeignKey("students.id"), nullable=False)
    clicked_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    approved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    status: Mapped[AttemptStatus] = mapped_column(
        Enum(AttemptStatus, native_enum=False, length=20),
        default=AttemptStatus.PENDING,
        nullable=False,
    )
    click_rank: Mapped[int] = mapped_column(Integer, nullable=False)
    points: Mapped[int] = mapped_column(Integer, nullable=False)
    trainer_notes: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, nullable=False
    )

    question = relationship("Question", back_populates="attempts")
    student = relationship("Student", back_populates="attempts")

    __table_args__ = (
        Index("ix_attempts_question_status", "question_id", "status"),
        Index("ix_attempts_question_clicked", "question_id", "clicked_at"),
        Index("ix_attempts_student_question", "student_id", "question_id"),
    )
