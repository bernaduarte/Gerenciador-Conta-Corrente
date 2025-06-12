from fastapi import Request,HTTPException

class UserController:
    def __init__(self, user_service):
        self.user_service = user_service

    async def get_information(self, request: Request):
        try:
            payload = request.state.user
            account_number = payload.get("sub") 
            return self.user_service.get_user_information(account_number)
        except Exception as e:
            return HTTPException(status_code=422, detail=str(e))
        
    async def change_balance_on_account_number(self, request: Request, new_balance: float, type_transaction: str,target_account_number: str = None):
        try:
            payload = request.state.user
            account_number = payload.get("sub") 
            user = self.user_service.change_balance(account_number, new_balance,type_transaction,payload.get("user_type"),target_account_number)
            if not user:
                raise HTTPException(status_code=404, detail="User not found or account does not exist")
            return {"message": "Balance updated successfully", "new_balance": user.account.balance}
        except Exception as e:
            return HTTPException(status_code=422, detail=str(e))
        

    async def manager_visit(self, request: Request):
        try:
            payload = request.state.user
            account_number = payload.get("sub") 
            profile = payload.get("user_type")
            return self.user_service.manager_visit(account_number, profile)
        except PermissionError as e:
            return HTTPException(status_code=403, detail=str(e))
        except Exception as e:
            return HTTPException(status_code=422, detail=str(e))