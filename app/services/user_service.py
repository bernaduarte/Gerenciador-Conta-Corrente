from app.models.transaction import TransactionType
from datetime import datetime
from app.models.transaction import Transaction
import pytz

class UserService:
    def __init__(self, user_repository):
        self.user_repository = user_repository

    def get_user_information(self, account_number: str):
        return self.user_repository.get_user_information(account_number)

    def _validate_transaction_value(self, value: float):
        if value <= 0:
            raise ValueError("O valor deve ser maior que zero.")

    def _calculate_transfer_tax(self, value: float, profile: str) -> float:
        return value * 0.008 if profile.upper() == "VIP" else 8.0

    def _can_transfer(self, value: float, profile: str, balance: float) -> bool:
        if profile.upper() == "VIP":
            return True
        return value <= 1000.0 and (balance >= value + self._calculate_transfer_tax(value, profile))

    def _apply_vip_negative_balance_penalty(self, user):
        if user.user_type.value.upper() != "VIP":
            return

        balance = user.account.balance
        if balance >= 0:
            return

        transactions = sorted(user.account.transactions, key=lambda t: t.timestamp, reverse=True)
        last_negative = None
        for t in transactions:
            if t.value < 0 and t.type_transaction in [TransactionType.WITHDRAWAL, TransactionType.TRANSFER]:
                last_negative = t.timestamp
                break

        if not last_negative:
            return

        saopaulo_tz = pytz.timezone("America/Sao_Paulo")
        now = datetime.now(saopaulo_tz)

        if last_negative.tzinfo is None or last_negative.tzinfo.utcoffset(last_negative) is None:
            last_negative = saopaulo_tz.localize(last_negative)
        else:
            last_negative = last_negative.astimezone(saopaulo_tz)

        minutes = int((now - last_negative).total_seconds() // 60)
        if minutes <= 0:
            return

        penalty = abs(balance) * (0.001 * minutes)
        user.account.balance -= penalty

        penalty_transaction = Transaction(
            account_id=user.account.id,
            value=-penalty,
            type_transaction=TransactionType.WITHDRAWAL,
            description=f"Penalidade saldo negativo VIP ({minutes} min)"
        )
        self.user_repository.save_transaction(penalty_transaction)

    def change_balance(self, account_number: str, amount: float, transaction_type: str, profile: str, target_account_number: str = None):
        self._validate_transaction_value(amount)
        user = self.user_repository.find_by_account_number(account_number)
        if not user:
            raise ValueError("Conta de origem inválida.")

        transaction_type_enum = TransactionType(transaction_type.lower())

        if transaction_type_enum == TransactionType.DEPOSIT:
            result = self.user_repository.change_balance(user, amount, transaction_type_enum, "Depósito realizado")

            return result

        if transaction_type_enum == TransactionType.WITHDRAWAL:
            if user.account.balance < amount and profile.upper() != "VIP":
                raise ValueError("Saldo insuficiente para saque.")
            if profile.upper() == "VIP":
                self._apply_vip_negative_balance_penalty(user)
            result = self.user_repository.change_balance(user, amount, transaction_type_enum, "Saque realizado")
            return result

        if transaction_type_enum == TransactionType.TRANSFER:
            if not target_account_number or len(target_account_number) != 5:
                raise ValueError("Conta de destino inválida.")
            if account_number == target_account_number:
                raise ValueError("Não é possível transferir para a própria conta.")

            target_user = self.user_repository.find_by_account_number(target_account_number)
            if not target_user:
                raise ValueError("Conta de destino não encontrada.")

            tax = self._calculate_transfer_tax(amount, profile)

            if not self._can_transfer(amount, profile, user.account.balance):
                raise ValueError("Limite de transferência ou saldo insuficiente")

            if profile.upper() == "VIP":
                self._apply_vip_negative_balance_penalty(user)
            result = self.user_repository.transfer(user, target_user, amount, tax)
            return result

        raise ValueError("Tipo de transação inválido.")

    def manager_visit(self, account_number: str, profile: str):
        if profile.upper() != "VIP":
            raise PermissionError("Apenas usuários VIP podem solicitar visita do gerente.")

        user = self.user_repository.find_by_account_number(account_number)
        if not user or not user.account:
            raise ValueError("Usuário não encontrado.")

        if user.account.balance < 50:
            raise ValueError("Saldo insuficiente para solicitação.")
        return self.user_repository.change_balance(user, 50.0, TransactionType.WITHDRAWAL, "Solicitação de visita do gerente")