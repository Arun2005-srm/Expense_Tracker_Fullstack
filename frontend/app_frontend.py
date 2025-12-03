import streamlit as st
import requests
import pandas as pd
from datetime import date
from typing import Optional


st.cache_data.clear()


API_URL = "http://127.0.0.1:8000"
TIMEOUT = 10

st.set_page_config(page_title="Expense Tracker", layout="wide")

# -------------------------
# Session initialization
# -------------------------
if "token" not in st.session_state:
    st.session_state["token"] = None
if "username" not in st.session_state:
    st.session_state["username"] = None
if "user_id" not in st.session_state:
    st.session_state["user_id"] = None
if "categories" not in st.session_state:
    st.session_state["categories"] = []
if "payment_methods" not in st.session_state:
    st.session_state["payment_methods"] = []

# -------------------------
# Helpers
# -------------------------
def _headers(token: Optional[str]):
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    return headers

def try_get(url, token=None):
    try:
        return requests.get(url, headers=_headers(token), timeout=TIMEOUT)
    except Exception as e:
        return {"error": True, "details": str(e)}

def try_post(url, data, token=None):
    try:
        return requests.post(url, json=data, headers=_headers(token), timeout=TIMEOUT)
    except Exception as e:
        return {"error": True, "details": str(e)}

def try_put(url, data, token=None):
    try:
        return requests.put(url, json=data, headers=_headers(token), timeout=TIMEOUT)
    except Exception as e:
        return {"error": True, "details": str(e)}

def try_delete(url, token=None):
    try:
        return requests.delete(url, headers=_headers(token), timeout=TIMEOUT)
    except Exception as e:
        return {"error": True, "details": str(e)}

# -------------------------
# Login / Signup
# -------------------------
def login_signup_page():
    st.title("💰 Expense Tracker")
    st.caption("Manage your expenses, budgets, and reports easily.")

    col1, col2 = st.columns(2)

    # --- SIGNUP ---
    with col1:
        st.subheader("Create Account")
        with st.form("signup_form"):
            s_user = st.text_input("Username*", key="signup_user")
            s_pw = st.text_input("Password*", type="password", key="signup_pw")
            s_email = st.text_input("Email*", key="signup_email")
            s_contact1 = st.text_input("Contact Number 1*", key="signup_c1")
            s_contact2 = st.text_input("Contact Number 2 (Optional)", key="signup_c2")
            submitted = st.form_submit_button("Sign Up")

            if submitted:
                if not s_user or not s_pw or not s_email or not s_contact1:
                    st.warning("Please fill all required fields.")
                else:
                    payload = {
                        "user_name": s_user,
                        "password": s_pw,
                        "user_email": s_email,
                        "contact_num_1": s_contact1,
                        "contact_num_2": s_contact2 or None,
                    }
                    r = requests.post(f"{API_URL}/auth/register", json=payload, timeout=TIMEOUT)
                    if r.status_code == 200:
                        st.success("✅ Account created! Please login.")
                    else:
                        st.error(f"Signup failed: {r.text}")

    # --- LOGIN ---
    with col2:
        st.subheader("Login")
        with st.form("login_form"):
            l_user = st.text_input("Username", key="login_user")
            l_pw = st.text_input("Password", type="password", key="login_pw")
            submitted = st.form_submit_button("Login")

            if submitted:
                if not l_user or not l_pw:
                    st.warning("Please enter both username and password.")
                else:
                    payload = {"username": l_user, "password": l_pw}
                    r = requests.post(f"{API_URL}/auth/login", json=payload, timeout=TIMEOUT)
                    if r.status_code == 200:
                        data = r.json()
                        if data.get("status") == "error":
                            st.error(data.get("message", "Login failed"))
                        elif data.get("status") == "success":
                            token = data.get("access_token")
                            st.session_state["token"] = token
                            st.session_state["username"] = data.get("username")
                            st.session_state["user_id"] = data.get("user_id")
                            st.success("✅ Login successful!")
                            st.rerun()
                        else:
                            st.error("Unexpected response from server.")
                    else:
                        st.error(f"⚠️ Backend error: {r.text}")

