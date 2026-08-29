from dataclasses import dataclass
from typing import Optional


@dataclass
class WebhookInputDTO:
    type: str            
    name: str
    email: str
    company_name: Optional[str] = None
    message: Optional[str] = None



@dataclass
class WebhookOutputDTO:
    success: bool
    make_status_code: int