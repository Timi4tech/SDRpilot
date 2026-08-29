# src/application/use_cases/login_user.py
from dataclasses import dataclass
from src.application.dtos.Response_dto import PitchResponseDTO
from src.application.interfaces.repository import AbstractPitchRepository
from src.application.exceptions import InvalidCredentialsError
import bcrypt
import jwt


@dataclass
class GetUserPitchUseCase:
    pitch_repository: AbstractPitchRepository 
    pitch_creator: str

    async def execute(self) -> PitchResponseDTO:
        pitch = await self.pitch_repository.find_by_pitch(self.pitch_creator)

        if not pitch:
            raise InvalidCredentialsError("Pitch not found")

        return PitchResponseDTO(
            Pitch_name=pitch.name,
            Pitch_email=pitch.email,
            Pitch_company_name=pitch.company_name,
            Pitch_profession=pitch.profession,
            Pitch_pitch=pitch.pitch
        )

@dataclass
class CreatePitchUseCase:
    pitch_repository: AbstractPitchRepository 
    pitch_creator: str

    async def execute(self) -> PitchResponseDTO:
        pitch = await self.pitch_repository.create_pitch(self.pitch_creator)

        if not pitch:
            raise InvalidCredentialsError("Pitch not found")

        return PitchResponseDTO(
            Pitch_name=pitch.name,
            Pitch_email=pitch.email,
            Pitch_company_name=pitch.company_name,
            Pitch_profession=pitch.profession,
            Pitch_pitch=pitch.pitch
        )
