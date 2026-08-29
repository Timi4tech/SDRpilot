# src/infrastructure/web/dependencies.py
import os

from fastapi import Depends, Request, HTTPException, status
from motor.motor_asyncio import AsyncIOMotorDatabase
from src.application.interfaces.use_case.login_use_case import LoginUserUseCase
from src.application.interfaces.use_case.register_use_case import RegisterUserUseCase
from src.application.interfaces.use_case.Pitch_use_case import GetUserPitchUseCase
from src.infrastructure.database.pitch_repository import MongoPitchRepository
from src.infrastructure.database.user_repository import MongoUserRepository
from src.infrastructure.database.mongo_client import get_db
from src.application.interfaces.use_case.submit_webhook_use_case import SubmitWebhookUseCase
from src.infrastructure.web.webhooks.make_webhook import MakeWebhookClient

SECRET_KEY = os.getenv("JWT_SECRET_KEY")


def get_current_user_id(request: Request) -> str:
    """Reads the user_id set by AuthMiddleware earlier in the request lifecycle."""
    user_id = getattr(request.state, "current_user", None)

    if not user_id:
        
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
        )

    return user_id

def get_login_use_case(db: AsyncIOMotorDatabase = Depends(get_db)) -> LoginUserUseCase:
    repository = MongoUserRepository(db)
    return LoginUserUseCase(user_repository=repository, secret_key=SECRET_KEY)
    
def get_pitch_use_case(db: AsyncIOMotorDatabase = Depends(get_db),pitch_creator:str=Depends(get_current_user_id)) -> MongoPitchRepository:
    repository = MongoPitchRepository(db)

    return GetUserPitchUseCase(pitch_repository=repository, pitch_creator=pitch_creator)

def get_register_use_case(db: AsyncIOMotorDatabase = Depends(get_db)) -> RegisterUserUseCase:
    repository = MongoUserRepository(db)
    return RegisterUserUseCase(repo=repository, secret_key=SECRET_KEY)


def get_submit_webhook_use_case() -> SubmitWebhookUseCase:
    client = MakeWebhookClient()
    return SubmitWebhookUseCase(webhook_client=client)

