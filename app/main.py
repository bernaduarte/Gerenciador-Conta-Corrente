import asyncio
from contextlib import asynccontextmanager
from sqlalchemy.orm import Session
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.exception_handlers import http_exception_handler
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.database import engine, get_db
from app import models
from app.models.user import UserRole, User  # UserRole em vez de UserType
from app.repositories.user_repository import UserRepository
from app.routers import page
from app.routers.auth import auth_router
from app.routers.user import user_router
from app.seed import seed

models.Base.metadata.create_all(bind=engine)

background_task_running = False

async def negative_balance_fee_task():
    global background_task_running
    background_task_running = True
    while background_task_running:
        db: Session = next(get_db())
        try:
            vip_users = db.query(User).filter(User.user_type == UserRole.VIP).all()
            user_repo = UserRepository(db)
            for user in vip_users:
                if user.account.balance < 0:
                    user_repo.apply_negative_balance_fee(user.id)
                    print(f"Débito de 0.1% aplicado a VIP {user.account_number}. Novo saldo: {user.account.balance}")
        except Exception as e:
            print(f"Erro na tarefa de débito de saldo negativo: {e}")
        finally:
            db.close()
        await asyncio.sleep(60)

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Iniciando tarefa de débito de saldo negativo...")
    task = asyncio.create_task(negative_balance_fee_task())
    yield
    print("Parando tarefa de débito de saldo negativo...")
    global background_task_running
    background_task_running = False
    task.cancel()
    try:
        await task
    except asyncio.CancelledError:
        pass

app = FastAPI(lifespan=lifespan)

app.mount("/static", StaticFiles(directory="app/static"), name="static")

templates = Jinja2Templates(directory="app/templates")

app.include_router(page.router)
app.include_router(auth_router)
app.include_router(user_router)

seed()

@app.exception_handler(HTTPException)
async def auth_exception_handler(request: Request, exc: HTTPException):
    if exc.status_code == 401:
        return RedirectResponse(url="/")
    return await http_exception_handler(request, exc)

@app.exception_handler(StarletteHTTPException)
async def custom_http_exception_handler(request: Request, exc: StarletteHTTPException):
    if exc.status_code == 404:
        return templates.TemplateResponse("not_found.html", {"request": request}, status_code=404)
    return await http_exception_handler(request, exc)