# -------------------------
# Dashboard
# -------------------------
def dashboard_page():
    user_id = st.session_state.get("user_id")
    if not user_id:
        st.warning("User ID not found in session. Please log in again.")
        return

    st.sidebar.title(f"👋 {st.session_state['username']}")
    if st.sidebar.button("🚪 Logout"):
        for k in ["token", "username", "user_id", "categories", "payment_methods"]:
            st.session_state[k] = None if k not in ["categories", "payment_methods"] else []
        st.rerun()

    # Delete account
    with st.sidebar.expander("⚠️ Danger zone"):
        st.markdown("### Delete Account")
        st.warning("This will permanently delete your account and all related data!")
        confirm = st.text_input("Type DELETE to confirm account deletion", key="delete_confirm")
        if st.button("🗑️ Delete my account", key="delete_btn"):
            if confirm == "DELETE":
                res = try_delete(f"{API_URL}/users/{user_id}", token=st.session_state["token"])
                if not isinstance(res, dict) and res.status_code == 200:
                    st.success("✅ Account deleted successfully. Logging out...")
                    for k in ["token", "username", "user_id", "categories", "payment_methods"]:
                        st.session_state[k] = None if k not in ["categories", "payment_methods"] else []
                    st.rerun()
                else:
                    st.error(f"❌ Failed to delete account: {res.text if not isinstance(res, dict) else res['details']}")
            else:
                st.warning("Please type DELETE in the box above to confirm.")

    # Load categories & payment methods
    # Fetch categories every time
    cat_res = try_get(f"{API_URL}/categories", token=st.session_state["token"])
    if not isinstance(cat_res, dict) and cat_res.status_code == 200:
        st.session_state["categories"] = cat_res.json()

    # Fetch payment methods every time
    pm_res = try_get(f"{API_URL}/payment-methods", token=st.session_state["token"])
    if not isinstance(pm_res, dict) and pm_res.status_code == 200:
        st.session_state["payment_methods"] = pm_res.json()


    cat_options = {c["category_ID"]: c["category_name"] for c in st.session_state["categories"]}
    pm_options = {p["payment_ID"]: p["payment_type"] for p in st.session_state["payment_methods"]}

    tab1, tab2, tab3 = st.tabs(["➕ Add / Manage Expenses", "💰 Budgets", "📈 Reports"])

    # ---- Expenses tab ----
    with tab1:
        st.subheader("Add Expense")
        with st.form("add_expense", clear_on_submit=True):
            col1, col2 = st.columns(2)
            with col1:
                amount = st.number_input("Amount", min_value=0.01, step=0.01)
                category_id = st.selectbox("Category", options=list(cat_options.keys()), format_func=lambda k: cat_options[k])
            with col2:
                payment_id = st.selectbox("Payment Method", options=list(pm_options.keys()), format_func=lambda k: pm_options[k])
                exp_date = st.date_input("Date", value=date.today())
            description = st.text_area("Description")
            submitted = st.form_submit_button("Add Expense")
            if submitted:
                payload = {
                    "user_ID": user_id,
                    "category_ID": int(category_id),
                    "payment_ID": int(payment_id),
                    "amount": float(amount),
                    "description": description,
                    "date": exp_date.isoformat()
                }
                res = try_post(f"{API_URL}/expenses/add", payload, token=st.session_state["token"])
                if not isinstance(res, dict) and res.status_code in (200, 201):
                    st.success("✅ Expense added!")
                    st.rerun()
                else:
                    st.error(f"Failed to add expense. {res.text if not isinstance(res, dict) else res['details']}")
           

        st.markdown("----")
        st.subheader("Your expenses")
        exp_res = try_get(f"{API_URL}/expenses/{user_id}", token=st.session_state["token"])
        if isinstance(exp_res, dict) or exp_res.status_code != 200:
            st.info("No expenses or couldn't fetch them.")
        else:
            data = exp_res.json()
            if data:
                df = pd.DataFrame(data)
                df["date"] = pd.to_datetime(df["date"]).dt.strftime("%Y-%m-%d")
                df["category_name"] = df["category_ID"].map(cat_options)
                df["payment_name"] = df["payment_ID"].map(pm_options)
                df["amount"] = df["amount"].astype(float)
                st.dataframe(df[["expense_ID","date","amount","category_name","payment_name","description"]], use_container_width=True)

                st.subheader("📊 Total Spending")
                total_res = try_get(f"{API_URL}/reports/total-spending/{user_id}", token=st.session_state["token"])
                if not isinstance(total_res, dict) and total_res.status_code == 200:
                    st.metric("Total Spending", f"₹{total_res.json().get('total_spending',0):.2f}")

                selected = st.selectbox("Choose expense_ID to edit/delete", df["expense_ID"])
                row = df[df["expense_ID"] == selected].iloc[0]
                new_amount = st.number_input("Amount (edit)", value=float(row["amount"]))
                new_desc = st.text_area("Description (edit)", value=row.get("description",""))
                if st.button("Update Expense"):
                    payload = {"amount": float(new_amount), "description": new_desc}
                    r = try_put(f"{API_URL}/expenses/{int(selected)}", payload, token=st.session_state["token"])
                    if not isinstance(r, dict) and r.status_code == 200:
                        st.success("✅ Expense updated!")
                        st.rerun()
                if st.button("Delete Expense"):
                    r = try_delete(f"{API_URL}/expenses/{int(selected)}", token=st.session_state["token"])
                    if not isinstance(r, dict) and r.status_code == 200:
                        st.success("🗑️ Expense deleted!")
                        st.rerun()
        

    # ---- Budgets tab ----
    with tab2:
        st.subheader("Add / Manage Budgets")
        with st.form("add_budget", clear_on_submit=True):
            b_cat = st.selectbox("Category", options=list(cat_options.keys()), format_func=lambda k: cat_options[k])
            b_amt = st.number_input("Amount limit", min_value=0.01, step=0.01)
            b_start = st.date_input("Start date", value=date.today())
            b_end = st.date_input("End date", value=date.today())
            submitted = st.form_submit_button("Save Budget")
            if submitted:
                if b_end <= b_start:
                    st.error("End date must be after start date.")
                else:
                    payload = {
                        "user_ID": user_id,
                        "category_ID": int(b_cat),
                        "amount_limit": float(b_amt),
                        "start_date": b_start.isoformat(),
                        "end_date": b_end.isoformat()
                    }
                    res = try_post(f"{API_URL}/budgets/add", payload, token=st.session_state["token"])
                    if not isinstance(res, dict) and res.status_code in (200,201):
                        st.success("✅ Budget saved!")
                        st.rerun()
                    else:
                        st.error(f"Failed to create budget. {res.text if not isinstance(res, dict) else res['details']}")

        st.markdown("----")
        st.subheader("Your budgets")
        bud_res = try_get(f"{API_URL}/budgets/{user_id}", token=st.session_state["token"])
        if isinstance(bud_res, dict) or bud_res.status_code != 200:
            st.info("No budgets or couldn't fetch them.")
        else:
            budgets = bud_res.json()
            if budgets:
                dfb = pd.DataFrame(budgets)
                dfb["category_name"] = dfb["category_ID"].map(cat_options)
                st.dataframe(dfb[["budget_ID","category_name","amount_limit","start_date","end_date"]], use_container_width=True)

                sel_bid = st.selectbox("Select budget_ID to edit/delete", dfb["budget_ID"])
                row = dfb[dfb["budget_ID"] == sel_bid].iloc[0]
                new_limit = st.number_input("New amount limit", value=float(row["amount_limit"]))
                new_start = st.date_input("New start date", value=pd.to_datetime(row["start_date"]).date())
                new_end = st.date_input("New end date", value=pd.to_datetime(row["end_date"]).date())
                if st.button("Update Budget"):
                    payload = {
                        "amount_limit": float(new_limit),
                        "start_date": new_start.isoformat(),
                        "end_date": new_end.isoformat()
                    }
                    r = try_put(f"{API_URL}/budgets/{int(sel_bid)}", payload, token=st.session_state["token"])
                    if not isinstance(r, dict) and r.status_code == 200:
                        st.success("✅ Budget updated!")
                        st.rerun()
                if st.button("Delete Budget"):
                    r = try_delete(f"{API_URL}/budgets/{int(sel_bid)}", token=st.session_state["token"])
                    if not isinstance(r, dict) and r.status_code == 200:
                        st.success("🗑️ Budget deleted!")
                        st.rerun()

    # ---- Reports tab ----
    with tab3:
        st.subheader("📊 Total Spending")
        total_res = try_get(f"{API_URL}/reports/total-spending/{user_id}", token=st.session_state["token"])
        if not isinstance(total_res, dict) and total_res.status_code == 200:
            st.metric("Total Spending", f"₹{total_res.json().get('total_spending',0):.2f}")

        st.markdown("----")
        st.subheader("Spending by category")
        rep_res = try_get(f"{API_URL}/reports/spending-by-category/{user_id}", token=st.session_state["token"])
        if not isinstance(rep_res, dict) and rep_res.status_code == 200:
            data = rep_res.json()
            if data:
                rdf = pd.DataFrame(data)
                rdf["total"] = rdf["total"].astype(float)
                st.bar_chart(rdf.set_index("category_name")["total"])
            else:
                st.info("No data for reports.")
        else:
            st.info("No report data or endpoint not available.")

        st.markdown("----")
        st.subheader("📆 Monthly Spending Trend")

        monthly_res = try_get(f"{API_URL}/reports/monthly-spending/{user_id}", token=st.session_state["token"])
        if not isinstance(monthly_res, dict) and monthly_res.status_code == 200:
            data = monthly_res.json()
            if data:
                mdf = pd.DataFrame(data)

                # Convert to datetime safely
                mdf["month_dt"] = pd.to_datetime(mdf["month"], format="%Y-%m", errors="coerce")

                # Sort by datetime
                mdf = mdf.sort_values("month_dt")

                # Create readable month labels
                mdf["month_label"] = mdf["month_dt"].dt.strftime("%b %Y")

                # ✅ Ensure x-axis is ordered by datetime
                st.bar_chart(data=mdf, x="month_label", y="total", use_container_width=True)

            else:
                st.info("No monthly data yet.")
        else:
            st.warning("Couldn't fetch monthly report.")


# -------------------------
# Run app
# -------------------------
if st.session_state["token"]:
    dashboard_page()
else:
    login_signup_page()
