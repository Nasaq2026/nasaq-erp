# web_app.py
import streamlit as st
import os
import sys
import warnings
import json
import psycopg2
from datetime import datetime

# --- 1. إصلاح المسارات ---
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

# --- 2. تهيئة الإعدادات ---
warnings.simplefilter('ignore', UserWarning)
st.set_page_config(
    page_title="Nasq ERP | الإدارة الفخمة", 
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
        except Exception as e:
            pages[key] = lambda *args, **kwargs: st.error(f"❌ خطأ في تحميل {key}")
    return pages

PAGES = load_system_pages()

# --- 4. ستايل NASAQ الملكي (CSS المطور والاحترافي) ---
def inject_nasq_royal_css():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700;800&display=swap');
    
    /* 1. الأساسيات والخطوط */
    html, body, [data-testid="stSidebar"] *, .stMarkdown, p, h1, h2, h3 {
        font-family: 'Cairo', sans-serif !important;
        direction: rtl; text-align: right;
    }

    /* 2. القائمة الجانبية (تصميم زجاجي داكن فخم) */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0f172a 0%, #1e293b 100%) !important;
        border-left: 1px solid rgba(56, 189, 248, 0.1);
        min-width: 300px !important;
    }

    /* 3. اللوجو والعنوان */
    .nasq-header {
        color: #38bdf8;
        font-size: 28px;
        font-weight: 800;
        text-align: center;
        padding: 20px 0;
        letter-spacing: 1px;
    }

    /* 4. تصميم أزرار القائمة (مثل الصورة الاحترافية) */
    div[data-testid="stSidebarUserContent"] .stRadio div[role="radiogroup"] label {
        background-color: transparent !important;
        border: none !important;
        padding: 14px 25px !important;
        border-radius: 12px !important;
        margin-bottom: 5px !important;
        color: rgba(255, 255, 255, 0.8) !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        font-size: 16px !important;
    }

    /* تأثير الاختيار (Glow Effect) */
    div[data-testid="stSidebarUserContent"] .stRadio div[role="radiogroup"] label[data-selected="true"] {
        background: rgba(56, 189, 248, 0.12) !important;
        color: #38bdf8 !important;
        font-weight: 700 !important;
        border-right: 4px solid #38bdf8 !important;
        box-shadow: -5px 0 15px rgba(56, 189, 248, 0.1);
    }

    /* إخفاء الدائرة الافتراضية للراديو */
    div[data-testid="stRadioButtonCustomObject"] { display: none !important; }

    /* 5. الأزرار (خروج) */
    .stButton > button {
        background-color: rgba(255, 255, 255, 0.05) !important;
        color: white !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 10px !important;
        padding: 10px !important;
        font-weight: 600 !important;
    }
    .stButton > button:hover {
        border-color: #ef4444 !important;
        background: rgba(239, 68, 68, 0.1) !important;
        color: #ef4444 !important;
    }

    /* إخفاء الهيدر */
    header {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

inject_nasq_royal_css()

# --- 5. الاتصال وإدارة الجلسة ---
@st.cache_resource(ttl=60)
def init_connection():
    try:
        db_uri = "postgresql://postgres.jfqmcgicbdrhrtkhuwws:Nasaq268609@aws-1-ap-northeast-1.pooler.supabase.com:6543/postgres"
        return psycopg2.connect(db_uri, sslmode="require", connect_timeout=15)
    except: return None

conn = init_connection()

if "logged_in" not in st.session_state:
    st.session_state.update({"logged_in": False, "emp_name": "", "role": ""})

# --- 6. بوابات النظام ---
def login_screen():
    st.write("<br><br><br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        st.markdown('<div class="nasq-header">NASAQ ERP</div>', unsafe_allow_html=True)
        with st.form("login"):
            serial = st.text_input("رقم الموظف")
            password = st.text_input("كلمة المرور", type="password")
            if st.form_submit_button("دخول آمن 🚀", use_container_width=True):
                if conn:
                    cursor = conn.cursor()
                    cursor.execute("SELECT emp_name, role FROM employees WHERE serial_number = %s AND password = %s", (serial, password))
                    user = cursor.fetchone()
                    if user:
                        st.session_state.update({"logged_in": True, "emp_name": user[0], "role": user[1]})
                        st.rerun()
                    else: st.error("بيانات خاطئة")

def main_portal():
    with st.sidebar:
        st.markdown('<div class="nasq-header">NASAQ ERP</div>', unsafe_allow_html=True)
        st.markdown(f"<p style='text-align:center; color: #94a3b8;'>أهلاً بك، {st.session_state.emp_name}</p>", unsafe_allow_html=True)
        st.divider()
        
        if st.session_state.role == "Admin":
            options = ["📊 لوحة القيادة", "🤖 المساعد الذكي", "➕ طلب جديد", "📦 الورشة", "🧾 المالية", "👥 العملاء", "👨‍💼 الفريق", "⚙️ الإعدادات"]
        else:
            options = ["🏠 شاشتي الرئيسية", "🤖 المساعد الذكي"]
            
        choice = st.radio("القائمة:", options, label_visibility="collapsed")
        
        st.divider()
        if st.button("🚪 تسجيل الخروج", use_container_width=True):
            st.session_state.logged_in = False
            st.rerun()

    # --- 7. منطق التنقل المصلح (إصلاح الـ TypeError) ---
    mapping = {
        "📊 لوحة القيادة": "dashboard", "🤖 المساعد الذكي": "ai_assistant", "➕ طلب جديد": "new_order",
        "📦 الورشة": "orders", "🧾 المالية": "accounts", "👥 العملاء": "clients",
        "👨‍💼 الفريق": "employees", "⚙️ الإعدادات": "categories", "🏠 شاشتي الرئيسية": "my_screen"
    }
    
    page_key = mapping.get(choice)
    
    if page_key == "ai_assistant":
        PAGES["ai_assistant"]() # استدعاء بدون تمرير 'conn'
    elif page_key == "my_screen":
        role = st.session_state.role
        if role == "Designer": PAGES["designer"](conn, st.session_state.emp_name)
        elif role == "Technician": PAGES["tech"](conn, st.session_state.emp_name)
        elif role == "Installer": PAGES["installer"](conn, st.session_state.emp_name)
    elif page_key:
        PAGES[page_key](conn)

# --- التشغيل ---
if not st.session_state.logged_in:
    login_screen()
else:
    main_portal()
