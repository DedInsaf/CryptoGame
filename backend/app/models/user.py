from sqlalchemy import Column, Integer, String, Float
from backend.app.utils.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True)
    password = Column(String(100))
    balance = Column(Float, default=1000.0)


class CryptoOrder(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer)
    crypto_name = Column(String(20))
    amount = Column(Float)
    price = Column(Float)
    status = Column(String(20), default="pending")