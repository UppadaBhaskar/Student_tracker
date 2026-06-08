from app.exceptions import ConflictException, NotFoundException, ValidationException
from app.models.enums import QuestionDifficulty, QuestionStatus
from app.models.question import Question
from app.repositories.entity_repository import SubjectRepository
from app.repositories.question_repository import QuestionRepository
from app.services.entity_service import EntityService
from app.utils.datetime_utils import utc_now
from app.utils.points import difficulty_default_points


class QuestionService:
    def __init__(self):
        self.question_repo = QuestionRepository()
        self.subject_repo = SubjectRepository()
        self.entity_service = EntityService()

    def list_questions(self, entity_id: int) -> list[Question]:
        self.entity_service.get_entity(entity_id)
        return self.question_repo.list_by_entity(entity_id)

    def get_question(self, question_id: int) -> Question:
        question = self.question_repo.get_by_id(question_id)
        if not question:
            raise NotFoundException("Question not found")
        return question

    def create_question(self, entity_id: int, data: dict) -> Question:
        self.entity_service.get_entity(entity_id)
        subject = self.subject_repo.get_by_id(data["subject_id"])
        if not subject or subject.entity_id != entity_id:
            raise NotFoundException("Subject not found in entity")

        difficulty = QuestionDifficulty(data.get("difficulty", "medium"))
        max_points = data.get("max_points") or difficulty_default_points(difficulty.value)

        question = Question(
            entity_id=entity_id,
            question_number=data["question_number"],
            subject_id=data["subject_id"],
            title=data["title"],
            description=data.get("description"),
            day=data["day"],
            timer_minutes=data["timer_minutes"],
            difficulty=difficulty,
            max_points=max_points,
            status=QuestionStatus.DRAFT,
        )
        self.question_repo.add(question)
        try:
            self.question_repo.commit()
        except Exception as exc:
            self.question_repo.rollback()
            raise ConflictException("Question number already exists for entity") from exc
        return question

    def update_question(self, question_id: int, data: dict) -> Question:
        question = self.get_question(question_id)
        if question.status == QuestionStatus.ACTIVE:
            raise ValidationException("Cannot edit active question")

        if "subject_id" in data:
            subject = self.subject_repo.get_by_id(data["subject_id"])
            if not subject or subject.entity_id != question.entity_id:
                raise NotFoundException("Subject not found in entity")
            question.subject_id = data["subject_id"]
        if "question_number" in data:
            question.question_number = data["question_number"]
        if "title" in data:
            question.title = data["title"]
        if "description" in data:
            question.description = data["description"]
        if "day" in data:
            question.day = data["day"]
        if "timer_minutes" in data:
            question.timer_minutes = data["timer_minutes"]
        if "difficulty" in data:
            question.difficulty = QuestionDifficulty(data["difficulty"])
            if "max_points" not in data:
                question.max_points = difficulty_default_points(data["difficulty"])
        if "max_points" in data:
            question.max_points = data["max_points"]

        self.question_repo.commit()
        return question

    def delete_question(self, question_id: int) -> None:
        question = self.get_question(question_id)
        if question.status == QuestionStatus.ACTIVE:
            raise ValidationException("Cannot delete active question")
        self.question_repo.delete(question)
        self.question_repo.commit()

    def reveal_question(self, question_id: int) -> Question:
        question = self.get_question(question_id)
        self.question_repo.archive_all_active()
        question.status = QuestionStatus.ACTIVE
        question.revealed_at = utc_now()
        self.question_repo.commit()
        return question

    def archive_question(self, question_id: int) -> Question:
        question = self.get_question(question_id)
        question.status = QuestionStatus.ARCHIVED
        self.question_repo.commit()
        return question

    def get_active_question(self) -> Question | None:
        return self.question_repo.get_active()
