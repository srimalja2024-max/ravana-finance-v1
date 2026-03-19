import streamlit as st
import pandas as pd
import os
from datetime import datetime
import plotly.express as px
from streamlit_option_menu import option_menu

# --- ⚙️ GLOBAL CONFIG ---
st.set_page_config(page_title="Ravana Finance Pro", layout="wide")

st.markdown("""
<style>
    .stApp { background-color: #F0F2F6; }
    [data-testid="stSidebar"] { background-color: #E2E6ED !important; }
    .stTextInput input, .stNumberInput input, .stSelectbox div[data-baseweb="select"] {
        background-color: white !important; border-radius: 8px !important; color: black !important;
    }
    .blue-header { background-color: #0066FF; padding: 15px; border-radius: 10px; color: white; text-align: center; margin-bottom: 20px; }
    .sidebar-acc-box { background-color: white; padding: 10px; border-radius: 8px; margin-bottom: 5px; border: 1px solid #DDE1E7; }
    .total-balance-box { background-color: #0066FF; color: white; padding: 12px; border-radius: 8px; margin-top: 10px; text-align: center; }
    .list-total-box { background-color: #ffffff; padding: 10px; border-radius: 8px; border-left: 5px solid #0066FF; margin-bottom: 15px; }
</style>
""", unsafe_allow_html=True)

DB_FOLDER = "ravana_data"
if not os.path.exists(DB_FOLDER):
    os.makedirs(DB_FOLDER)

# --- 🛠️ HELPER FUNCTIONS ---
def load_data(name):
    path = os.path.join(DB_FOLDER, f"{name}.csv")
    if os.path.exists(path):
        df_temp = pd.read_csv(path)
        if 'Sub_Category' not in df_temp.columns:
            df_temp['Sub_Category'] = ""
            df_temp.to_csv(path, index=False)
        return df_temp
    return pd.DataFrame(columns=["ID", "DateTime", "Category", "Sub_Category", "Account", "To_Account", "Type", "Amount"])

def load_meta(name):
    path = os.path.join(DB_FOLDER, f"{name}_meta.csv")
    if os.path.exists(path):
        return pd.read_csv(path)

    default_cats = [
        ["Food 🍔", "Category"], ["Vegetable 🥗", "Category"], ["Fruit 🍎", "Category"],
        ["Fuel ⛽", "Category"], ["Shopping 🛒", "Category"], ["Beauty 💄", "Category"],
        ["Telephone 📞", "Category"], ["Transportation 🚗", "Category"], ["Social 🌐", "Category"],
        ["Clothing 👗", "Category"], ["Health ❤️", "Category"], ["Housing 🏠", "Category"],
        ["Repair 🛠️", "Category"], ["Personal Insurance 🛡️", "Category"], ["Cash Contributions 💵", "Category"],
        ["Apparel & Services 👕", "Category"], ["Education 🎓", "Category"], ["Electronic ⚡", "Category"], ["Gift 🎁", "Category"]
    ]

    df_meta = pd.DataFrame([["Cash", "Account"], ["Bank", "Account"]] + default_cats, columns=["Name", "Type"])
    df_meta.to_csv(path, index=False)
    return df_meta

# --- CLEAN TRANSFERS ---
def clean_invalid_transfers(df_in, acc_list, p_name):
    temp_df = df_in.copy()
    changed = False

    while True:
        loop_changed = False
        for acc in acc_list:
            inc = temp_df[(temp_df['Account'] == acc) & (temp_df['Type'] == 'Income')]['Amount'].sum()
            t_in = temp_df[(temp_df['To_Account'] == acc) & (temp_df['Type'] == 'Transfer')]['Amount'].sum()
            exp = temp_df[(temp_df['Account'] == acc) & (temp_df['Type'] == 'Expense')]['Amount'].sum()
            t_out = temp_df[(temp_df['Account'] == acc) & (temp_df['Type'] == 'Transfer')]['Amount'].sum()

            current_bal = (inc + t_in) - (exp + t_out)

            if current_bal < 0:
                transfers_from_acc = temp_df[(temp_df['Account'] == acc) & (temp_df['Type'] == 'Transfer')]
                if not transfers_from_acc.empty:
                    last_id = transfers_from_acc.iloc[-1]['ID']
                    temp_df = temp_df[temp_df['ID'] != last_id]
                    loop_changed = True
                    changed = True
                    break

        if not loop_changed:
            break

    if changed:
        temp_df.to_csv(os.path.join(DB_FOLDER, f"{p_name}.csv"), index=False)

    return temp_df

# ---------------- UI STATE ----------------
if "active_p" not in st.session_state:
    st.session_state.active_p = None

# ---------------- HOME ----------------
if st.session_state.active_p is None:
    st.title("🏠 Ravana Finance Hub")

    p_input = st.text_input("Project Name")

    if st.button("Open Project"):
        if p_input:
            st.session_state.active_p = p_input
            load_meta(p_input)
            st.rerun()

# ---------------- MAIN ----------------
else:
    p_name = st.session_state.active_p
    df = load_data(p_name)
    meta = load_meta(p_name)

    acc_list = meta[meta["Type"] == "Account"]["Name"].tolist()
    cat_list = meta[meta["Type"] == "Category"]["Name"].tolist()

    df = clean_invalid_transfers(df, acc_list, p_name)

    if st.sidebar.button("Back"):
        st.session_state.active_p = None
        st.rerun()

    st.markdown(f'<div class="blue-header"><h1>{p_name} Dashboard</h1></div>', unsafe_allow_html=True)

    selected = option_menu(None, ["Transactions", "Insights", "Accounts"], orientation="horizontal")

    if selected == "Transactions":
        st.dataframe(df)

    elif selected == "Insights":
        if not df.empty:
            fig = px.pie(df[df["Type"] != "Transfer"], names="Category", values="Amount")
            st.plotly_chart(fig)

    elif selected == "Accounts":
        st.write("Accounts view")
