import os
import logging
import httpx
from dataclasses import asdict
from src.application.interfaces.repository import AbstractWebhookClient
from src.application.dtos.webhook_dto import WebhookInputDTO, WebhookOutputDTO
from src.application.exceptions import WebhookDeliveryError

logger = logging.getLogger(__name__)

MAKE_WEBHOOK_URL = os.environ["VITE_MAKE_WEBHOOK_URL"]  
TIMEOUT_SECONDS = 10.0


class MakeWebhookClient(AbstractWebhookClient):
    async def send(self, payload: WebhookInputDTO) -> WebhookOutputDTO:
        body = asdict(payload)

        try:
            async with httpx.AsyncClient(timeout=TIMEOUT_SECONDS) as client:
                response = await client.post(MAKE_WEBHOOK_URL, json=body)
        except httpx.TimeoutException:
            logger.error("Make.com webhook timed out for payload type=%s", payload.type)
            raise WebhookDeliveryError("Webhook delivery timed out")
        except httpx.RequestError as e:
            logger.error("Make.com webhook request failed: %s", e, exc_info=True)
            raise WebhookDeliveryError("Webhook delivery failed")

        if response.status_code >= 400:
            logger.error(
                "Make.com webhook returned error status=%d body=%s",
                response.status_code, response.text[:200],
            )
            raise WebhookDeliveryError(f"Webhook rejected with status {response.status_code}")

        return WebhookOutputDTO(success=True, make_status_code=response.status_code)