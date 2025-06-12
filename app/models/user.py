from sqlalchemy import Column, Integer, String,Enum as SqlEnum
from sqlalchemy.orm import relationship
from app.database import Base
from enum import Enum

class UserRole(str, Enum):
    NORMAL = "normal"
    VIP = "vip"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    account_number = Column(String(5), unique=True, index=True)
    password = Column(String(4),nullable=False) 
    user_type = Column(SqlEnum(UserRole),nullable=False)

    account = relationship("Account", back_populates="user", uselist=False)