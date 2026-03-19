import streamlit as st
import pandas as pd
import os
from datetime import datetime
import plotly.express as px
from streamlit_option_menu import option_menu

# ------------------------------
# CONFIG
# ------------------------------
st.set_page_config(
    page_title="Ravana Finance Pro",
    layout="wide",
    page_icon="💰"
)

# ------------------------------
# DARK MODE TOGGLE
# ------------------------------
if "dark_mode" not in st.session_state:
    st.session_state.dark_mode = False

st.sidebar.header("Settings")
dark_toggle = st.sidebar.toggle("Dark Mode", value=st.session_state.dark_mode)
st.session_state.dark_mode = dark_toggle

# ------------------------------
# STYLES
# ------------------------------
st.markdown(f"""
<style>
.stApp {{
    background: {'#0f172a' if st.session_state.dark_mode else '#eef2f7'};
    color: {'white' if st.session_state.dark_mode else 'black'};
}}

[data-testid="stSidebar"] {{
    background: {'#020617' if st.session_state.dark_mode else '#e2e6ed'} !important;
}}

.blue-header {{
    background: linear-gradient(90deg, #2563eb, #1d4ed8);
    padding: 20px;
    border-radius: 15px;
    color: white;
    text-align: center;
    margin-bottom: 20px;
}}

.stButton > button {{
    border-radius: 10px !important;
    background: linear-gradient(135deg, #2563eb, #1d4ed8);
    color: white;
}}
</style>
""", unsafe_allow_html=True)

# ------------------------------
# DATA SETUP
# ------------------------------
DB_FOLDER = "ravana_data"
os.makedirs(DB_FOLDER, exist_ok=True)

# ------------------------------
# LOAD DATA
# ------------------------------
def load_data(name):
    path = os.path.join(DB_FOLDER, f"{name}.csv")
    if os.path.exists(path):
        return pd.read_csv(path)
    return pd.DataFrame(columns=["ID", "DateTime", "Category", "Account", "Type", "Amount"])

def save_data(name, df):
    path = os.path.join(DB_FOLDER, f"{name}.csv")
    df.to_csv(path, index=False)

# ------------------------------
# SESSION INIT
# ------------------------------
if "project" not in st.session_state:
    st.session_state.project = None

# ------------------------------
# HOME
# ------------------------------
if st.session_state.project is None:
    st.title("🏠 Ravana Finance Hub")

    project_name = st.text_input("Enter Project Name")

    if st.button("Open Project"):
        if project_name:
            st.session_state.project = project_name
            st.rerun()

    st.subheader("Existing Projects")

    projects = [f.replace(".csv", "") for f in os.listdir(DB_FOLDER) if f.endswith(".csv")]

    for p in projects:
        if st.button(p):
            st.session_state.project = p
            st.rerun()

# ------------------------------
# MAIN APP
# ------------------------------
else:
    project = st.session_state.project
    st.markdown(f'<div class="blue-header"><h2>{project} Dashboard</h2></div>', unsafe_allow_html=True)

    df = load_data(project)

    if st.sidebar.button("⬅ Back"):
        st.session_state.project = None
        st.rerun()

    menu = option_menu(
        menu_title=None,
        options=["Transactions", "Add Transaction", "Analytics"],
        orientation="horizontal"
    )

    # --------------------------
    # ADD TRANSACTION
    # --------------------------
    if menu == "Add Transaction":
        st.subheader("➕ Add Transaction")

        t_type = st.selectbox("Type", ["Income", "Expense"])
        category = st.text_input("Category")
        account = st.text_input("Account")
        amount = st.number_input("Amount", min_value=0.0)

        if st.button("Save"):
            new_row = {
                "ID": len(df) + 1,
                "DateTime": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "Category": category,
                "Account": account,
                "Type": t_type,
                "Amount": amount
            }
            df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
            save_data(project, df)
            st.success("Saved!")

    # --------------------------
    # TRANSACTIONS VIEW
    # --------------------------
    elif menu == "Transactions":
        st.subheader("📄 Transactions")
        st.dataframe(df, use_container_width=True)

    # --------------------------
    # ANALYTICS
    # --------------------------
    elif menu == "Analytics":
        st.subheader("📊 Analytics")

        if not df.empty:
            fig = px.bar(df, x="Category", y="Amount", color="Type")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No data available")
