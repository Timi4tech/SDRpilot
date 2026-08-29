from dataclasses import dataclass
from src.application.interfaces.repository import AbstractWebhookClient
from src.application.dtos.webhook_dto import WebhookInputDTO, WebhookOutputDTO


@dataclass
class SubmitWebhookUseCase:
    webhook_client: AbstractWebhookClient 

    async def execute(self, dto: WebhookInputDTO) -> WebhookOutputDTO:
        return await self.webhook_client.send(dto)