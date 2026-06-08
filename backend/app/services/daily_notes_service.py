from app.models.daily_notes import DailyNote
from app.repositories.tracking_repository import DailyNoteRepository
from app.services.entity_service import EntityService


class DailyNotesService:
    def __init__(self):
        self.note_repo = DailyNoteRepository()
        self.entity_service = EntityService()

    def get_notes(self, entity_id: int, day: int | None = None) -> list[DailyNote]:
        self.entity_service.get_entity(entity_id)
        if day is not None:
            note = self.note_repo.get_by_entity_day(entity_id, day)
            return [note] if note else []
        return self.note_repo.list_by_entity(entity_id)

    def upsert_note(self, entity_id: int, day: int, notes: str) -> DailyNote:
        self.entity_service.get_entity(entity_id)
        note = self.note_repo.get_by_entity_day(entity_id, day)
        if note:
            note.notes = notes.strip()
        else:
            note = DailyNote(entity_id=entity_id, day=day, notes=notes.strip())
            self.note_repo.add(note)
        self.note_repo.commit()
        return note
