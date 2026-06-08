from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Index, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.extensions import db
from app.utils.datetime_utils import utc_now


class StudentRemark(db.Model):
    __tablename__ = "student_remarks"

    id: Mapped[int] = mapped_column(primary_key=True)
    student_id: Mapped[int] = mapped_column(
        ForeignKey("students.id", ondelete="CASCADE"), nullable=False
    )
    remark: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, nullable=False
    )

    student = relationship("Student", back_populates="remarks")

    __table_args__ = (Index("ix_student_remarks_student_created", "student_id", "created_at"),)
