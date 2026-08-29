from fastapi import APIRouter, Depends
from src.infrastructure.web.middleware.idempotency_middleware import IdempotencyManager

from src.infrastructure.web.controllers.auth_controller import (
    AuthController,
    LoginResponseModel,
    RegisterResponseModel,
)
from src.infrastructure.web.controllers.Pitch_controller import (
    PitchController,
    PitchResponseModel,
)

from src.infrastructure.web.controllers.webhook_controller import (
    WebhookController,
    WebhookResponseModel,
)

# --- Auth router ---
auth_router = APIRouter(prefix="/auth", tags=["auth"])
auth_router.add_api_route("/login", AuthController.login, methods=["POST"], response_model=LoginResponseModel)
auth_router.add_api_route("/register", AuthController.register, methods=["POST"], response_model=RegisterResponseModel)

# --- Pitch router ---
pitch_router = APIRouter(prefix="/protected/pitch", tags=["pitch"])
pitch_router.add_api_route("/me", PitchController.get_pitch, methods=["GET"], response_model=PitchResponseModel, dependencies=[Depends(IdempotencyManager.verify_key)])





webhook_router = APIRouter(prefix="/protected/webhook", tags=["webhook"])
webhook_router.add_api_route("/submit", WebhookController.submit, methods=["POST"], response_model=WebhookResponseModel)

def register_routers(app):
    app.include_router(auth_router)
    app.include_router(pitch_router)
    app.include_router(webhook_router)  