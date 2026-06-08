from app.exceptions import ConflictException, NotFoundException
from app.models.enums import UserRole
from app.models.student import Student
from app.repositories.entity_repository import EntityRepository
from app.repositories.student_repository import StudentRemarkRepository, StudentRepository
from app.repositories.user_repository import UserRepository
from app.services.auth_service import AuthService
from app.services.entity_service import EntityService


class StudentService:
    def __init__(self):
        self.student_repo = StudentRepository()
        self.user_repo = UserRepository()
        self.remark_repo = StudentRemarkRepository()
        self.entity_repo = EntityRepository()
        self.auth_service = AuthService()
        self.entity_service = EntityService()

    def list_students(self, entity_id: int) -> list[Student]:
        self.entity_service.get_entity(entity_id)
        return self.student_repo.list_by_entity(entity_id)

    def get_student(self, student_id: int) -> Student:
        student = self.student_repo.get_by_id(student_id)
        if not student:
            raise NotFoundException("Student not found")
        return student

    def get_student_profile(self, student_id: int) -> dict:
        student = self.get_student(student_id)
        remarks = self.remark_repo.list_by_student(student_id)
        return {
            "student": student,
            "remarks": remarks,
        }

    def create_student(self, entity_id: int, data: dict) -> Student:
        self.entity_service.get_entity(entity_id)
        if self.student_repo.get_by_usn(data["usn"]):
            raise ConflictException("USN already exists")
        if self.user_repo.get_by_email(data["email"]):
            raise ConflictException("Email already exists")

        user = self.auth_service.create_user(data["email"], data["password"], UserRole.STUDENT)
        self.user_repo.flush()

        student = Student(
            user_id=user.id,
            entity_id=entity_id,
            usn=data["usn"].strip(),
            full_name=data["full_name"].strip(),
            college=data.get("college"),
            branch=data.get("branch"),
        )
        self.student_repo.add(student)
        self.student_repo.commit()
        return student

    def update_student(self, student_id: int, data: dict) -> Student:
        student = self.get_student(student_id)
        if "usn" in data and data["usn"] != student.usn:
            if self.student_repo.get_by_usn(data["usn"]):
                raise ConflictException("USN already exists")
            student.usn = data["usn"].strip()
        if "full_name" in data:
            student.full_name = data["full_name"].strip()
        if "college" in data:
            student.college = data["college"]
        if "branch" in data:
            student.branch = data["branch"]
        if "email" in data and data["email"] != student.user.email:
            if self.user_repo.get_by_email(data["email"]):
                raise ConflictException("Email already exists")
            student.user.email = data["email"].lower().strip()
        if "password" in data:
            student.user.password_hash = AuthService.hash_password(data["password"])
        self.student_repo.commit()
        return student

    def delete_student(self, student_id: int) -> None:
        student = self.get_student(student_id)
        user = student.user
        self.student_repo.delete(student)
        if user:
            self.user_repo.delete(user)
        self.student_repo.commit()

    def get_by_user_id(self, user_id: int) -> Student:
        student = self.student_repo.get_by_user_id(user_id)
        if not student:
            raise NotFoundException("Student profile not found")
        return student
