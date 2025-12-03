from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import func
from backend import models, schemas
from backend.database import engine, get_db
from backend.auth import router as auth_router

# create tables (if not already)
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Expense Tracker API", version="3.1")

# CORS - allow your Streamlit frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:8501",
        "http://127.0.0.1:8501",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# include authentication router
app.include_router(auth_router, prefix="/auth", tags=["Authentication"])

# -----------------------
# Categories & Payments
# -----------------------
@app.get("/categories", tags=["Categories"])
def get_categories(db: Session = Depends(get_db)):
    return db.query(models.Category).all()

@app.get("/payment-methods", tags=["Payments"])
def get_payment_methods(db: Session = Depends(get_db)):
    return db.query(models.PaymentMethod).all()

# -----------------------
# Budgets (user-specific)
# -----------------------
@app.get("/budgets/{user_id}", tags=["Budgets"])
def get_user_budgets(user_id: int, db: Session = Depends(get_db)):
    return db.query(models.Budget).filter(models.Budget.user_ID == user_id).all()

@app.post("/budgets/add", status_code=status.HTTP_201_CREATED, tags=["Budgets"])
def add_budget(budget: schemas.BudgetCreate, db: Session = Depends(get_db)):
    new_budget = models.Budget(**budget.dict())
    db.add(new_budget)
    db.commit()
    db.refresh(new_budget)
    return {"message": "Budget created successfully", "budget": new_budget}

@app.put("/budgets/{budget_id}", tags=["Budgets"])
def update_budget(budget_id: int, update: schemas.BudgetUpdate, db: Session = Depends(get_db)):
    budget = db.query(models.Budget).filter(models.Budget.budget_ID == budget_id).first()
    if not budget:
        raise HTTPException(status_code=404, detail="Budget not found")
    for k, v in update.dict(exclude_unset=True).items():
        setattr(budget, k, v)
    db.commit()
    db.refresh(budget)
    return {"message": "Budget updated", "budget": budget}

@app.delete("/budgets/{budget_id}", tags=["Budgets"])
def delete_budget(budget_id: int, db: Session = Depends(get_db)):
    budget = db.query(models.Budget).filter(models.Budget.budget_ID == budget_id).first()
    if not budget:
        raise HTTPException(status_code=404, detail="Budget not found")
    db.delete(budget)
    db.commit()
    return {"message": "Budget deleted successfully"}

# -----------------------
# Expenses (user-specific)
# -----------------------
@app.get("/expenses/{user_id}", tags=["Expenses"])
def get_user_expenses(user_id: int, db: Session = Depends(get_db)):
    return db.query(models.Expense).filter(models.Expense.user_ID == user_id).all()

@app.post("/expenses/add", status_code=status.HTTP_201_CREATED, tags=["Expenses"])
def add_expense(expense: schemas.ExpenseCreate, db: Session = Depends(get_db)):
    new_expense = models.Expense(**expense.dict())
    db.add(new_expense)
    db.commit()
    db.refresh(new_expense)
    return {"message": "Expense added successfully", "expense": new_expense}

@app.put("/expenses/{expense_id}", tags=["Expenses"])
def update_expense(expense_id: int, update: schemas.ExpenseUpdate, db: Session = Depends(get_db)):
    exp = db.query(models.Expense).filter(models.Expense.expense_ID == expense_id).first()
    if not exp:
        raise HTTPException(status_code=404, detail="Expense not found")
    for k, v in update.dict(exclude_unset=True).items():
        setattr(exp, k, v)
    db.commit()
    db.refresh(exp)
    return {"message": "Expense updated", "expense": exp}

@app.delete("/expenses/{expense_id}", tags=["Expenses"])
def delete_expense(expense_id: int, db: Session = Depends(get_db)):
    exp = db.query(models.Expense).filter(models.Expense.expense_ID == expense_id).first()
    if not exp:
        raise HTTPException(status_code=404, detail="Expense not found")
    db.delete(exp)
    db.commit()
    return {"message": "Expense deleted successfully"}

# -----------------------
# Reports (user-specific)
# -----------------------
@app.get("/reports/spending-by-category/{user_id}", tags=["Reports"])
def get_spending_by_category(user_id: int, db: Session = Depends(get_db)):
    results = (
        db.query(
            models.Category.category_name,
            func.sum(models.Expense.amount).label("total_spent")
        )
        .join(models.Expense, models.Category.category_ID == models.Expense.category_ID)
        .filter(models.Expense.user_ID == user_id)
        .group_by(models.Category.category_name)
        .all()
    )
    return [{"category_name": r[0], "total": float(r[1] or 0)} for r in results]

@app.get("/reports/total-spending/{user_id}", tags=["Reports"])
def get_total_spending(user_id: int, db: Session = Depends(get_db)):
    total = db.query(func.sum(models.Expense.amount)).filter(models.Expense.user_ID == user_id).scalar()
    return {"user_id": user_id, "total_spending": float(total or 0.0)}

from sqlalchemy import func

from sqlalchemy import func, extract

from sqlalchemy import extract, func

from sqlalchemy import func

from sqlalchemy import func, extract

from sqlalchemy import func

from sqlalchemy import func

from sqlalchemy import func, cast, String

from sqlalchemy import func

from sqlalchemy import func

@app.get("/reports/monthly-spending/{user_id}", tags=["Reports"])
def get_monthly_spending(user_id: int, db: Session = Depends(get_db)):
    results = (
        db.query(
            func.year(models.Expense.date).label("year"),
            func.month(models.Expense.date).label("month_num"),
            func.min(
                func.concat(
                    func.year(models.Expense.date), "-",
                    func.lpad(func.month(models.Expense.date), 2, "0")
                )
            ).label("month"),  # ✅ fixed for only_full_group_by
            func.sum(models.Expense.amount).label("total")
        )
        .filter(models.Expense.user_ID == user_id)
        .group_by(func.year(models.Expense.date), func.month(models.Expense.date))
        .order_by(func.year(models.Expense.date), func.month(models.Expense.date))
        .all()
    )

    return [{"month": r.month, "total": float(r.total or 0)} for r in results]





# -----------------------
# Delete user (account removal)
# -----------------------
@app.delete("/users/{user_id}", tags=["Users"])
def delete_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.user_ID == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    db.query(models.Expense).filter(models.Expense.user_ID == user_id).delete()
    db.query(models.Budget).filter(models.Budget.user_ID == user_id).delete()
    db.delete(user)
    db.commit()
    return {"message": "User and related data deleted successfully"}

# -----------------------
# Utility: seed default categories/payment methods
# -----------------------
@app.post("/seed-data", tags=["Utility"])
def seed_initial_data(db: Session = Depends(get_db)):
    default_categories = ["Food", "Transport", "Entertainment", "Bills", "Health", "Shopping", "Education"]
    for name in default_categories:
        if not db.query(models.Category).filter(models.Category.category_name == name).first():
            db.add(models.Category(category_name=name))

    default_methods = ["Cash", "Credit Card", "Debit Card", "UPI", "Net Banking"]
    for m in default_methods:
        if not db.query(models.PaymentMethod).filter(models.PaymentMethod.payment_type == m).first():
            db.add(models.PaymentMethod(payment_type=m))

    db.commit()
    return {"message": "✅ Default data seeded successfully."}

# -----------------------
# Root
# -----------------------
@app.get("/")
def root():
    return {"message": "Expense Tracker API is running 🚀"}
