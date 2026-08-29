from fastapi import HTTPException, Depends, Response
from pydantic import BaseModel
from src.application.dtos.query_dto import LoginInputDTO, UserCreateDTO
from src.application.interfaces.use_case.login_use_case import LoginUserUseCase
from src.application.interfaces.use_case.register_use_case import RegisterUserUseCase
from src.application.exceptions import InvalidCredentialsError, UserAlreadyExistsError
from src.infrastructure.web.dependencies import get_login_use_case, get_register_use_case



class LoginRequestModel(BaseModel):
    email: str
    password: str


class LoginResponseModel(BaseModel):
    id: str
    email: str

class RegisterRequestModel(BaseModel):
    email: str
    password: str
    name: str


class RegisterResponseModel(BaseModel):
    id: str
    email: str

class AuthController:
    @staticmethod
    async def login(
        response:Response,
        payload: LoginRequestModel,
        use_case: LoginUserUseCase = Depends(get_login_use_case),
    ) -> LoginResponseModel:
        dto = LoginInputDTO(email=payload.email, password=payload.password)

        try:
            result = await use_case.execute(dto)
        except InvalidCredentialsError as e:
            raise HTTPException(status_code=401, detail=str(e))

        response.headers["Authorization"] = f"Bearer {result.token}"
        return LoginResponseModel(id=result.id,email=result.email)

    @staticmethod
    async def register(
        payload: RegisterRequestModel,
        use_case: RegisterUserUseCase = Depends(get_register_use_case),
    ) -> RegisterResponseModel:
        dto = UserCreateDTO(
            email=payload.email,
            password=payload.password,
            name=payload.name,
        )

        try:
            result = await use_case.execute(dto)
        except UserAlreadyExistsError as e:
            raise HTTPException(status_code=409, detail=str(e))
        response.headers["Authorization"] = f"Bearer {result.token}"
        return RegisterResponseModel(id=result.id, email=result.email)