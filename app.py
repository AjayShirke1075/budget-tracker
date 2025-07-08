import streamlit as st
import sqlite3
import pandas as pd
import datetime
import matplotlib.pyplot as plt
import plotly.express as px
from db import init_db, add_entry, get_data, create_user, check_user

# Streamlit Config
st.set_page_config(page_title="Budget Tracker", layout="wide")

# Initialize DB
init_db()

# --------------------- Login System ---------------------
def login():
    st.subheader("🔐 Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        if check_user(username, password):
            st.session_state.user = username
            st.success("Login successful!")
            st.rerun()
        else:
            st.error("Invalid username or password.")

def register():
    st.subheader("🧾 Register")
    username = st.text_input("Choose Username")
    password = st.text_input("Choose Password", type="password")
    if st.button("Register"):
        if create_user(username, password):
            st.success("User created successfully. Please login.")
            st.session_state.register = False
            st.rerun()
        else:
            st.error("Username already exists!")

# --------------------- Budget App ---------------------
def budget_app(user):
    st.title("📊 Budget Tracker Dashboard")

    # --- Add Entry
    st.subheader("➕ Add Entry")
    with st.form("entry_form", clear_on_submit=True):
        date = st.date_input("Date", datetime.date.today())
        entry_type = st.selectbox("Type", ["Income", "Expense"])
        description = st.text_input("Description")
        amount = st.number_input("Amount", min_value=0.0)
        submitted = st.form_submit_button("Add")
        if submitted:
            add_entry(user, date.strftime("%Y-%m-%d"), entry_type, description, amount)
            st.success("Entry added successfully!")

    # --- Fetch Data
    df = get_data(user)
    if df.empty:
        st.info("No data yet.")
        return

    df["date"] = pd.to_datetime(df["date"])

    # --- Filter by Month
    st.subheader("📅 Filter by Month")
    months = df['date'].dt.to_period('M').astype(str).unique()
    selected_month = st.selectbox("Choose Month", months)
    filtered_df = df[df['date'].dt.to_period('M').astype(str) == selected_month]

    # --- Export to Excel
    st.download_button("📥 Export to Excel", data=filtered_df.to_csv(index=False).encode("utf-8"), file_name="budget_data.csv")

    # --- Show Data
    st.dataframe(filtered_df, use_container_width=True)

    # --- Summary
    summary = filtered_df.groupby("type")["amount"].sum().reset_index()
    income = summary[summary["type"] == "Income"]["amount"].sum()
    expense = summary[summary["type"] == "Expense"]["amount"].sum()
    profit = income - expense

    st.metric("💰 Total Income", f"₹{income:,.2f}")
    st.metric("💸 Total Expense", f"₹{expense:,.2f}")
    st.metric("📈 Profit / Loss", f"₹{profit:,.2f}", delta=f"{profit:,.2f}")

    # --- Charts Layout
    st.subheader("📊 Visual Insights")
    chart_col1, chart_col2 = st.columns(2)

    with chart_col1:
        pie_chart = px.pie(summary, names='type', values='amount', title="Expense Breakdown")
        st.plotly_chart(pie_chart, use_container_width=True)

    with chart_col2:
        bar_chart = px.bar(filtered_df, x='date', y='amount', color='type', title="Income vs Expense")
        st.plotly_chart(bar_chart, use_container_width=True)

    # --- Profit & Loss Chart
    st.subheader("📉 Profit & Loss Overview")
    df_monthly = df.copy()
    df_monthly["month"] = df_monthly["date"].dt.to_period("M").astype(str)
    pivot_df = df_monthly.pivot_table(index="month", columns="type", values="amount", aggfunc="sum", fill_value=0)
    pivot_df["Profit"] = pivot_df.get("Income", 0) - pivot_df.get("Expense", 0)

    st.line_chart(pivot_df[["Profit"]])

    # --- Forecasting with AI
    st.subheader("🤖 Forecast Future Spending (AI-based)")
    forecast_df = df.copy()
    forecast_df = forecast_df[df["type"] == "Expense"]
    forecast_df = forecast_df.groupby("date")["amount"].sum().reset_index()
    forecast_df = forecast_df.set_index("date").asfreq("D", fill_value=0)
    forecast_df["rolling"] = forecast_df["amount"].rolling(7).mean()
    st.line_chart(forecast_df[["amount", "rolling"]])

# -------------------- Main App --------------------
def main():
    st.markdown(
        """
        <style>
        body {
            background-color: #111;
            color: white;
        }
        .stApp {
            background-color: #1e1e1e;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    if "user" not in st.session_state:
        st.session_state.user = None
    if "register" not in st.session_state:
        st.session_state.register = False

    if st.session_state.user:
        budget_app(st.session_state.user)
    elif st.session_state.register:
        register()
    else:
        st.sidebar.title("👋 Welcome")
        if st.sidebar.button("Register"):
            st.session_state.register = True
            st.rerun()
        login()

if __name__ == "__main__":
    main()
