from sqlalchemy import select

from app.extensions import db
from app.models import Subject, WorkshopEntity
from app.repositories.base import BaseRepository


class EntityRepository(BaseRepository[WorkshopEntity]):
    model = WorkshopEntity

    def list_all(self) -> list[WorkshopEntity]:
        return db.session.scalars(select(WorkshopEntity).order_by(WorkshopEntity.id)).all()


class SubjectRepository(BaseRepository[Subject]):
    model = Subject

    def list_by_entity(self, entity_id: int) -> list[Subject]:
        return db.session.scalars(
            select(Subject).where(Subject.entity_id == entity_id).order_by(Subject.name)
        ).all()

    def get_by_entity_and_name(self, entity_id: int, name: str) -> Subject | None:
        return db.session.scalar(
            select(Subject).where(Subject.entity_id == entity_id, Subject.name == name)
        )
