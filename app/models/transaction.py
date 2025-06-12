from app.database import Base
from sqlalchemy import Column, Integer, String, Float, ForeignKey,Enum as SqlEnum
from sqlalchemy.orm import relationship
from datetime import datetime
from sqlalchemy.sql.sqltypes import DateTime
from enum import Enum
import pytz

class TransactionType(str, Enum):
    DEPOSIT = "deposit"
    TRANSFER = "transfer"
    WITHDRAWAL = "withdrawal"

def now_brasilia():
    return datetime.now(pytz.timezone("America/Sao_Paulo"))

class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime(timezone=True), default=now_brasilia, nullable=False)
    description = Column(String)
    value = Column(Float)
    type_transaction = Column(SqlEnum(TransactionType), nullable=False)
    account_id = Column(Integer, ForeignKey("accounts.id"))

    account = relationship("Account", back_populates="transactions")