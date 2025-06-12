from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import RedirectResponse
from .database import engine
from . import models
from app.routers import page
from app.routers.auth import auth_router
from app.routers.user import user_router
from .seed import seed
from fastapi.templating import Jinja2Templates
from fastapi.exception_handlers import http_exception_handler
from starlette.exceptions import HTTPException as StarletteHTTPException
from fastapi.staticfiles import StaticFiles

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

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