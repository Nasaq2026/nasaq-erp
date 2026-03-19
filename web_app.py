# web_app.py
import streamlit as st
import os
import sys
import warnings
import psycopg2
from datetime import datetime

# --- 1. إصلاح المسارات ---
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

# --- 2. تهيئة الإعدادات ---
warnings.simplefilter('ignore', UserWarning)
st.set_page_config(
    page_title="Nasq ERP | Pro UI", 
    page_icon="🎯", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 3. تحميل الشاشات بأمان ---
def load_system_pages():
    pages = {}
    modules = {
        "dashboard": ("web_ui.dashboard", "render_dashboard"),
        "new_order": ("web_ui.new_order", "render_new_order"),
        "orders": ("web_ui.orders", "render_orders"),
        "accounts": ("web_ui.accounts", "render_accounts"),
        "clients": ("web_ui.clients", "render_clients"),
        "employees": ("web_ui.employees", "render_employees"),
        "categories": ("web_ui.categories", "render_categories"),
        "ai_assistant": ("web_ui.ai_assistant", "render_ai_assistant"),
        "designer": ("web_ui.designer", "render_designer"),
        "tech": ("web_ui.technician", "render_technician"),
        "installer": ("web_ui.installer", "render_installer")
    }
    for key, (path, func) in modules.items():
        try:
            module = __import__(path, fromlist=[func])
            pages[key] = getattr(module, func)
        except Exception:
            pages[key] = lambda *args, **kwargs: st.error(f"❌ خطأ في تحميل {key}")
    return pages

PAGES = load_system_pages()

# --- 4. ستايل NASAQ PRO (الملكي المطور) ---
def inject_nasq_pro_css():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700;800&display=swap');
    html, body, [data-testid="stSidebar"] *, .stMarkdown, p, h1, h2, h3 {
        font-family: 'Cairo', sans-serif !important;
        direction: rtl; text-align: right;
    }
    .top-bar {
        display: flex; justify-content: space-between; align-items: center;
        padding: 10px 25px; background: rgba(15, 23, 42, 0.6);
        backdrop-filter: blur(12px); border-radius: 15px;
        border: 1px solid rgba(56, 189, 248, 0.2); margin-bottom: 25px;
    }
    .badge-pro {
        position: absolute; top: -5px; right: -8px; background: #ef4444;
        color: white; font-size: 10px; padding: 1px 5px; border-radius: 50%;
    }
    [data-testid="stSidebar"] { background: linear-gradient(180deg, #0f172a 0%, #1e293b 100%) !important; }
    div[data-testid="stRadioButtonCustomObject"] { display: none !important; }
    header {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

inject_nasq_pro_css()

# --- 5. الاتصال وإدارة الجداول تلقائياً ---
@st.cache_resource(ttl=60)
def init_connection():
    try:
        db_uri = "postgresql://postgres.jfqmcgicbdrhrtkhuwws:Nasaq268609@aws-1-ap-northeast-1.pooler.supabase.com:6543/postgres"
        conn = psycopg2.connect(db_uri, sslmode="require", connect_timeout=15)
        
        # التأكد من وجود جدول المراسلات لمنع الـ UndefinedTable
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS internal_messages (
                id SERIAL PRIMARY KEY,
                sender_name TEXT,
                sender_role TEXT,
                message TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()
        return conn
    except: return None

conn = init_connection()

if "logged_in" not in st.session_state:
    st.session_state.update({"logged_in": False, "emp_name": "", "role": ""})

# --- 6. وظائف الواجهة ---
def render_top_bar(msg_count=0):
    col_empty, col_info = st.columns([2, 1.2])
    with col_info:
        st.markdown(f"""
            <div class="top-bar">
                <div style="display: flex; gap: 20px;">
                    <div style="position: relative;">📩<span class="badge-pro">{msg_count}</span></div>
                    <div style="position: relative;">🔔<span class="badge-pro">!</span></div>
                </div>
                <div style="display: flex; align-items: center; gap: 12px;">
                    <div style="text-align: left;">
                        <div style="color: #38bdf8; font-weight: 800; font-size: 14px;">{st.session_state.emp_name}</div>
                        <div style="color: #94a3b8; font-size: 10px;">{st.session_state.role}</div>
                    </div>
                    <div style="font-size: 24px;">👤</div>
                </div>
            </div>
        """, unsafe_allow_html=True)

def render_sidebar_chat(conn):
    with st.sidebar:
        st.divider()
        with st.expander("💬 المراسلات الداخلية", expanded=False):
            try:
                cursor = conn.cursor()
                cursor.execute("SELECT sender_name, message FROM internal_messages ORDER BY id DESC LIMIT 5")
                msgs = cursor.fetchall()
                for m in reversed(msgs):
                    st.markdown(f"<small><b>{m[0]}:</b> {m[1]}</small>", unsafe_allow_html=True)
                
                with st.form("chat", clear_on_submit=True):
                    t = st.text_input("رسالة..", label_visibility="collapsed")
                    if st.form_submit_button("🚀"):
                        cursor.execute("INSERT INTO internal_messages (sender_name, sender_role, message) VALUES (%s, %s, %s)",
                                       (st.session_state.emp_name, st.session_state.role, t))
                        conn.commit()
                        st.rerun()
            except: conn.rollback()

# --- 7. بوابات النظام ---
def login_screen():
    st.write("<br><br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 1.2, 1])
    with col2:
        st.markdown('<h1 style="color:#38bdf8; text-align:center;">NASAQ ERP</h1>', unsafe_allow_html=True)
        with st.form("login"):
            serial = st.text_input("رقم الموظف")
            password = st.text_input("كلمة المرور", type="password")
            if st.form_submit_button("دخول 🚀", use_container_width=True):
                if conn:
                    cursor = conn.cursor()
                    cursor.execute("SELECT emp_name, role FROM employees WHERE serial_number = %s AND password = %s", (serial, password))
                    user = cursor.fetchone()
                    if user:
                        st.session_state.update({"logged_in": True, "emp_name": user[0], "role": user[1]})
                        st.rerun()
                    else: st.error("خطأ")

def main_portal():
    msg_count = 0
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM internal_messages")
        msg_count = cursor.fetchone()[0]
    except:
        conn.rollback() # إصلاح خطأ Transaction المنهارة

    render_top_bar(msg_count)
    render_sidebar_chat(conn)
    
    with st.sidebar:
        st.markdown('<h2 style="color: #38bdf8; text-align: center;">NASAQ PRO</h2>', unsafe_allow_html=True)
        st.divider()
        if st.session_state.role == "Admin":
            options = ["📊 لوحة القيادة", "🤖 المساعد الذكي", "➕ طلب جديد", "📦 الورشة", "🧾 المالية", "👥 العملاء", "👨‍💼 الفريق", "⚙️ الإعدادات"]
        else:
            options = ["🏠 شاشتي الرئيسية", "🤖 المساعد الذكي"]
        choice = st.radio("القائمة:", options, label_visibility="collapsed")
        if st.button("🚪 خروج", use_container_width=True):
            st.session_state.logged_in = False
            st.rerun()

    mapping = {
        "📊 لوحة القيادة": "dashboard", "🤖 المساعد الذكي": "ai_assistant", "➕ طلب جديد": "new_order",
        "📦 الورشة": "orders", "🧾 المالية": "accounts", "👥 العملاء": "clients",
        "👨‍💼 الفريق": "employees", "⚙️ الإعدادات": "categories", "🏠 شاشتي الرئيسية": "my_screen"
    }
    page_key = mapping.get(choice)
    if page_key == "ai_assistant": PAGES["ai_assistant"]()
    elif page_key == "my_screen":
        role = st.session_state.role
        if role == "Designer": PAGES["designer"](conn, st.session_state.emp_name)
        elif role == "Technician": PAGES["tech"](conn, st.session_state.emp_name)
        elif role == "Installer": PAGES["installer"](conn, st.session_state.emp_name)
    elif page_key: PAGES[page_key](conn)

# --- التشغيل ---
if not st.session_state.logged_in:
    login_screen()
else:
    main_portal()
