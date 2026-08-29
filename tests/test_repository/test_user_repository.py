from src.application.interfaces.repository import AbstractUserRepository
from src.domain.models import User
from typing import Optional


class FakeUserRepository(AbstractUserRepository):

    def __init__(self):
        self.users_by_email = {}
        self.users_by_id = {}

    async def create_user(self, user_data) -> any:
       
        user_id = "mock_id_123"
        self.users[user_id] = user_data
        return user_data

    async def find_by_email(self, email: str) -> Optional[User]:
        return self.users_by_email.get(email)

    async def find_by_id(self, user_id: str) -> Optional[User]:
        return self.users_by_id.get(user_id)

    async def save(self, user: User) -> User:
        user.id = user.id or f"fake-id-{len(self.users_by_id) + 1}"
        self.users_by_email[user.email] = user
        self.users_by_id[user.id] = user
        return user

    async def update(self, user_id: str, updates: dict) -> Optional[User]:
        user = self.users_by_id.get(user_id)
        if not user:
            return None
        for key, value in updates.items():
            setattr(user, key, value)
        return user

    async def delete(self, user_id: str) -> bool:
        user = self.users_by_id.pop(user_id, None)
        if not user:
            return False
        self.users_by_email.pop(user.email, None)
        return True

    async def list_all(self, limit: int = 50):
        return list(self.users_by_id.values())[:limit]


    def seed(self, user: User):
        self.users_by_email[user.email] = user
        self.users_by_id[user.id] = user