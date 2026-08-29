from typing import Optional
from motor.motor_asyncio import AsyncIOMotorDatabase 
from src.application.dtos.Response_dto import UserResponseDTO
from src.application.interfaces.repository import AbstractUserRepository
from src.domain.models import User

class MongoUserRepository(AbstractUserRepository):
    def __init__(self, db: AsyncIOMotorDatabase):
        self.collection = db["users"]
    async def create_user(self, user: User) -> None:
        # Map Clean Domain Model to Native BSON Document format
        document = {
            "_id": user.id,  # Storing our domain UUID string as the primary collection key
            "email": user.email,
            "name" : user.name,
            "password": user.password
        }
        await self.collection.replace_one({"_id": user.id}, document, upsert=True)

    async def find_by_email(self, email: str) -> Optional[UserResponseDTO]:
        doc = await self.collection.find_one({"email": email})
        if not doc:
            return None
            
        return UserResponseDTO(
            id=doc["_id"],
            email=doc["email"],
            password=doc["password"]
        )

