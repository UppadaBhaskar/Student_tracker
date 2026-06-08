import bcrypt
from flask_jwt_extended import create_access_token

from app.exceptions import UnauthorizedException
from app.models.enums import UserRole
from app.models.user import User
from app.repositories.user_repository import UserRepository


class AuthService:
    def __init__(self):
        self.user_repo = UserRepository()

    @staticmethod
    def hash_password(password: str) -> str:
        return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

    @staticmethod
    def verify_password(password: str, password_hash: str) -> bool:
        return bcrypt.checkpw(password.encode("utf-8"), password_hash.encode("utf-8"))

    def login(self, email: str, password: str) -> dict:
        user = self.user_repo.get_by_email(email.lower().strip())
        if not user or not self.verify_password(password, user.password_hash):
            raise UnauthorizedException("Invalid email or password")

        token = create_access_token(
            identity=str(user.id),
            additional_claims={"role": user.role.value, "user_id": user.id},
        )
        return {"access_token": token, "user": self._user_payload(user)}

    def get_me(self, user_id: int) -> dict:
        user = self.user_repo.get_by_id(user_id)
        if not user:
            raise UnauthorizedException("User not found")
        return self._user_payload(user)

    def _user_payload(self, user: User) -> dict:
        payload = {
            "id": user.id,
            "email": user.email,
            "role": user.role.value,
        }
        if user.role == UserRole.STUDENT and user.student:
            payload["student_id"] = user.student.id
            payload["entity_id"] = user.student.entity_id
            payload["full_name"] = user.student.full_name
        return payload

    def create_user(self, email: str, password: str, role: UserRole) -> User:
        user = User(
            email=email.lower().strip(),
            password_hash=self.hash_password(password),
            role=role,
        )
        self.user_repo.add(user)
        return user
