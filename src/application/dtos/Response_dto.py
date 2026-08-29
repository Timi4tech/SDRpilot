from dataclasses import dataclass

@dataclass
class UserResponseDTO:
    id: str
    email: str
    password: str

@dataclass
class PitchResponseDTO:
    Pitch_name: str
    Pitch_email: str
    Pitch_company_name: str
    Pitch_profession: str
    Pitch_pitch: str

@dataclass
class LoginOutputDTO:
    id:str
    email: str
    token: str
