# web_app.py
import streamlit as st
import os
import sys
import psycopg2
from datetime import datetime

# --- 1. إعدادات المسارات ---
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

# --- 2. تهيئة الإعدادات (ثبات تام) ---
st.set_page_config(
    page_title="Nasq ERP | PRO", 
    page_icon="🎯", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 3. استايل نَسق الأصلي المنظم (نظيف وبسيط) ---
def inject_nasq_ui():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700&display=swap');
    
    /* الخط العربي والاتجاه */
    html, body, [data-testid="stSidebar"] *, .stMarkdown {
        font-family: 'Cairo', sans-serif !important;
        direction: rtl; text-align: right;
    }

    /* تنسيق القائمة الجانبية */
    [data-testid="stSidebar"] {
        background-color: #0f172a !important;
        border-left: 1px solid #1e293b;
    }

    /* تنسيق نصوص القائمة */
    div[data-testid="stSidebarUserContent"] .stRadio div[role="radiogroup"] label {
        color: white !important;
        font-size: 16px !important;
        background: #1e293b;
        padding: 10px;
        border-radius: 8px;
        margin-bottom: 5px;
        cursor: pointer;
    }
    
    /* إخفاء الهيدر الافتراضي */
    header {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

inject_nasq_ui()

# --- 4. الاتصال بقاعدة البيانات ---
@st.cache_resource(ttl=60)
def init_connection():
    try:
        db_uri = "postgresql://postgres.jfqmcgicbdrhrtkhuwws:Nasaq268609@aws-1-ap-northeast-1.pooler.supabase.com:6543/postgres"
        conn = psycopg2.connect(db_uri, sslmode="require", connect_timeout=15)
        return conn
    except: return None

conn = init_connection()

# تحميل الصفحات (تأكد من وجود المجلدات والملفات)
def load_system_pages():
    pages = {}
    modules = {
        "dashboard": ("web_ui.dashboard", "render_dashboard"),
        "ai_assistant": ("web_ui.ai_assistant", "render_ai_assistant"),
        "new_order": ("web_ui.new_order", "render_new_order"),
        "orders": ("web_ui.orders", "render_orders"),
        "accounts": ("web_ui.accounts", "render_accounts"),
        "clients": ("web_ui.clients", "render_clients"),
        "employees": ("web_ui.employees", "render_employees"),
        "categories": ("web_ui.categories", "render_categories")
    }
    for key, (path, func) in modules.items():
        try:
            module = __import__(path, fromlist=[func])
            pages[key] = getattr(module, func)
        except: pages[key] = lambda *args, **kwargs: st.error(f"⚠️ الملف {key} يحتاج فحص")
    return pages

PAGES = load_system_pages()

if "logged_in" not in st.session_state:
    st.session_state.update({"logged_in": False, "emp_name": "", "role": ""})

# --- 5. بوابة الدخول ---
def login_screen():
    st.write("<br><br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 1.2, 1])
    with col2:
        st.markdown("<h1 style='text-align:center; color:#38bdf8;'>NASAQ ERP</h1>", unsafe_allow_html=True)
        with st.form("login_form"):
            serial = st.text_input("رقم الموظف")
            pwd = st.text_input("كلمة المرور", type="password")
            if st.form_submit_button("دخول", width='stretch'):
                cursor = conn.cursor()
                cursor.execute("SELECT emp_name, role FROM employees WHERE serial_number = %s AND password = %s", (serial, pwd))
                user = cursor.fetchone()
                if user:
                    st.session_state.update({"logged_in": True, "emp_name": user[0], "role": user[1]})
                    st.rerun()
                else: st.error("بيانات خاطئة")

# --- 6. بوابة النظام الرئيسية ---
def main_portal():
    # الهيدر العلوي البسيط
    col_l, col_r = st.columns([1, 1])
    with col_r:
        st.markdown(f"**👤 {st.session_state.emp_name}** | {st.session_state.role}")

    with st.sidebar:
        st.markdown("<h2 style='color:#38bdf8; text-align:center;'>نَسق PRO</h2>", unsafe_allow_html=True)
        st.divider()
        
        # القائمة الموحدة
        if st.session_state.role == "Admin":
            options = ["📊 لوحة القيادة", "🤖 المساعد الذكي", "➕ طلب جديد", "📦 الورشة", "🧾 المالية", "👥 العملاء", "👨‍💼 الفريق", "⚙️ الإعدادات"]
        else:
            options = ["🏠 شاشتي الرئيسية", "🤖 المساعد الذكي"]
            
        choice = st.radio("القائمة:", options, label_visibility="collapsed")
        
        # الشات الداخلي (في القائمة)
        st.divider()
        with st.expander("💬 شات الفريق"):
            msg = st.text_input("رسالة سريعة", key="sidebar_chat")
            if st.button("إرسال", width='stretch'): st.toast("تم الإرسال!")

        if st.button("🚪 خروج", width='stretch'):
            st.session_state.logged_in = False
            st.rerun()

    # الربط
    mapping = {
        "📊 لوحة القيادة": "dashboard", "🤖 المساعد الذكي": "ai_assistant", "➕ طلب جديد": "new_order",
        "📦 الورشة": "orders", "🧾 المالية": "accounts", "👥 العملاء": "clients",
        "👨‍💼 الفريق": "employees", "⚙️ الإعدادات": "categories"
    }
    
    page_key = mapping.get(choice)
    if page_key == "ai_assistant": PAGES["ai_assistant"]()
    elif page_key: PAGES[page_key](conn)

# التشغيل
if not st.session_state.logged_in:
    login_screen()
else:
    main_portal()
