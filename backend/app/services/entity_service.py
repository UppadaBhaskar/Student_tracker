from app.exceptions import ConflictException, NotFoundException, ValidationException
from app.models.entity import Subject, WorkshopEntity
from app.models.enums import EntityType
from app.repositories.entity_repository import EntityRepository, SubjectRepository


class EntityService:
    def __init__(self):
        self.entity_repo = EntityRepository()
        self.subject_repo = SubjectRepository()

    def list_entities(self) -> list[WorkshopEntity]:
        return self.entity_repo.list_all()

    def get_entity(self, entity_id: int) -> WorkshopEntity:
        entity = self.entity_repo.get_by_id(entity_id)
        if not entity:
            raise NotFoundException("Entity not found")
        return entity

    def create_entity(self, data: dict) -> WorkshopEntity:
        if data["end_date"] < data["start_date"]:
            raise ValidationException("end_date must be on or after start_date")
        entity = WorkshopEntity(
            name=data["name"],
            entity_type=EntityType(data["entity_type"]),
            total_days=data["total_days"],
            start_date=data["start_date"],
            end_date=data["end_date"],
        )
        self.entity_repo.add(entity)
        self.entity_repo.commit()
        return entity

    def update_entity(self, entity_id: int, data: dict) -> WorkshopEntity:
        entity = self.get_entity(entity_id)
        if "name" in data:
            entity.name = data["name"]
        if "entity_type" in data:
            entity.entity_type = EntityType(data["entity_type"])
        if "total_days" in data:
            entity.total_days = data["total_days"]
        if "start_date" in data:
            entity.start_date = data["start_date"]
        if "end_date" in data:
            entity.end_date = data["end_date"]
        if entity.end_date < entity.start_date:
            raise ValidationException("end_date must be on or after start_date")
        self.entity_repo.commit()
        return entity

    def delete_entity(self, entity_id: int) -> None:
        entity = self.get_entity(entity_id)
        self.entity_repo.delete(entity)
        self.entity_repo.commit()

    def list_subjects(self, entity_id: int) -> list[Subject]:
        self.get_entity(entity_id)
        return self.subject_repo.list_by_entity(entity_id)

    def create_subject(self, entity_id: int, name: str) -> Subject:
        self.get_entity(entity_id)
        existing = self.subject_repo.get_by_entity_and_name(entity_id, name)
        if existing:
            raise ConflictException("Subject already exists for this entity")
        subject = Subject(entity_id=entity_id, name=name.strip())
        self.subject_repo.add(subject)
        self.subject_repo.commit()
        return subject

    def update_subject(self, subject_id: int, name: str) -> Subject:
        subject = self.subject_repo.get_by_id(subject_id)
        if not subject:
            raise NotFoundException("Subject not found")
        existing = self.subject_repo.get_by_entity_and_name(subject.entity_id, name)
        if existing and existing.id != subject_id:
            raise ConflictException("Subject name already in use")
        subject.name = name.strip()
        self.subject_repo.commit()
        return subject

    def delete_subject(self, subject_id: int) -> None:
        subject = self.subject_repo.get_by_id(subject_id)
        if not subject:
            raise NotFoundException("Subject not found")
        self.subject_repo.delete(subject)
        self.subject_repo.commit()
