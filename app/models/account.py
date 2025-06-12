from app.database import Base
from sqlalchemy import Column, Integer,Float, ForeignKey
from sqlalchemy.orm import relationship

class Account(Base):
      __tablename__ = "accounts"
  
      id = Column(Integer, primary_key=True, index=True)
      user_id = Column(Integer, ForeignKey("users.id"))
      balance = Column(Float, default=0.0)
  
      user = relationship("User", back_populates="account")
      transactions = relationship("Transaction", back_populates="account")