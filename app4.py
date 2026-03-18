import streamlit as st
import pandas as pd
import os
from datetime import datetime
import plotly.express as px

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
    /* බටන් වල පෙනුම පෝන් එකට ගැලපෙන සේ සැකසීම */
    div.stButton > button {
        width: 100%;
        border-radius: 5px;
        height: 3em;
        background-color: #0066FF;
        color: white;
    }
</style>
""", unsafe_allow_html=True)

DB_FOLDER = "ravana_data"
if not os.path.exists(DB_FOLDER): os.makedirs(DB_FOLDER)

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
if "selected_page" not in st.session_state: st.session_state.selected_page = "Transactions"

# ==========================================
# 1️⃣ PART: HOME
# ==========================================
if st.session_state.active_p is None:
    st.title("🏠 Ravana Finance Hub")
    with st.container(border=True):
        p_input = st.text_input("Project Name (New or Existing)", placeholder="Type and press Enter")
        if st.button("🚀 Open Project"):
            if p_input: st.session_state.active_p = p_input; load_meta(p_input); st.rerun()
    st.divider()
    st.subheader("📂 Saved Projects")
    projs = [f.replace("_meta.csv", "") for f in os.listdir(DB_FOLDER) if f.endswith("_meta.csv")]
    for p in projs:
        if st.button(f"📊 {p}"): st.session_state.active_p = p; st.rerun()

# ==========================================
# 2️⃣ PART: CORE LOGIC
# ==========================================
else:
    p_name = st.session_state.active_p
    df = load_data(p_name)
    meta = load_meta(p_name)
    acc_list = meta[meta["Type"] == "Account"]["Name"].tolist()
    cat_list = meta[meta["Type"] == "Category"]["Name"].tolist()
    df = clean_invalid_transfers(df, acc_list, p_name)

    if st.sidebar.button("🏠 Back to Home Page"):
        st.session_state.active_p = None; st.rerun()
    st.sidebar.divider()
    
    # --- Sidebar Transaction Entry ---
    st.sidebar.header("➕ Add Transaction")
    t_type_map = {"Expense 💸": "Expense", "Income 💰": "Income", "Transfer 🔄": "Transfer"}
    t_type_display = st.sidebar.selectbox("Type", list(t_type_map.keys()))
    t_type = t_type_map[t_type_display]
    f_acc = st.sidebar.selectbox("From Account", [f"💳 {acc}" for acc in acc_list]).replace("💳 ", "")
    t_acc = st.sidebar.selectbox("To Account", [f"💳 {acc}" for acc in acc_list]).replace("💳 ", "") if t_type == "Transfer" else None
    
    if t_type == "Income":
        t_cat, c_cat = "Income", ""
    elif t_type == "Transfer":
        t_cat, c_cat = "Transfer", ""
    else:
        t_cat = st.sidebar.selectbox("Category", cat_list + ["+ New Category"])
        c_cat = st.sidebar.text_input("Custom Category Name") if t_cat == "+ New Category" else ""
    
    sub_cat = st.sidebar.text_input("Category detail") if t_type != "Transfer" else ""

    with st.sidebar.form("left_entry_form", clear_on_submit=True):
        amt = st.number_input("Amount (LKR)", min_value=0.0, value=None, placeholder="0.00")
        if st.form_submit_button("✅ Save Data"):
            if amt is not None and amt > 0:
                fin_cat = c_cat if t_cat == "+ New Category" else t_cat
                if t_cat == "+ New Category" and c_cat:
                    meta = pd.concat([meta, pd.DataFrame([[c_cat, "Category"]], columns=meta.columns)])
                    meta.to_csv(os.path.join(DB_FOLDER, f"{p_name}_meta.csv"), index=False)
                new_row = {"ID": int(datetime.now().timestamp()*1000), "DateTime": datetime.now().strftime("%Y-%m-%d %H:%M"), "Category": fin_cat, "Sub_Category": sub_cat, "Account": f_acc, "To_Account": t_acc, "Type": t_type, "Amount": amt}
                pd.concat([df, pd.DataFrame([new_row])]).to_csv(os.path.join(DB_FOLDER, f"{p_name}.csv"), index=False); st.rerun()

    # --- Header & Navigation ---
    st.markdown(f'<div class="blue-header"><h1>📊 {p_name} Dashboard</h1></div>', unsafe_allow_html=True)
    
    # 🎯 මෙන්න මෙතන තමයි බටන් 3 එක පේළියට හදලා තියෙන්නේ
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("Transactions"): st.session_state.selected_page = "Transactions"
    with col2:
        if st.button("Insights"): st.session_state.selected_page = "Insights"
    with col3:
        if st.button("Accounts"): st.session_state.selected_page = "Accounts"

    st.divider()

    # --- PAGE LOGIC ---
    if st.session_state.selected_page == "Transactions":
        t1, t2, t3, t4 = st.tabs(["📝 All", "💸 Expense", "💰 Income", "🔄 Transfer"])
        def show_list(filter_type=None, exclude_transfer=True, tab_name=""):
            target_df = df[df['Type'] == filter_type] if filter_type else (df[df['Type'] != 'Transfer'] if exclude_transfer else df)
            list_sum = target_df['Amount'].sum()
            st.markdown(f'<div class="list-total-box"><small>Total</small><br><span style="font-size: 20px; font-weight: bold; color: #0066FF;">Rs. {list_sum:,.0f}</span></div>', unsafe_allow_html=True)
            if target_df.empty: st.info("No records found."); return
            for idx, row in target_df.copy().iloc[::-1].iterrows():
                with st.container(border=True):
                    c1, c2, c3 = st.columns([4, 1.5, 0.5])
                    color = "green" if row['Type'] == 'Income' else ("blue" if row['Type'] == 'Transfer' else "red")
                    detail_str = f" | <small>{row['Sub_Category']}</small>" if pd.notna(row['Sub_Category']) and row['Sub_Category'] != "" else ""
                    label = f"🔄 {row['Account']} ➔ {row['To_Account']}" if row['Type'] == 'Transfer' else f"**{row['Category']}**{detail_str} | {row['Account']}"
                    c1.markdown(f"{label}<br><small>{row['DateTime']}</small>", unsafe_allow_html=True)
                    c2.markdown(f"<h3 style='color:{color}; text-align:right;'>{row['Amount']:,.0f}</h3>", unsafe_allow_html=True)
                    if c3.button("🗑️", key=f"del_{tab_name}_{row['ID']}"):
                        df[df['ID'] != row['ID']].to_csv(os.path.join(DB_FOLDER, f"{p_name}.csv"), index=False); st.rerun()
        with t1: show_list(exclude_transfer=True, tab_name="all")
        with t2: show_list("Expense", tab_name="exp")
        with t3: show_list("Income", tab_name="inc")
        with t4: show_list("Transfer", tab_name="tra")

    elif st.session_state.selected_page == "Insights":
        inc_s = df[df['Type'] == 'Income']['Amount'].sum()
        exp_s = df[df['Type'] == 'Expense']['Amount'].sum()
        it1, it2 = st.tabs(["📋 Summary", "💹 Category Analysis"])
        with it1:
            st.metric("Savings", f"{(inc_s-exp_s):,.0f}")
            if inc_s > 0 or exp_s > 0:
                st.plotly_chart(px.pie(values=[inc_s, exp_s], names=['Income', 'Expense'], hole=0.5), use_container_width=True)
        with it2:
            analysis_df = df[df['Type'] != 'Transfer']
            if not analysis_df.empty:
                cat_sum = analysis_df.groupby(['Category', 'Type'])['Amount'].sum().reset_index()
                st.plotly_chart(px.pie(cat_sum, values='Amount', names='Category', color='Type', hole=0.4), use_container_width=True)

    elif st.session_state.selected_page == "Accounts":
        for acc in acc_list:
            inc = df[(df['Account'] == acc) & (df['Type'] == 'Income')]['Amount'].sum() + df[(df['To_Account'] == acc) & (df['Type'] == 'Transfer')]['Amount'].sum()
            exp = df[(df['Account'] == acc) & (df['Type'] == 'Expense')]['Amount'].sum() + df[(df['Account'] == acc) & (df['Type'] == 'Transfer')]['Amount'].sum()
            bal = max(0, inc - exp)
            with st.container(border=True): st.markdown(f"### {acc}\n**Balance: Rs {bal:,.0f}**")
