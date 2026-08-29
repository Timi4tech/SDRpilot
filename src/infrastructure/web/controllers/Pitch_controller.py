from fastapi import HTTPException, Depends
from pydantic import BaseModel
from src.application.dtos.Response_dto import PitchResponseDTO
from src.application.interfaces.use_case.Pitch_use_case import GetUserPitchUseCase
from src.application.exceptions import PitchNotFoundError, InvalidCredentialsError
from src.infrastructure.web.dependencies import get_pitch_use_case 
from src.infrastructure.web.middleware.cache_middleware import cache_response

class PitchCreateModel(BaseModel):
    company_name:str
    search_target: str

class PitchResponseModel(BaseModel):
    Pitch_name: str
    Pitch_email: str
    Pitch_company_name: str
    Pitch_profession: str
    Pitch_pitch: str

class PitchController:
    @staticmethod
    @cache_response(expire_seconds = 3600)
    async def get_pitch(
        use_case: GetUserPitchUseCase = Depends(get_pitch_use_case),
    ) -> PitchResponseDTO:
        
        try:
            result = await use_case.execute()
        except PitchNotFoundError as e:
            raise HTTPException(status_code=404, detail=str(e))

        return result

    #@staticmethod
    #async def create_pitch(
     #      use_case: GetUserPitchUseCase = Depends(create_pitch_use_case),
    #) -> PitchResponseDTO:
        
    #    try:
    #        result = await use_case.execute()
    #    except InvalidCredentialsError as e:
    #        raise HTTPException(status_code=401, detail=str(e))

    #    return result