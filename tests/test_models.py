import pytest
from app.models.user import User, UserRole
from app.models.account import Account
from app.models.transaction import Transaction, TransactionType
from sqlalchemy.orm import Session


def test_create_user(session: Session):
    user = User(
        name="Test User",
        account_number="12345",
        password="password",
        user_type=UserRole.NORMAL
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    assert user.id is not None
    assert user.name == "Test User"


def test_create_account(session: Session):
    user = User(
        name="Account User",
        account_number="54321",
        password="pass",
        user_type=UserRole.VIP
    )
    session.add(user)
    session.commit()
    session.refresh(user)

    account = Account(
        balance=100.0,
        user_id=user.id
    )
    session.add(account)
    session.commit()
    session.refresh(account)
    assert account.id is not None
    assert account.balance == 100.0
    assert account.user_id == user.id


def test_create_transaction(session: Session):
    user = User(
        name="Transaction User",
        account_number="98765",
        password="1234",
        user_type=UserRole.NORMAL
    )
    session.add(user)
    session.commit()
    session.refresh(user)

    account = Account(
        balance=500.0,
        user_id=user.id
    )
    session.add(account)
    session.commit()
    session.refresh(account)

    transaction = Transaction(
        account_id=account.id,
        value=50.0,
        type_transaction=TransactionType.DEPOSIT,
        description="Test Deposit"
    )
    session.add(transaction)
    session.commit()
    session.refresh(transaction)

    assert transaction.id is not None
    assert transaction.account_id == account.id
    assert transaction.value == 50.0
    assert transaction.type_transaction == TransactionType.DEPOSIT
    assert transaction.description == "Test Deposit"

