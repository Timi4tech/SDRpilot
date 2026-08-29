# src/application/interfaces/repository.py
from abc import ABC, abstractmethod
from typing import Optional
from src.domain.models import User 
from src.domain.models import Pitch
from src.application.dtos.webhook_dto import WebhookInputDTO, WebhookOutputDTO

class AbstractUserRepository(ABC):
    @abstractmethod
    def find_by_email(self, email: str) -> Optional[User]:
        pass

    @abstractmethod
    def create_user(self, user: User) -> User:
        pass

class AbstractPitchRepository(ABC):
    @abstractmethod
    def find_by_pitch(self, creator: str) -> Optional[User]:
        pass

    @abstractmethod
    def create_pitch(self, pitch: Pitch) -> Pitch:
        pass


class AbstractWebhookClient(ABC):
    @abstractmethod
    async def send(self, payload: WebhookInputDTO) -> WebhookOutputDTO:
        ...