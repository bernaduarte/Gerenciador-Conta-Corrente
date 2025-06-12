from fastapi import APIRouter,Depends
from app.database import get_db
from sqlalchemy.orm import Session
from app.controllers.auth_controller import AuthController
from app.services.auth_service import AuthService
from app.repositories.user_repository import UserRepository
from app.schemas.auth import LoginRequest

auth_router = APIRouter(prefix="/auth", tags=["auth"])

def get_user_repository(db: Session = Depends(get_db)):
    return UserRepository(db)

def get_auth_service(user_repo: UserRepository = Depends(get_user_repository)):
    return AuthService(user_repo)

def get_auth_controller(auth_service: AuthService = Depends(get_auth_service)):
    return AuthController(auth_service)

@auth_router.post('/login')
async def login(
    login_request: LoginRequest,
    controller: AuthController = Depends(get_auth_controller)
):
    return await controller.login(login_request)

@auth_router.post('/logout')
async def logout(
    controller: AuthController = Depends(get_auth_controller)
):
    return await controller.logout()