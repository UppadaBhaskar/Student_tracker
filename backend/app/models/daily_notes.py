from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Index, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.extensions import db
from app.utils.datetime_utils import utc_now


class DailyNote(db.Model):
    __tablename__ = "daily_notes"

    id: Mapped[int] = mapped_column(primary_key=True)
    entity_id: Mapped[int] = mapped_column(
        ForeignKey("entities.id", ondelete="CASCADE"), nullable=False
    )
    day: Mapped[int] = mapped_column(Integer, nullable=False)
    notes: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False
    )

    entity = relationship("WorkshopEntity", back_populates="daily_notes")

    __table_args__ = (
        db.UniqueConstraint("entity_id", "day", name="uq_daily_note_entity_day"),
        Index("ix_daily_notes_entity_day", "entity_id", "day"),
    )
