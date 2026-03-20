import streamlit as st
import pandas as pd
import os
from datetime import datetime
import plotly.express as px
from streamlit_option_menu import option_menu

# --- ⚙️ GLOBAL CONFIG ---
st.set_page_config(page_title="Ravana Finance Pro", layout="wide")

# UI එක ලස්සන කිරීමට අවශ්‍ය CSS මෙහි අලුත් කර ඇත
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
    
    html, body, [data-testid="stAppViewContainer"] {
        font-family: 'Inter', sans-serif;
        background-color: #f8f9fa;
    }
    
    .stApp { background-color: #f8f9fa; }
    
    /* Sidebar Design */
    [data-testid="stSidebar"] {
        background-color: #ffffff !important;
        border-right: 1px solid #e0e0e0;
    }
    
    /* Headers */
    .blue-header {
        background: linear-gradient(90deg, #0052D4 0%, #4364F7 50%, #6FB1FC 100%);
        padding: 2rem;
        border-radius: 15px;
        color: white;
        text-align: center;
        margin-bottom: 25px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    }
    
    /* Balance Boxes */
    .sidebar-acc-box {
        background-color: #f1f3f5;
        padding: 15px;
        border-radius: 12px;
        margin-bottom: 10px;
        border: 1px solid #e9ecef;
        transition: transform 0.2s;
    }
    .sidebar-acc-box:hover {
        transform: translateY(-2px);
    }
    
    .total-balance-box {
        background: #212529;
        color: #ffffff;
        padding: 20px;
        border-radius: 12px;
        margin-top: 15px;
        text-align: center;
        box-shadow: 0 4px 10px rgba(0,0,0,0.2);
    }
    
    /* List Items */
    .list-total-box {
        background-color: #ffffff;
        padding: 15px;
        border-radius: 12px;
        border-left: 6px solid #4364F7;
        margin-bottom: 20px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
    }

    /* Input Fields */
    .stTextInput input, .stNumberInput input, .stSelectbox div[data-baseweb="select"] {
        border-radius: 10px !important;
    }
</style>
""", unsafe_allow_html=True)

DB_FOLDER = "ravana_data"
if not os.path.exists(DB_FOLDER): os.makedirs(DB_FOLDER)

# --- 🛠️ HELPER FUNCTIONS (No Logic Changes) ---
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
    if os.path.exists(path): return pd.read_csv(path)
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
        if not loop_changed: break
    if changed:
        temp_df.to_csv(os.path.join(DB_FOLDER, f"{p_name}.csv"), index=False)
    return temp_df

if "active_p" not in st.session_state: st.session_state.active_p = None

# ==========================================
# 1️⃣ PART: HOME
# ==========================================
if st.session_state.active_p is None:
    st.markdown('<div class="blue-header"><h1>Ravana Finance Hub</h1><p>Smart Financial Management</p></div>', unsafe_allow_html=True)
    with st.container():
        p_input = st.text_input("Project Name", placeholder="Enter your project name (e.g., MyShop)")
        if st.button("🚀 Open or Create Project", use_container_width=True):
            if p_input: st.session_state.active_p = p_input; load_meta(p_input); st.rerun()
    st.divider()
    st.subheader("📂 Your Saved Projects")
    projs = [f.replace("_meta.csv", "") for f in os.listdir(DB_FOLDER) if f.endswith("_meta.csv")]
    if not projs: st.info("No projects yet. Create one above!")
    for p in projs:
        if st.button(f"📊 {p}", use_container_width=True): st.session_state.active_p = p; st.rerun()

# ==========================================
# 2️⃣ PART: DASHBOARD
# ==========================================
else:
    p_name = st.session_state.active_p
    df = load_data(p_name)
    meta = load_meta(p_name)
    acc_list = meta[meta["Type"] == "Account"]["Name"].tolist()
    cat_list = meta[meta["Type"] == "Category"]["Name"].tolist()
    df = clean_invalid_transfers(df, acc_list, p_name)

    # Sidebar Navigation
    if st.sidebar.button("🏠 Back to Home Hub", use_container_width=True):
        st.session_state.active_p = None; st.rerun()
    st.sidebar.divider()
    
    st.sidebar.subheader("➕ New Entry")
    t_type_map = {"Expense 💸": "Expense", "Income 💰": "Income", "Transfer 🔄": "Transfer"}
    t_type_display = st.sidebar.selectbox("Transaction Type", list(t_type_map.keys()))
    t_type = t_type_map[t_type_display]

    f_acc = st.sidebar.selectbox("Account", [f"💳 {acc}" for acc in acc_list]).replace("💳 ", "")
    t_acc = st.sidebar.selectbox("To Account", [f"💳 {acc}" for acc in acc_list]).replace("💳 ", "") if t_type == "Transfer" else None
    
    if t_type == "Income":
        t_cat, c_cat = "Income", ""
    elif t_type == "Transfer":
        t_cat, c_cat = "Transfer", ""
    else:
        t_cat = st.sidebar.selectbox("Category", cat_list + ["+ New Category"])
        c_cat = st.sidebar.text_input("New Category Name") if t_cat == "+ New Category" else ""
    
    sub_cat = st.sidebar.text_input("Note / Details") if t_type != "Transfer" else ""

    with st.sidebar.form("entry_form", clear_on_submit=True):
        amt = st.number_input("Amount (LKR)", min_value=0.0, step=100.0)
        if st.form_submit_button("✅ Save Transaction", use_container_width=True):
            if amt > 0:
                fin_cat = c_cat if t_cat == "+ New Category" else t_cat
                if t_cat == "+ New Category" and c_cat:
                    meta = pd.concat([meta, pd.DataFrame([[c_cat, "Category"]], columns=meta.columns)])
                    meta.to_csv(os.path.join(DB_FOLDER, f"{p_name}_meta.csv"), index=False)
                new_row = {"ID": int(datetime.now().timestamp()*1000), "DateTime": datetime.now().strftime("%Y-%m-%d %H:%M"), "Category": fin_cat, "Sub_Category": sub_cat, "Account": f_acc, "To_Account": t_acc, "Type": t_type, "Amount": amt}
                pd.concat([df, pd.DataFrame([new_row])]).to_csv(os.path.join(DB_FOLDER, f"{p_name}.csv"), index=False); st.rerun()

    st.sidebar.divider()
    st.sidebar.subheader("💰 Balance")
    actual_balances = {acc: 0.0 for acc in acc_list}
    total_net = 0
    for acc in acc_list:
        inc = df[(df['Account'] == acc) & (df['Type'] == 'Income')]['Amount'].sum() + df[(df['To_Account'] == acc) & (df['Type'] == 'Transfer')]['Amount'].sum()
        exp = df[(df['Account'] == acc) & (df['Type'] == 'Expense')]['Amount'].sum() + df[(df['Account'] == acc) & (df['Type'] == 'Transfer')]['Amount'].sum()
        bal = inc - exp
        actual_balances[acc] = bal
        total_net += bal
        st.sidebar.markdown(f'<div class="sidebar-acc-box"><b>{acc}</b><br><span style="color: #0052D4; font-weight: bold;">Rs. {max(0, bal):,.0f}</span></div>', unsafe_allow_html=True)
    st.sidebar.markdown(f'<div class="total-balance-box"><small>Total Net Worth</small><br><span style="font-size: 20px; font-weight: bold;">Rs. {total_net:,.0f}</span></div>', unsafe_allow_html=True)

    # Main Dashboard UI
    st.markdown(f'<div class="blue-header"><h1>📊 {p_name}</h1></div>', unsafe_allow_html=True)
    
    selected = option_menu(
        menu_title=None, 
        options=["Transactions", "Insights", "Accounts"], 
        icons=["list-task", "pie-chart", "wallet2"],
        orientation="horizontal",
        styles={
            "container": {"padding": "0!important", "background-color": "#ffffff", "border-radius": "10px", "margin-bottom": "20px"},
            "nav-link": {"font-size": "18px", "text-align": "center", "margin": "0px", "--hover-color": "#f1f3f5"},
            "nav-link-selected": {"background-color": "#4364F7", "color": "white"},
        }
    )

    if selected == "Transactions":
        st.markdown("<br>", unsafe_allow_html=True)
        t1, t2, t3, t4 = st.tabs(["📝 All History", "💸 Expenses", "💰 Income", "🔄 Transfers"])
        
        def show_list(filter_type=None, exclude_transfer=True, tab_name=""):
            target_df = df[df['Type'] == filter_type] if filter_type else (df[df['Type'] != 'Transfer'] if exclude_transfer else df)
            list_sum = target_df['Amount'].sum()
            st.markdown(f'<div class="list-total-box"><small>Total Selected</small><br><span style="font-size: 22px; font-weight: bold; color: #4364F7;">Rs. {list_sum:,.0f}</span></div>', unsafe_allow_html=True)
            if target_df.empty: st.info("No records to show."); return
            for idx, row in target_df.copy().iloc[::-1].iterrows():
                with st.container(border=True):
                    c1, c2, c3 = st.columns([4, 2, 0.5])
                    color = "#28a745" if row['Type'] == 'Income' else ("#007bff" if row['Type'] == 'Transfer' else "#dc3545")
                    detail = f" | <small>{row['Sub_Category']}</small>" if row['Sub_Category'] else ""
                    label = f"🔄 {row['Account']} ➔ {row['To_Account']}" if row['Type'] == 'Transfer' else f"**{row['Category']}**{detail} <br><small>via {row['Account']}</small>"
                    c1.markdown(f"{label}<br><small style='color:grey;'>{row['DateTime']}</small>", unsafe_allow_html=True)
                    c2.markdown(f"<h3 style='color:{color}; text-align:right; margin:0;'>{row['Amount']:,.0f}</h3>", unsafe_allow_html=True)
                    if c3.button("🗑️", key=f"del_{tab_name}_{row['ID']}"):
                        df[df['ID'] != row['ID']].to_csv(os.path.join(DB_FOLDER, f"{p_name}.csv"), index=False); st.rerun()
        
        with t1: show_list(exclude_transfer=True, tab_name="all")
        with t2: show_list("Expense", tab_name="exp")
        with t3: show_list("Income", tab_name="inc")
        with t4: show_list("Transfer", tab_name="tra")

    elif selected == "Insights":
        inc_s = df[df['Type'] == 'Income']['Amount'].sum()
        exp_s = df[df['Type'] == 'Expense']['Amount'].sum()
        it1, it2 = st.tabs(["Summary Statistics", "Category Breakdown"])
        with it1:
            c_pie, c_met = st.columns([2, 1])
            with c_pie:
                if inc_s > 0 or exp_s > 0:
                    fig = px.pie(values=[inc_s, exp_s], names=['Income', 'Expense'], hole=0.6, color_discrete_sequence=['#28a745', '#dc3545'])
                    st.plotly_chart(fig, use_container_width=True)
            with c_met:
                st.metric("Total Income", f"Rs. {inc_s:,.0f}")
                st.metric("Total Expense", f"Rs. {exp_s:,.0f}", delta=f"-{exp_s:,.0f}", delta_color="inverse")
                st.metric("Net Savings", f"Rs. {(inc_s-exp_s):,.0f}")
        with it2:
            analysis_df = df[df['Type'] != 'Transfer']
            if not analysis_df.empty:
                cat_sum = analysis_df.groupby(['Category', 'Type'])['Amount'].sum().reset_index()
                fig2 = px.bar(cat_sum, x='Category', y='Amount', color='Type', barmode='group', color_discrete_map={'Income':'#28a745', 'Expense':'#dc3545'})
                st.plotly_chart(fig2, use_container_width=True)

    elif selected == "Accounts":
        cols = st.columns(2)
        for i, acc in enumerate(acc_list):
            with cols[i % 2]:
                bal = max(0, actual_balances[acc])
                st.info(f"### {acc}\n**Current Balance: Rs. {bal:,.0f}**")

    # Sidebar account management (No logic change)
    with st.sidebar.expander("🛠️ Advanced Settings"):
        n_acc = st.text_input("New Account Name")
        if st.button("Add Account"):
            if n_acc and n_acc not in acc_list:
                pd.concat([meta, pd.DataFrame([[n_acc, "Account"]], columns=meta.columns)]).to_csv(os.path.join(DB_FOLDER, f"{p_name}_meta.csv"), index=False); st.rerun()
