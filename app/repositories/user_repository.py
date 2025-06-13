from sqlalchemy.orm import Session
from app.models.user import User
from app.models.transaction import Transaction
from app.repositories.iuserRepository import IUserRepository
from app.models.transaction import TransactionType 

class UserRepository(IUserRepository):
    def __init__(self, db: Session):
        self.db = db

    def find_by_account_number(self, account_number: str) -> User | None:
        return self.db.query(User).filter(User.account_number == account_number).first()

    def get_balance(self, account_number: str) -> float | None:
        user = self.find_by_account_number(account_number)
        return user.account.balance if user and user.account else None

    def save_transaction(self, transaction: Transaction):
        self.db.add(transaction)
        self.db.commit()
        self.db.refresh(transaction)
        return transaction

    def change_balance(
        self,
        user: User,
        amount: float,
        transaction_type: TransactionType,
        description: str
    ):
        if transaction_type == TransactionType.DEPOSIT:
            user.account.balance += amount
            value_to_save = amount
        elif transaction_type == TransactionType.WITHDRAWAL:
            user.account.balance -= amount
            value_to_save = -amount 

        transaction = Transaction(
            account_id=user.account.id,
            value=value_to_save,
            type_transaction=transaction_type,
            description=description,
        )
        return self.save_transaction(transaction)


    def transfer(self, origin_user: User, target_user: User, amount: float, tax: float):
        origin_user.account.balance -= amount + tax
        target_user.account.balance += amount

        transaction = Transaction(
            account_id=origin_user.id,
            value=-amount,
            type_transaction=TransactionType.TRANSFER,
            description=f"Transferência para {target_user.name} ({target_user.account_number})"
        )
        tax_transaction = Transaction(
            account_id=origin_user.id,
            value=-tax, 
            type_transaction=TransactionType.TRANSFER,
            description="Taxa de transferência"
        )
        receiver_transaction = Transaction(
            account_id=target_user.id,
            value=amount,  
            type_transaction=TransactionType.TRANSFER,
            description=f"Transferência recebida de {origin_user.name} ({origin_user.account_number})"
        )

        self.db.add_all([transaction, tax_transaction, receiver_transaction])
        self.db.commit()
        return origin_user


    def get_user_information(self, account_number: str):
        user = self.find_by_account_number(account_number)
        if not user:
            return None

        transactions = sorted(
            user.account.transactions,
            key=lambda t: t.timestamp,
            reverse=True
        )

        return {
            "name": user.name,
            "account_number": user.account_number,
            "user_type": user.user_type.value,
            "balance": user.account.balance,
            "statement": [
                {
                    "timestamp": t.timestamp.isoformat(),
                    "description": t.description,
                    "value": f"{t.value:.2f}"
                }
                for t in transactions
            ]
        }
    def apply_negative_balance_fee(self, user_id: int):
        
        from app.models.user import User
        from app.models.transaction import Transaction, TransactionType
        from datetime import datetime

        user = self.db.query(User).filter(User.id == user_id).first()
        if not user or user.user_type.value != "vip" or user.account.balance >= 0:
            return

        fee_amount = abs(user.account.balance) * 0.001

        user.account.balance -= fee_amount

        transaction = Transaction(
            account_id=user.account.id,
            value=-fee_amount,
            type_transaction=TransactionType.NEGATIVE_BALANCE_FEE,
            description="Débito por saldo negativo (0.1%)"
        )

        self.db.add(user.account) 
        self.db.add(transaction)
        self.db.commit()
        self.db.refresh(user.account)
        self.db.refresh(transaction)

