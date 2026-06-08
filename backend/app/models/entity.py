from datetime import date, datetime

from sqlalchemy import Date, DateTime, Enum, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.extensions import db
from app.models.enums import EntityType
from app.utils.datetime_utils import utc_now


class WorkshopEntity(db.Model):
    __tablename__ = "entities"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    entity_type: Mapped[EntityType] = mapped_column(
        Enum(EntityType, native_enum=False, length=30), nullable=False
    )
    total_days: Mapped[int] = mapped_column(Integer, nullable=False)
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    end_date: Mapped[date] = mapped_column(Date, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False
    )

    subjects = relationship("Subject", back_populates="entity", cascade="all, delete-orphan")
    students = relationship("Student", back_populates="entity")
    questions = relationship("Question", back_populates="entity")
    daily_notes = relationship("DailyNote", back_populates="entity", cascade="all, delete-orphan")


class Subject(db.Model):
    __tablename__ = "subjects"

    id: Mapped[int] = mapped_column(primary_key=True)
    entity_id: Mapped[int] = mapped_column(ForeignKey("entities.id", ondelete="CASCADE"), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False
    )

    entity = relationship("WorkshopEntity", back_populates="subjects")
    questions = relationship("Question", back_populates="subject")

    __table_args__ = (db.UniqueConstraint("entity_id", "name", name="uq_subject_entity_name"),)
