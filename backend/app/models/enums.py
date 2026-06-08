import enum


class UserRole(str, enum.Enum):
    TRAINER = "trainer"
    STUDENT = "student"


class EntityType(str, enum.Enum):
    WORKSHOP = "workshop"
    BOOTCAMP = "bootcamp"
    TRAINING_PROGRAM = "training_program"


class AttendanceStatus(str, enum.Enum):
    PRESENT = "present"
    ABSENT = "absent"


class AssignmentStatus(str, enum.Enum):
    COMPLETED = "completed"
    NOT_COMPLETED = "not_completed"


class QuestionDifficulty(str, enum.Enum):
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"


class QuestionStatus(str, enum.Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    ARCHIVED = "archived"


class AttemptStatus(str, enum.Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
