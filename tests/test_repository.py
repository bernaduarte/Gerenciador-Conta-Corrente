import pytest
from app.repositories.user_repository import UserRepository
from app.models.user import User, UserRole
from app.models.account import Account
from app.models.transaction import Transaction, TransactionType
from sqlalchemy.orm import Session

@pytest.fixture
def setup_users(session: Session):
    user_normal = User(
        name="User Normal",
        account_number="11111",
        password="1111",
        user_type=UserRole.NORMAL
    )
    account_normal = Account(balance=1000.0, user=user_normal)

    user_vip = User(
        name="User VIP",
        account_number="22222",
        password="2222",
        user_type=UserRole.VIP
    )
    account_vip = Account(balance=5000.0, user=user_vip)

    session.add_all([user_normal, account_normal, user_vip, account_vip])
    session.commit()
    session.refresh(user_normal)
    session.refresh(user_vip)
    return user_normal, user_vip


def test_find_by_account_number(session: Session, setup_users):
    user_normal, _ = setup_users
    repo = UserRepository(session)
    found_user = repo.find_by_account_number("11111")
    assert found_user is not None
    assert found_user.account_number == "11111"
    assert found_user.name == "User Normal"

    not_found_user = repo.find_by_account_number("99999")
    assert not_found_user is None


def test_get_balance(session: Session, setup_users):
    user_normal, _ = setup_users
    repo = UserRepository(session)
    balance = repo.get_balance("11111")
    assert balance == 1000.0

    balance_not_found = repo.get_balance("99999")
    assert balance_not_found is None


def test_save_transaction(session: Session, setup_users):
    user_normal, _ = setup_users
    repo = UserRepository(session)
    transaction = Transaction(
        account_id=user_normal.account.id,
        value=50.0,
        type_transaction=TransactionType.DEPOSIT,
        description="Test Transaction"
    )
    saved_transaction = repo.save_transaction(transaction)
    assert saved_transaction.id is not None
    assert saved_transaction.value == 50.0
    assert saved_transaction.type_transaction == TransactionType.DEPOSIT


def test_change_balance_deposit(session: Session, setup_users):
    user_normal, _ = setup_users
    repo = UserRepository(session)
    initial_balance = user_normal.account.balance
    repo.change_balance(user_normal, 200.0, TransactionType.DEPOSIT, "Deposit Test")
    assert user_normal.account.balance == initial_balance + 200.0
    assert len(user_normal.account.transactions) == 1
    assert user_normal.account.transactions[0].value == 200.0


def test_change_balance_withdrawal(session: Session, setup_users):
    user_normal, _ = setup_users
    repo = UserRepository(session)
    initial_balance = user_normal.account.balance
    repo.change_balance(user_normal, 100.0, TransactionType.WITHDRAWAL, "Withdrawal Test")
    assert user_normal.account.balance == initial_balance - 100.0
    assert len(user_normal.account.transactions) == 1
    assert user_normal.account.transactions[0].value == -100.0


def test_transfer(session: Session, setup_users):
    user_normal, user_vip = setup_users
    repo = UserRepository(session)
    initial_balance_normal = user_normal.account.balance
    initial_balance_vip = user_vip.account.balance

    repo.transfer(user_normal, user_vip, 100.0, 8.0)

    assert user_normal.account.balance == initial_balance_normal - 100.0 - 8.0
    assert user_vip.account.balance == initial_balance_vip + 100.0
    assert len(user_normal.account.transactions) == 2 
    assert len(user_vip.account.transactions) == 1 


def test_get_user_information(session: Session, setup_users):
    user_normal, _ = setup_users
    repo = UserRepository(session)

    repo.change_balance(user_normal, 50.0, TransactionType.DEPOSIT, "Initial Deposit")
    repo.change_balance(user_normal, 20.0, TransactionType.WITHDRAWAL, "Initial Withdrawal")

    info = repo.get_user_information("11111")

    assert info is not None
    assert info["name"] == "User Normal"
    assert info["account_number"] == "11111"
    assert info["user_type"] == UserRole.NORMAL
    assert info["balance"] == user_normal.account.balance
    assert len(info["statement"]) == 2
    assert info["statement"][0]["description"] == "Initial Withdrawal"
    assert info["statement"][1]["description"] == "Initial Deposit"
