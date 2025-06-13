import pytest
from unittest.mock import Mock
from app.services.user_service import UserService
from app.models.user import User, UserRole
from app.models.account import Account
from app.models.transaction import Transaction, TransactionType
from datetime import datetime, timedelta

@pytest.fixture
def mock_user_repository():
    return Mock()

@pytest.fixture
def user_service(mock_user_repository):
    return UserService(mock_user_repository)

@pytest.fixture
def mock_user_normal():
    user = User(
        name="User Normal",
        account_number="11111",
        password="1111",
        user_type=UserRole.NORMAL
    )
    user.account = Account(balance=1000.0, user=user)
    return user

@pytest.fixture
def mock_user_vip():
    user = User(
        name="User VIP",
        account_number="22222",
        password="2222",
        user_type=UserRole.VIP
    )
    user.account = Account(balance=5000.0, user=user)
    return user

def test_get_user_information(user_service, mock_user_repository, mock_user_normal):
    mock_user_repository.get_user_information.return_value = {
        "name": mock_user_normal.name,
        "account_number": mock_user_normal.account_number,
        "user_type": mock_user_normal.user_type.value,
        "balance": mock_user_normal.account.balance,
        "statement": []
    }
    info = user_service.get_user_information("11111")
    assert info["account_number"] == "11111"
    mock_user_repository.get_user_information.assert_called_once_with("11111")

def test_validate_transaction_value(user_service):
    with pytest.raises(ValueError, match="O valor deve ser maior que zero."):
        user_service._validate_transaction_value(0)
    with pytest.raises(ValueError, match="O valor deve ser maior que zero."):
        user_service._validate_transaction_value(-10)
    user_service._validate_transaction_value(10)

def test_calculate_transfer_tax(user_service):
    assert user_service._calculate_transfer_tax(1000, "NORMAL") == 8.0
    assert user_service._calculate_transfer_tax(1000, "VIP") == 8.0
    assert user_service._calculate_transfer_tax(5000, "VIP") == 40.0

def test_can_transfer(user_service):
    # NORMAL
    assert user_service._can_transfer(100, "NORMAL", 200) is True
    assert user_service._can_transfer(1000, "NORMAL", 1008) is True
    assert user_service._can_transfer(1001, "NORMAL", 2000) is False 
    assert user_service._can_transfer(100, "NORMAL", 100) is False 
    # VIP
    assert user_service._can_transfer(10000, "VIP", 5000) is True 

def test_apply_vip_negative_balance_penalty(user_service, mock_user_vip):
    
    mock_user_vip.account.balance = 100.0
    user_service._apply_vip_negative_balance_penalty(mock_user_vip)
    assert mock_user_vip.account.balance == 100.0

    
    mock_user_vip.account.balance = -100.0
  
    mock_user_vip.account.transactions = [
        Transaction(
            account_id=mock_user_vip.account.id,
            value=-100.0,
            type_transaction=TransactionType.WITHDRAWAL,
            description="Withdrawal",
            timestamp=datetime.utcnow() - timedelta(minutes=10)
        )
    ]
    user_service._apply_vip_negative_balance_penalty(mock_user_vip)
  
    assert mock_user_vip.account.balance == -100.0
    user_service.user_repository.save_transaction.assert_not_called()

def test_change_balance_deposit(user_service, mock_user_repository, mock_user_normal):
    mock_user_repository.find_by_account_number.return_value = mock_user_normal
    user_service.change_balance("11111", 200.0, "deposit", "NORMAL")
    mock_user_repository.change_balance.assert_called_once_with(mock_user_normal, 200.0, TransactionType.DEPOSIT, "Depósito realizado")

def test_change_balance_withdrawal_normal(user_service, mock_user_repository, mock_user_normal):
    mock_user_repository.find_by_account_number.return_value = mock_user_normal
    user_service.change_balance("11111", 100.0, "withdrawal", "NORMAL")
    mock_user_repository.change_balance.assert_called_once_with(mock_user_normal, 100.0, TransactionType.WITHDRAWAL, "Saque realizado")

