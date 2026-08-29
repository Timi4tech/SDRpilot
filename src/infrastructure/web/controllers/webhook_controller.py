from fastapi import HTTPException, Depends
from pydantic import BaseModel
from typing import Optional
from src.application.dtos.webhook_dto import WebhookInputDTO
from src.application.interfaces.use_case.submit_webhook_use_case import SubmitWebhookUseCase
from src.application.exceptions import WebhookDeliveryError
from src.infrastructure.web.dependencies import get_submit_webhook_use_case


class WebhookRequestModel(BaseModel):
    type: str
    name: str
    email: str
    company_name: Optional[str] = None
    message: Optional[str] = None


class WebhookResponseModel(BaseModel):
    success: bool


class WebhookController:
    @staticmethod
    async def submit(
        payload: WebhookRequestModel,
        use_case: SubmitWebhookUseCase = Depends(get_submit_webhook_use_case),
    ) -> WebhookResponseModel:
        dto = WebhookInputDTO(
            type=payload.type,
            name=payload.name,
            email=payload.email,
            company_name=payload.company_name,
            message=payload.message,
        )

        try:
            result = await use_case.execute(dto)
        except WebhookDeliveryError as e:
            raise HTTPException(status_code=502, detail=str(e))

        return WebhookResponseModel(success=result.success)