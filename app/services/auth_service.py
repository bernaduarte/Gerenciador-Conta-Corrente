import jwt
from app.schemas.auth import LoginRequest, TokenResponse
from app.config import SECRET_KEY, ALGORITHM


class AuthService:
    def __init__(self, user_repository):
        self.user_repository = user_repository

    async def login(self, login_request: LoginRequest):
        if len(login_request.account_number) != 5 or len(login_request.password) != 4:
            raise Exception("Número da conta deve ter 5 dígitos e senha deve ter 4 dígitos")
        user = self.user_repository.find_by_account_number(login_request.account_number)
        if not user:
            raise Exception("Usuario não encontrado")
        if user.password != login_request.password:
            raise Exception("Senha incorreta")
        access_token = self.create_access_token(data={
            "sub": user.account_number,
            "user_type": user.user_type.value  
        })
        return TokenResponse(access_token=access_token).dict()
    
    def create_access_token(self, data: dict):
        return jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)