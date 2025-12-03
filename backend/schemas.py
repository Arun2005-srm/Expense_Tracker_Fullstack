from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import date, datetime

# ======================
# 👤 USER SCHEMAS
# ======================
class UserCreate(BaseModel):
    user_name: str
    password: str
    user_email: EmailStr
    contact_num_1: str
    contact_num_2: Optional[str] = None


class LoginRequest(BaseModel):
    username: str
    password: str


# ======================
# 🏷 CATEGORY / PAYMENT
# ======================
class CategoryCreate(BaseModel):
    category_name: str


class PaymentMethodCreate(BaseModel):
    payment_type: str


# ======================
# 💰 BUDGET SCHEMAS
# ======================
class BudgetCreate(BaseModel):
    user_ID: int
    category_ID: int
    amount_limit: float
    start_date: date
    end_date: date


# Used for PUT update (all fields optional)
class BudgetUpdate(BaseModel):
    category_ID: Optional[int] = None
    amount_limit: Optional[float] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None


# ======================
# 💸 EXPENSE SCHEMAS
# ======================
class ExpenseCreate(BaseModel):
    user_ID: int
    category_ID: int
    payment_ID: int
    amount: float
    date: datetime
    description: Optional[str] = None


# Used for PUT update (all fields optional)
class ExpenseUpdate(BaseModel):
    category_ID: Optional[int] = None
    payment_ID: Optional[int] = None
    amount: Optional[float] = None
    date: Optional[datetime] = None
    description: Optional[str] = None

