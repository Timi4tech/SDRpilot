from dataclasses import dataclass, field

@dataclass
class User:
    id: int
    email: str
    name: str
    password: str
    is_active: bool = field(default=True)


@dataclass
class Pitch:
    name: str
    email: str
    company_name: str
    Profession: str
    Pitch: str
