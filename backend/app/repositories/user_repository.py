from sqlalchemy import select

from app.extensions import db
from app.models import User
from app.repositories.base import BaseRepository


class UserRepository(BaseRepository[User]):
    model = User

    def get_by_email(self, email: str) -> User | None:
        return db.session.scalar(select(User).where(User.email == email))
