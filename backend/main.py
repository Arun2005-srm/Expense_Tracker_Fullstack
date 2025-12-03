from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from . import models, schemas, crud
from .database import engine, SessionLocal, Base
from auth import create_token, decode_token, verify_password, hash_password
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from auth import router as auth_router

# --- DATABASE SETUP ---
Base.metadata.create_all(bind=engine)

# --- APP INITIALIZATION ---
app = FastAPI(title="Expense Tracker API")

# --- CORS MIDDLEWARE ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- DEPENDENCY: DB SESSION ---
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- AUTH CONFIGURATION ---
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """Decodes JWT and returns the current user object."""
    try:
        payload = decode_token(token)
        user_name: str = payload.get("sub")
        user_id: int = payload.get("user_id")

        if user_name is None or user_id is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

        user = crud.get_user_by_username(db, user_name)
        if not user:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")

        return user
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token or expired")

# =====================================================
#                   AUTH ROUTES
# =====================================================

@app.post("/register", response_model=schemas.UserOut)
def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
    """Register a new user."""
    if crud.get_user_by_username(db, user.user_name):
        raise HTTPException(status_code=400, detail="Username already exists")

    new_user = crud.create_user(db, user)
    return new_user


@app.post("/login", response_model=schemas.TokenOut)
def login(data: schemas.LoginRequest, db: Session = Depends(get_db)):
    """Login and get JWT token."""
    user = crud.get_user_by_username(db, data.user_name)
    if not user or not verify_password(data.password, user.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_token({"sub": user.user_name, "user_id": user.user_ID})
    return {"access_token": token, "token_type": "bearer"}


# =====================================================
#                USER-BASED ROUTES
# =====================================================

@app.get("/me", response_model=schemas.UserOut)
def read_current_user(current_user: schemas.UserOut = Depends(get_current_user)):
    """Returns current logged-in user details."""
    return current_user


# =====================================================
#                EXPENSES (User-Specific)
# =====================================================

@app.post("/expenses", response_model=schemas.ExpenseOut)
def add_expense(
    exp: schemas.ExpenseCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Add an expense for the logged-in user."""
    return crud.create_expense(db, exp, current_user.user_ID)


@app.get("/expenses", response_model=list[schemas.ExpenseOut])
def list_user_expenses(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Get all expenses for the logged-in user."""
    return crud.list_expenses_by_user(db, current_user.user_ID)


@app.delete("/expenses/{expense_id}")
def delete_expense(
    expense_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Delete expense (only if owned by user)."""
    expense = crud.get_expense_by_id(db, expense_id)
    if not expense or expense.user_ID != current_user.user_ID:
        raise HTTPException(status_code=404, detail="Expense not found")
    crud.delete_expense(db, expense_id)
    return {"detail": "Expense deleted"}


# =====================================================
#                BUDGETS (User-Specific)
# =====================================================

@app.post("/budgets", response_model=schemas.BudgetOut)
def add_budget(
    b: schemas.BudgetCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Add budget for the logged-in user."""
    return crud.create_budget(db, b, current_user.user_ID)


@app.get("/budgets", response_model=list[schemas.BudgetOut])
def list_budgets(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Get all budgets for current user."""
    return crud.list_budgets_by_user(db, current_user.user_ID)


@app.delete("/budgets/{bid}")
def delete_budget(
    bid: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Delete budget (only if owned by user)."""
    b = crud.get_budget_by_id(db, bid)
    if not b or b.user_ID != current_user.user_ID:
        raise HTTPException(status_code=404, detail="Budget not found")
    crud.delete_budget(db, bid)
    return {"detail": "Budget deleted"}


# =====================================================
#                REPORTS (User-Specific)
# =====================================================

@app.get("/reports/spending_by_category", response_model=list[schemas.ReportOut])
def spending_by_category(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Report spending by category for logged-in user."""
    rows = crud.spending_by_category_for_user(db, current_user.user_ID)
    return [{"category": r[0], "total": float(r[1])} for r in rows]


@app.get("/reports/total_spent")
def total_spent(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Report total expense for logged-in user."""
    total = crud.total_expense_for_user(db, current_user.user_ID)
    return {"user": current_user.user_name, "total_spent": float(total or 0.0)}


# =====================================================
#                ROOT
# =====================================================

@app.get("/")
def root():
    return {"message": "Expense Tracker API is running 🚀"}
