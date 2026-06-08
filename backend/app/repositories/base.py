from typing import Generic, TypeVar

from app.extensions import db

ModelT = TypeVar("ModelT")


class BaseRepository(Generic[ModelT]):
    model: type[ModelT]

    def get_by_id(self, record_id: int) -> ModelT | None:
        return db.session.get(self.model, record_id)

    def get_all(self) -> list[ModelT]:
        return db.session.scalars(db.select(self.model)).all()

    def add(self, instance: ModelT) -> ModelT:
        db.session.add(instance)
        return instance

    def delete(self, instance: ModelT) -> None:
        db.session.delete(instance)

    def commit(self) -> None:
        db.session.commit()

    def rollback(self) -> None:
        db.session.rollback()

    def flush(self) -> None:
        db.session.flush()
