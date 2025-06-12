from fastapi import APIRouter,Depends,Request
from app.utils.auth_middleware import require_auth
from app.database import get_db
from sqlalchemy.orm import Session
from app.controllers.user_controller import UserController
from app.services.user_service import UserService
from app.repositories.user_repository import UserRepository
from pydantic import BaseModel

class TransactionRequest(BaseModel):
    amount: float
    type: str
    target_account_number: str = None

user_router = APIRouter(prefix="/user", tags=["user"])

def get_user_repository(db: Session = Depends(get_db)):
    return UserRepository(db)

def get_auth_service(user_repo: UserRepository = Depends(get_user_repository)):
    return UserService(user_repo)

def get_auth_controller(auth_service: UserService = Depends(get_auth_service)):
    return UserController(auth_service)

@user_router.get('/information')
async def get_information(
    request: Request,
    _=Depends(require_auth),
    controller: UserController = Depends(get_auth_controller)
):
    return await controller.get_information(request)


@user_router.post('/deposit')
async def deposit(
    deposit_data: TransactionRequest,
    request: Request,
    _=Depends(require_auth),
    controller: UserController = Depends(get_auth_controller)
):
    return await controller.change_balance_on_account_number(
        request, 
        deposit_data.amount,
        deposit_data.type,
    )

@user_router.post('/withdrawal')
async def deposit(
    deposit_data: TransactionRequest,
    request: Request,
    _=Depends(require_auth),
    controller: UserController = Depends(get_auth_controller)
):
    return await controller.change_balance_on_account_number(
        request, 
        deposit_data.amount,
        deposit_data.type,
    )

@user_router.post('/transfer')
async def deposit(
    deposit_data: TransactionRequest,
    request: Request,
    _=Depends(require_auth),
    controller: UserController = Depends(get_auth_controller)
):
    return await controller.change_balance_on_account_number(
        request, 
        deposit_data.amount,
        deposit_data.type,
        deposit_data.target_account_number
    )

@user_router.post('/manager_visit')
async def manager_visit(
     request: Request,
    _=Depends(require_auth),
    controller: UserController = Depends(get_auth_controller)
):
    return await controller.manager_visit(request)