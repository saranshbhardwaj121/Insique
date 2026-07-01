from datetime import datetime, timedelta, timezone
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from backend.app.models.user import User
from backend.app.repositories.base import BaseRepository


class UserRepository(BaseRepository[User]):
    def __init__(self, session: Session) -> None:
        super().__init__(session, User)

    def get_by_id(self, user_id: UUID | str) -> User | None:
        return self.session.get(User, user_id)

    def get_by_username(self, username: str) -> User | None:
        statement = select(User).where(func.lower(User.username) == func.lower(username))
        return self.session.scalar(statement)

    def get_by_email(self, email: str) -> User | None:
        statement = select(User).where(func.lower(User.email) == func.lower(email))
        return self.session.scalar(statement)

    def delete_by_id(self, user_id: UUID) -> bool:
        user = self.session.get(User, user_id)
        if user is None:
            return False
        self.session.delete(user)
        return True

    def increment_failed_attempts(self, user_id: UUID, max_attempts: int = 10, lockout_minutes: int = 15) -> None:
        user = self.session.get(User, user_id)
        if user is None:
            return
        user.failed_login_attempts = (user.failed_login_attempts or 0) + 1
        if user.failed_login_attempts >= max_attempts:
            user.locked_until = datetime.now(timezone.utc) + timedelta(minutes=lockout_minutes)

    def reset_failed_attempts(self, user_id: UUID) -> None:
        user = self.session.get(User, user_id)
        if user is None:
            return
        user.failed_login_attempts = 0
        user.locked_until = None
