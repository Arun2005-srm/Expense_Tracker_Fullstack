from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, DECIMAL
from sqlalchemy.orm import relationship
from datetime import datetime
from backend.database import Base

class User(Base):
    __tablename__ = "user"  # ✅ match MySQL table name

    user_ID = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_name = Column(String(100), nullable=False)
    password = Column(String(100), nullable=False)
    user_email = Column(String(150), nullable=False, unique=True)
    contact_num_1 = Column(String(15), nullable=False, unique=True)
    contact_num_2 = Column(String(15), nullable=True, unique=True)
    

    # Relationships (optional but recommended)
    expenses = relationship("Expense", back_populates="user")
    budgets = relationship("Budget", back_populates="user")


class Category(Base):
    __tablename__ = "category"

    category_ID = Column(Integer, primary_key=True, index=True, autoincrement=True)
    category_name = Column(String(100), nullable=False)

    expenses = relationship("Expense", back_populates="category")
    budgets = relationship("Budget", back_populates="category")


class PaymentMethod(Base):
    __tablename__ = "payment_method"

    payment_ID = Column(Integer, primary_key=True, index=True, autoincrement=True)
    payment_type = Column(String(50), nullable=True)

    expenses = relationship("Expense", back_populates="payment_method")


class Expense(Base):
    __tablename__ = "expense"

    expense_ID = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_ID = Column(Integer, ForeignKey("user.user_ID"), nullable=False)
    category_ID = Column(Integer, ForeignKey("category.category_ID"), nullable=False)
    payment_ID = Column(Integer, ForeignKey("payment_method.payment_ID"), nullable=False)
    date = Column(DateTime, default=datetime.utcnow)
    amount = Column(DECIMAL(10, 2))
    description = Column(String(255))

    user = relationship("User", back_populates="expenses")
    category = relationship("Category", back_populates="expenses")
    payment_method = relationship("PaymentMethod", back_populates="expenses")


class Budget(Base):
    __tablename__ = "budget"

    budget_ID = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_ID = Column(Integer, ForeignKey("user.user_ID"), nullable=False)
    category_ID = Column(Integer, ForeignKey("category.category_ID"), nullable=False)
    amount_limit = Column(DECIMAL(10, 2))
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=False)

    user = relationship("User", back_populates="budgets")
    category = relationship("Category", back_populates="budgets")
