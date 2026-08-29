from typing import Optional
from motor.motor_asyncio import AsyncIOMotorDatabase
from src.application.interfaces.repository import AbstractPitchRepository
from src.application.dtos.Response_dto import PitchResponseDTO
from src.domain.models import User

class MongoPitchRepository(AbstractPitchRepository):
    def __init__(self, db: AsyncIOMotorDatabase):
        self.collection = db["Pitches"]


async def get_pitch(self, pitch_creator: str) -> PitchResponseDTO:
        doc = await self.collection.find_Many({"creator": pitch_creator})
        if not doc:
            return None
            
        return PitchResponseDTO(
            Pitch_name=doc["name"],
            Pitch_email=doc["email"],
            Pitch_company_name=doc["company_name"],
            Pitch_profession=doc["Profession"],
            Pitch_pitch=doc["Pitch"]
        )