def test_change_balance_withdrawal_insufficient_balance(user_service, mock_user_repository, mock_user_normal):
    mock_user_repository.find_by_account_number.return_value = mock_user_normal
    with pytest.raises(ValueError, match="Saldo insuficiente para saque."):
        user_service.change_balance("11111", 2000.0, "withdrawal", "NORMAL")

def test_change_balance_withdrawal_vip(user_service, mock_user_repository, mock_user_vip):
    mock_user_repository.find_by_account_number.return_value = mock_user_vip
    user_service.change_balance("22222", 6000.0, "withdrawal", "VIP") # VIP can have negative balance
    mock_user_repository.change_balance.assert_called_once_with(mock_user_vip, 6000.0, TransactionType.WITHDRAWAL, "Saque realizado")

def test_change_balance_transfer_success(user_service, mock_user_repository, mock_user_normal, mock_user_vip):
    mock_user_repository.find_by_account_number.side_effect = [mock_user_normal, mock_user_vip]
    user_service.change_balance("11111", 100.0, "transfer", "NORMAL", "22222")
    mock_user_repository.transfer.assert_called_once()

def test_change_balance_transfer_invalid_target_account(user_service, mock_user_repository, mock_user_normal):
    mock_user_repository.find_by_account_number.return_value = mock_user_normal
    with pytest.raises(ValueError, match="Conta de destino inválida."):
        user_service.change_balance("11111", 100.0, "transfer", "NORMAL", "123")

    with pytest.raises(ValueError, match="Conta de destino não encontrada."):
        mock_user_repository.find_by_account_number.side_effect = [mock_user_normal, None]
        user_service.change_balance("11111", 100.0, "transfer", "NORMAL", "99999")

def test_change_balance_transfer_self_transfer(user_service, mock_user_repository, mock_user_normal):
    mock_user_repository.find_by_account_number.return_value = mock_user_normal
    with pytest.raises(ValueError, match="Não é possível transferir para a própria conta."):
        user_service.change_balance("11111", 100.0, "transfer", "NORMAL", "11111")

def test_change_balance_transfer_insufficient_limit(user_service, mock_user_repository, mock_user_normal, mock_user_vip):
    mock_user_repository.find_by_account_number.side_effect = [mock_user_normal, mock_user_vip]
    with pytest.raises(ValueError, match="Limite de transferência ou saldo insuficiente"):
        user_service.change_balance("11111", 1500.0, "transfer", "NORMAL", "22222")

def test_manager_visit_success(user_service, mock_user_repository, mock_user_vip):
    mock_user_repository.find_by_account_number.return_value = mock_user_vip
    user_service.manager_visit("22222", "VIP")
    mock_user_repository.change_balance.assert_called_once_with(mock_user_vip, 50.0, TransactionType.WITHDRAWAL, "Solicitação de visita do gerente")

def test_manager_visit_not_vip(user_service, mock_user_normal):
    with pytest.raises(PermissionError, match="Apenas usuários VIP podem solicitar visita do gerente."):
        user_service.manager_visit("11111", "NORMAL")

def test_manager_visit_user_not_found(user_service, mock_user_repository):
    mock_user_repository.find_by_account_number.return_value = None
    with pytest.raises(ValueError, match="Usuário não encontrado."):
        user_service.manager_visit("99999", "VIP")

def test_manager_visit_insufficient_balance(user_service, mock_user_repository, mock_user_vip):
    mock_user_vip.account.balance = 40.0
    mock_user_repository.find_by_account_number.return_value = mock_user_vip
    user_service.manager_visit("22222", "VIP")
    user_service.user_repository.change_balance.assert_called_once_with(
        mock_user_vip, 50.0, TransactionType.WITHDRAWAL, "Solicitação de visita do gerente"
    )
