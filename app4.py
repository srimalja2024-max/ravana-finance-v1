import streamlit as st import pandas as pd import os from datetime import datetime import plotly.express as px from streamlit_option_menu import option_menu

------------------------------

GLOBAL CONFIG

------------------------------

st.set_page_config( page_title="Ravana Finance Pro", layout="wide", page_icon="💰" )

------------------------------

DARK MODE TOGGLE

------------------------------

if "dark_mode" not in st.session_state: st.session_state.dark_mode = False

st.sidebar.header("Settings") dark_toggle = st.sidebar.toggle("Dark Mode", value=st.session_state.dark_mode) st.session_state.dark_mode = dark_toggle

------------------------------

UI STYLES

------------------------------

st.markdown(f"""

<style>
.stApp {{
    background: {'#0f172a' if st.session_state.dark_mode else 'linear-gradient(135deg, #eef2f7, #e3e9f2)'};
    color: {'white' if st.session_state.dark_mode else 'black'};
}}

[data-testid="stSidebar"] {{
    background: {'#020617' if st.session_state.dark_mode else '#E2E6ED'} !important;
    color: white;
}}

[data-testid="stSidebar"] * {{
    color: white !important;
}}

.blue-header {{
    background: {'linear-gradient(90deg, #0ea5e9, #0284c7)' if st.session_state.dark_mode else 'linear-gradient(90deg, #2563eb, #1d4ed8)'};
    padding: 20px;
    border-radius: 15px;
    color: white;
    text-align: center;
    margin-bottom: 20px;
}}

.sidebar-acc-box {{
    background: rgba(255,255,255,0.08);
    padding: 10px;
    border-radius: 8px;
    margin-bottom: 5px;
}}

.total-balance-box {{
    background: {'#22c55e' if st.session_state.dark_mode else '#0066FF'};
    color: white;
    padding: 12px;
    border-radius: 8px;
    margin-top: 10px;
    text-align: center;
}}

.list-total-box {{
    background: {'#1e293b' if st.session_state.dark_mode else '#ffffff'};
    padding: 10px;
    border-radius: 8px;
    border-left: 5px solid #0066FF;
    margin-bottom: 15px;
}}

.stButton > button {{
    border-radius: 10px !important;
    background: linear-gradient(135deg, #2563eb, #1d4ed8);
    color: white;
}}

.stTextInput input,
.stNumberInput input,
.stSelectbox div[data-baseweb="select"] {{
    border-radius: 8px !important;
}}

</style>""", unsafe_allow_html=True)

------------------------------

DATA SETUP

------------------------------

DB_FOLDER = "ravana_data" if not os.path.exists(DB_FOLDER): os.makedirs(DB_FOLDER)

------------------------------

HELPER FUNCTIONS

------------------------------

def load_data(name): path = os.path.join(DB_FOLDER, f"{name}.csv") if os.path.exists(path): df_temp = pd.read_csv(path) if 'Sub_Category' not in df_temp.columns: df_temp['Sub_Category'] = "" df_temp.to_csv(path, index=False) return df_temp return pd.DataFrame(columns=["ID", "DateTime", "Category", "Sub_Category", "Account", "To_Account", "Type", "Amount"])

def load_meta(name): path = os.path.join(DB_FOLDER, f"{name}_meta.csv") if os.path.exists(path): return pd.read_csv(path) default_cats = [ ["Food 🍔", "Category"], ["Vegetable 🥗", "Category"], ["Fruit 🍎", "Category"], ["Fuel ⛽", "Category"], ["Shopping 🛒", "Category"], ["Beauty 💄", "Category"], ["Telephone 📞", "Category"], ["Transportation 🚗", "Category"], ["Social 🌐", "Category"], ["Clothing 👗", "Category"], ["Health ❤️", "Category"], ["Housing 🏠", "Category"], ["Repair 🛠️", "Category"], ["Personal Insurance 🛡️", "Category"], ["Cash Contributions 💵", "Category"], ["Apparel & Services 👕", "Category"], ["Education 🎓", "Category"], ["Electronic ⚡", "Category"], ["Gift 🎁", "Category"] ] df_meta = pd.DataFrame([["Cash", "Account"], ["Bank", "Account"]] + default_cats, columns=["Name", "Type"]) df_meta.to_csv(path, index=False) return df_meta

def clean_invalid_transfers(df_in, acc_list, p_name): temp_df = df_in.copy() changed = False while True: loop_changed = False for acc in acc_list: inc = temp_df[(temp_df['Account'] == acc) & (temp_df['Type'] == 'Income')]['Amount'].sum() t_in = temp_df[(temp_df['To_Account'] == acc) & (temp_df['Type'] == 'Transfer')]['Amount'].sum() exp = temp_df[(temp_df['Account'] == acc) & (temp_df['Type'] == 'Expense')]['Amount'].sum() t_out = temp_df[(temp_df['Account'] == acc) & (temp_df['Type'] == 'Transfer')]['Amount'].sum() current_bal = (inc + t_in) - (exp + t_out) if current_bal < 0: transfers_from_acc = temp_df[(temp_df['Account'] == acc) & (temp_df['Type'] == 'Transfer')] if not transfers_from_acc.empty: last_id = transfers_from_acc.iloc[-1]['ID'] temp_df = temp_df[temp_df['ID'] != last_id] loop_changed = True changed = True break if not loop_changed: break if changed: temp_df.to_csv(os.path.join(DB_FOLDER, f"{p_name}.csv"), index=False) return temp_df

------------------------------

SESSION INIT

------------------------------

if "active_p" not in st.session_state: st.session_state.active_p = None

------------------------------

HOME PAGE

------------------------------

if st.session_state.active_p is None: st.title("🏠 Ravana Finance Hub")

p_input = st.text_input("Project Name")
if st.button("Open Project"):
    if p_input:
        st.session_state.active_p = p_input
        load_meta(p_input)
        st.rerun()

st.subheader("Saved Projects")
projs = [f.replace("_meta.csv", "") for f in os.listdir(DB_FOLDER) if f.endswith("_meta.csv")]
for p in projs:
    if st.button(p):
        st.session_state.active_p = p
        st.rerun()

------------------------------

MAIN APP

------------------------------

else: p_name = st.session_state.active_p df = load_data(p_name) meta = load_meta(p_name)

acc_list = meta[meta["Type"] == "Account"]["Name"].tolist()
cat_list = meta[meta["Type"] == "Category"]["Name"].tolist()

df = clean_invalid_transfers(df, acc_list, p_name)

if st.sidebar.button("Back"):
    st.session_state.active_p = None
    st.rerun()

st.markdown(f'<div class="blue-header"><h1>{p_name} Dashboard</h1></div>', unsafe_allow_html=True)

selected = option_menu(None, ["Transactions", "Insights", "Accounts"], orientation="horizontal")

if selected == "Transactions":
    st.write("Transactions section")

elif selected == "Insights":
    st.write("Insights section")

elif selected == "Accounts":
    st.write("Accounts section")
