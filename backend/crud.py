# backend/crud.py
from sqlalchemy.orm import Session
import models, schemas
from sqlalchemy import func
# IMPORTANT: Import the hash function for user creation
from auth import hash_password 

# ---------- USERS ----------
def get_user_by_username(db: Session, username: str):
    return db.query(models.User).filter(models.User.user_name == username).first()

def get_user_by_email(db: Session, email: str):
    # This function is used to check for duplicate emails during registration.
    return db.query(models.User).filter(models.User.email == email).first()

def create_user(db: Session, user: schemas.UserCreate):
    # CRITICAL FIX: Hash the password before saving to the database
    hashed_password = hash_password(user.password)
    
    new = models.User(
        user_name=user.user_name,
        email=user.email,
        password=hashed_password # Store the HASHED password
    )
    db.add(new)
    db.commit()
    db.refresh(new)
    return new

# ---------- EXPENSE ----------
def create_expense(db: Session, exp: schemas.ExpenseCreate, user_id: int):
    new_exp = models.Expense(
        user_ID=user_id,
        category_ID=exp.category_ID,
        payment_ID=exp.payment_ID,
        amount=exp.amount,
        description=exp.description
    )
    db.add(new_exp)
    db.commit()
    db.refresh(new_exp)
    return new_exp

def list_expenses_by_user(db: Session, user_id: int):
    return db.query(models.Expense).filter(models.Expense.user_ID == user_id).order_by(models.Expense.created_at.desc()).all()

def get_expense_by_id(db: Session, eid: int):
    return db.query(models.Expense).filter(models.Expense.expense_ID == eid).first()

def delete_expense(db: Session, eid: int):
    exp = get_expense_by_id(db, eid)
    if exp:
        db.delete(exp)
        db.commit()
    return exp

# ---------- CATEGORY ----------
def create_category(db: Session, cname: str):
    new = models.Category(category_name=cname)
    db.add(new)
    db.commit()
    db.refresh(new)
    return new

def list_categories_global(db: Session):
    return db.query(models.Category).order_by(models.Category.category_name).all()

# ---------- PAYMENT METHOD ----------
def create_payment_method(db: Session, ptype: str):
    new = models.Payment(payment_type=ptype)
    db.add(new)
    db.commit()
    db.refresh(new)
    return new

def list_payments_global(db: Session):
    return db.query(models.Payment).order_by(models.Payment.payment_type).all()

# ---------- BUDGET ----------
def create_budget(db: Session, b: schemas.BudgetCreate, user_id: int):
    new = models.Budget(user_ID=user_id, category_ID=b.category_ID, amount_limit=b.amount)
    db.add(new)
    db.commit()
    db.refresh(new)
    return new

def list_budgets_by_user(db: Session, user_id: int):
    return db.query(models.Budget).filter(models.Budget.user_ID == user_id).all()

def get_budget_by_id(db: Session, bid: int):
    return db.query(models.Budget).filter(models.Budget.budget_ID == bid).first()

def delete_budget(db: Session, bid: int):
    b = get_budget_by_id(db, bid)
    if b:
        db.delete(b)
        db.commit()
    return b

# ---------- REPORTS ----------
def total_expense_for_user(db: Session, user_id: int):
    total = db.query(func.sum(models.Expense.amount)).filter(models.Expense.user_ID == user_id).scalar()
    return total if total is not None else 0

def spending_by_category_for_user(db: Session, user_id: int):
    return db.query(
        models.Category.category_name, 
        func.sum(models.Expense.amount)
    ).join(models.Expense).filter(
        models.Expense.user_ID == user_id
    ).group_by(
        models.Category.category_name
    ).order_by(
        func.sum(models.Expense.amount).desc()
    ).all()
