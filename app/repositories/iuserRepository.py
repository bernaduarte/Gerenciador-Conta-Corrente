from abc import ABC, abstractmethod
from typing import Optional, Any
from app.models.user import User
from app.models.transaction import Transaction, TransactionType

class IUserRepository(ABC):
    @abstractmethod
    def find_by_account_number(self, account_number: str) -> Optional[User]:
        pass

    @abstractmethod
    def get_balance(self, account_number: str) -> Optional[float]:
        pass

    @abstractmethod
    def save_transaction(self, transaction: Transaction) -> Transaction:
        pass

    @abstractmethod
    def change_balance(
        self,
        user: User,
        amount: float,
        transaction_type: TransactionType,
        description: str
    ) -> Any:
        pass

    @abstractmethod
    def transfer(self, origin_user: User, target_user: User, amount: float, tax: float) -> Any:
        pass

    @abstractmethod
    def get_user_information(self, account_number: str) -> Optional[dict]:
        pass