from app.models.tracking import TestScore
from app.repositories.tracking_repository import TestScoreRepository
from app.services.tracking_service import TrackingService


class TestScoreService:
    def __init__(self):
        self.test_repo = TestScoreRepository()
        self.tracking_service = TrackingService()

    def list_scores(self, entity_id: int) -> list[TestScore]:
        self.tracking_service.entity_service.get_entity(entity_id)
        return self.test_repo.list_by_entity(entity_id)

    def upsert_scores(self, entity_id: int, records: list[dict]) -> list[TestScore]:
        result = []
        for item in records:
            self.tracking_service._ensure_student_in_entity(entity_id, item["student_id"])
            self.tracking_service._validate_day(entity_id, item["day"])
            record = self.test_repo.get_record(
                entity_id, item["student_id"], item["subject_id"], item["day"]
            )
            if record:
                record.score = item["score"]
            else:
                record = TestScore(
                    entity_id=entity_id,
                    student_id=item["student_id"],
                    subject_id=item["subject_id"],
                    day=item["day"],
                    score=item["score"],
                )
                self.test_repo.add(record)
            result.append(record)
        self.test_repo.commit()
        return result
