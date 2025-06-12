from app.database import SessionLocal
from app.models.user import User, UserRole
from app.models.account import Account
from sqlalchemy.orm import Session

def seed():
    db: Session = SessionLocal()

    if db.query(User).count() > 0:
        db.close()
        return

    user1 = User(
        name="Bernado Normal",
        account_number="12345",
        password="1111",
        user_type=UserRole.NORMAL
    )
    account1 = Account(balance=1000.0, user=user1)

    user2 = User(
        name="Amanda VIP",
        account_number="54321",
        password="2222",
        user_type=UserRole.VIP
    )
    account2 = Account(balance=5000.0, user=user2)

    db.add_all([user1, account1, user2, account2])
    db.commit()
    db.close()

if __name__ == "__main__":
    seed()