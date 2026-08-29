import uuid
import jwt
from passlib.context import CryptContext
from dataclasses import dataclass
from src.application.dtos.query_dto import UserCreateDTO
from src.application.dtos.Response_dto import UserResponseDTO
from src.application.interfaces.repository import AbstractUserRepository
from src.domain.models import User
from datetime import datetime, timedelta, timezone

@dataclass
class RegisterUserUseCase:
    repo: AbstractUserRepository
    secret_key: str
    async def execute(self, dto: UserCreateDTO):
        existing_user = await self.repo.find_by_email(dto.email)
        if existing_user:
            raise ValueError("Email boundary conflict: User already registered")
        pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        hashed_password = pwd_context.hash(dto.password)
        new_user = User(
            id=str(uuid.uuid4()),
            name = dto.name,
            email=dto.email,
            password=hashed_password
        )

       
        token = jwt.encode(
            {"sub": new_user.id, "exp": datetime.now(timezone.utc) + timedelta(hours=1)},
            self.secret_key,
            algorithm="HS256",
        )

        await self.repo.create_user(new_user)
        
        return{
               "id": str(new_user.id),
                "email": new_user.email,
                "token": token
        } 