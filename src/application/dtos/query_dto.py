from dataclasses import dataclass

@dataclass
class UserCreateDTO:
    email: str
    password: str
    name: str

@dataclass
class LoginInputDTO:
    email:str
    password: str

@dataclass
class PitchCreateDTO:
    company_name: str
    search_target: str
