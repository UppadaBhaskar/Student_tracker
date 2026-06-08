from sqlalchemy import func, select

from app.extensions import db
from app.models import Question, QuestionAttempt
from app.models.enums import AttemptStatus, QuestionStatus
from app.repositories.base import BaseRepository


class QuestionRepository(BaseRepository[Question]):
    model = Question

    def list_by_entity(self, entity_id: int) -> list[Question]:
        return db.session.scalars(
            select(Question)
            .where(Question.entity_id == entity_id)
            .order_by(Question.question_number)
        ).all()

    def get_active(self) -> Question | None:
        return db.session.scalar(select(Question).where(Question.status == QuestionStatus.ACTIVE))

    def archive_all_active(self) -> None:
        active = db.session.scalars(select(Question).where(Question.status == QuestionStatus.ACTIVE))
        for q in active:
            q.status = QuestionStatus.ARCHIVED


class QuestionAttemptRepository(BaseRepository[QuestionAttempt]):
    model = QuestionAttempt

    def list_by_question(
        self, question_id: int, status: AttemptStatus | None = None
    ) -> list[QuestionAttempt]:
        stmt = select(QuestionAttempt).where(QuestionAttempt.question_id == question_id)
        if status:
            stmt = stmt.where(QuestionAttempt.status == status)
        return db.session.scalars(stmt.order_by(QuestionAttempt.clicked_at, QuestionAttempt.id)).all()

    def count_earlier_clicks(self, question_id: int, clicked_at, attempt_id: int | None = None) -> int:
        stmt = select(func.count()).select_from(QuestionAttempt).where(
            QuestionAttempt.question_id == question_id,
            QuestionAttempt.clicked_at < clicked_at,
        )
        return db.session.scalar(stmt) or 0

    def get_approved_for_student_question(
        self, student_id: int, question_id: int
    ) -> QuestionAttempt | None:
        return db.session.scalar(
            select(QuestionAttempt).where(
                QuestionAttempt.student_id == student_id,
                QuestionAttempt.question_id == question_id,
                QuestionAttempt.status == AttemptStatus.APPROVED,
            )
        )

    def list_by_student(self, student_id: int) -> list[QuestionAttempt]:
        return db.session.scalars(
            select(QuestionAttempt).where(QuestionAttempt.student_id == student_id)
        ).all()

    def count_pending(self) -> int:
        return (
            db.session.scalar(
                select(func.count())
                .select_from(QuestionAttempt)
                .where(QuestionAttempt.status == AttemptStatus.PENDING)
            )
            or 0
        )

    def list_approved_by_entity(self, entity_id: int, subject_id: int | None = None) -> list[QuestionAttempt]:
        stmt = (
            select(QuestionAttempt)
            .join(Question, QuestionAttempt.question_id == Question.id)
            .where(Question.entity_id == entity_id, QuestionAttempt.status == AttemptStatus.APPROVED)
        )
        if subject_id:
            stmt = stmt.where(Question.subject_id == subject_id)
        return db.session.scalars(stmt).all()

    def list_by_question_ids(self, question_ids: list[int]) -> list[QuestionAttempt]:
        if not question_ids:
            return []
        return db.session.scalars(
            select(QuestionAttempt).where(QuestionAttempt.question_id.in_(question_ids))
        ).all()
