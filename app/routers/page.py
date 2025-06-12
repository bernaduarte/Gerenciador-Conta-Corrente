from fastapi import APIRouter, Request,Depends
from app.utils.auth_middleware import require_auth
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
import jwt
from fastapi.responses import RedirectResponse
from app.config import SECRET_KEY, ALGORITHM

templates = Jinja2Templates(directory="app/templates")
router = APIRouter()

@router.get("/", response_class=HTMLResponse)
async def login_page(request: Request):
    token = request.cookies.get("access_token")
    if token:
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            return RedirectResponse(url="/dashboard")
        except jwt.ExpiredSignatureError:
            pass 
        except jwt.InvalidTokenError:
            pass 
    return templates.TemplateResponse("login.html", {"request": request})


@router.get("/dashboard", response_class=HTMLResponse)
async def dashboard_page(request: Request, _=Depends(require_auth)):
    return templates.TemplateResponse("dashboard.html", {"request": request})