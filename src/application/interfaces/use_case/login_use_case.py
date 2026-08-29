# src/application/use_cases/login_user.py
from dataclasses import dataclass
from passlib.context import CryptContext
from src.application.dtos.query_dto import LoginInputDTO
from src.application.dtos.Response_dto import  LoginOutputDTO
from src.application.interfaces.repository import AbstractUserRepository
from src.application.exceptions import InvalidCredentialsError
import bcrypt
import jwt
from datetime import datetime, timedelta, timezone


@dataclass
class LoginUserUseCase:
    user_repository: AbstractUserRepository  
    secret_key: str

    async def execute(self, dto: LoginInputDTO) -> LoginOutputDTO:
        user = await self.user_repository.find_by_email(dto.email)
        pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        if not user or not pwd_context.verify(dto.password, user.password):
            raise InvalidCredentialsError("Invalid email or password")

        token = jwt.encode(
            {"sub": user.id, "exp": datetime.now(timezone.utc) + timedelta(hours=7)},
            self.secret_key,
            algorithm="HS256",
        )

        return LoginOutputDTO(id=user.id,email=user.email,token=token)