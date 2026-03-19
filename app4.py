st.markdown("""
<style>

/* 🌙 Overall App */
.stApp {
    background: linear-gradient(135deg, #eef2f7, #e3e9f2);
    font-family: 'Segoe UI', sans-serif;
}

/* 📦 Sidebar */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #1e293b, #334155) !important;
    color: white;
}

/* Sidebar text */
[data-testid="stSidebar"] * {
    color: white !important;
}

/* 🧊 Cards (containers) */
div[data-testid="stContainer"] {
    border-radius: 15px !important;
    padding: 10px !important;
}

/* 🔵 Header */
.blue-header {
    background: linear-gradient(90deg, #2563eb, #1d4ed8);
    padding: 20px;
    border-radius: 15px;
    color: white;
    text-align: center;
    margin-bottom: 20px;
    box-shadow: 0px 5px 15px rgba(0,0,0,0.2);
}

/* 💳 Account Box */
.sidebar-acc-box {
    background: rgba(255,255,255,0.08);
    padding: 12px;
    border-radius: 12px;
    margin-bottom: 8px;
    backdrop-filter: blur(8px);
    border: 1px solid rgba(255,255,255,0.1);
}

/* 💰 Total Box */
.total-balance-box {
    background: linear-gradient(135deg, #22c55e, #16a34a);
    color: white;
    padding: 14px;
    border-radius: 12px;
    margin-top: 10px;
    text-align: center;
    font-weight: bold;
    box-shadow: 0px 4px 12px rgba(0,0,0,0.2);
}

/* 📊 List total */
.list-total-box {
    background: white;
    padding: 12px;
    border-radius: 12px;
    border-left: 6px solid #2563eb;
    margin-bottom: 15px;
    box-shadow: 0px 2px 8px rgba(0,0,0,0.08);
}

/* 🔘 Buttons */
.stButton > button {
    border-radius: 10px !important;
    background: linear-gradient(135deg, #2563eb, #1d4ed8);
    color: white;
    border: none;
    transition: 0.3s;
}

.stButton > button:hover {
    transform: scale(1.05);
    background: linear-gradient(135deg, #1d4ed8, #1e40af);
}

/* Inputs */
.stTextInput input,
.stNumberInput input,
.stSelectbox div[data-baseweb="select"] {
    border-radius: 10px !important;
}

/* Tabs */
button[data-baseweb="tab"] {
    font-size: 16px !important;
    font-weight: bold;
}

/* Scrollbar */
::-webkit-scrollbar {
    width: 6px;
}
::-webkit-scrollbar-thumb {
    background: #94a3b8;
    border-radius: 10px;
}

</style>
""", unsafe_allow_html=True)
