from app.schemas.auth import LoginRequest
from fastapi import HTTPException
from fastapi.responses import JSONResponse,RedirectResponse

class AuthController:
    def __init__(self, auth_service):
        self.auth_service = auth_service

    async def login(self, login_request: LoginRequest):
        try:
            token_response = await self.auth_service.login(login_request)
            resp = JSONResponse(content={"message": "Login bem-sucedido!"})

            resp.set_cookie(
                key="access_token",
                value=token_response["access_token"],
                httponly=True,
                max_age=3600,  
                samesite="lax",
                secure=False  
            )

            return resp
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))
        
    async def logout(self):
        resp = RedirectResponse(url="/", status_code=302)
        resp.delete_cookie("access_token")
        return resp