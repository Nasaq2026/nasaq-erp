# web_app.py
import streamlit as st
import os
import sys
import warnings
import psycopg2
from datetime import datetime

# --- 1. حل مشاكل المسارات ---
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

# --- 2. إعدادات الصفحة (ثبات عالي) ---
warnings.simplefilter('ignore', UserWarning)
st.set_page_config(
    page_title="Nasq ERP | نَسق", 
    page_icon="🎯", 
    layout="wide",
    initial_sidebar_state="expanded" # إجبار القائمة على الظهور
)

# --- 3. ستايل نَسق الأصلي النظيف (بدون تداخل) ---
def inject_stable_ui():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700;800&display=swap');
    
    /* الخط العربي والاتجاه */
    html, body, [data-testid="stSidebar"] *, .stMarkdown {
        font-family: 'Cairo', sans-serif !important;
        direction: rtl; text-align: right;
    }

    /* ضمان ظهور القائمة الجانبية بلونها الداكن الملكي */
    [data-testid="stSidebar"] {
        background-color: #0f172a !important;
        min-width: 280px !important;
    }

    /* تنسيق أزرار القائمة (أبيض ناصع وواضح) */
    div[data-testid="stSidebarUserContent"] .stRadio div[role="radiogroup"] label {
        color: white !important;
        background-color: #1e293b !important;
        padding: 12px 15px !important;
        border-radius: 10px !important;
        margin-bottom: 8px !important;
        border: 1px solid #334155 !important;
        font-weight: 600 !important;
    }

    /* إخفاء الهيدر الافتراضي */
    header {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

inject_stable_ui()

# --- 4. الاتصال بقاعدة البيانات ---
@st.cache_resource(ttl=60)
def init_connection():
    try:
        db_uri = "postgresql://postgres.jfqmcgicbdrhrtkhuwws:Nasaq268609@aws-1-ap-northeast-1.pooler.supabase.com:6543/postgres"
        return psycopg2.connect(db_uri, sslmode="require", connect_timeout=15)
    except: return None

conn = init_connection()

# --- 5. تحميل موديولات النظام ---
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
        except:
            pages[key] = lambda *args, **kwargs: st.error(f"❌ الملف {key} غير موجود")
    return pages

PAGES = load_system_pages()

if "logged_in" not in st.session_state:
    st.session_state.update({"logged_in": False, "emp_name": "", "role": ""})

# --- 6. بوابة الدخول ---
def login_screen():
    st.write("<br><br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 1.2, 1])
    with col2:
        if os.path.exists("logo.png"):
            st.image("logo.png", width=200)
        else:
            st.markdown("<h1 style='text-align:center; color:#38bdf8;'>نَسق ERP</h1>", unsafe_allow_html=True)
            
        with st.form("login"):
            u = st.text_input("رقم الموظف")
            p = st.text_input("كلمة المرور", type="password")
            if st.form_submit_button("دخول آمن", width='stretch'):
                cursor = conn.cursor()
                cursor.execute("SELECT emp_name, role FROM employees WHERE serial_number = %s AND password = %s", (u, p))
                user = cursor.fetchone()
                if user:
                    st.session_state.update({"logged_in": True, "emp_name": user[0], "role": user[1]})
                    st.rerun()
                else: st.error("بيانات الدخول غير صحيحة")

# --- 7. بوابة النظام الرئيسية ---
def main_portal():
    with st.sidebar:
        # استعادة اللوجو
        if os.path.exists("logo.png"):
            st.image("logo.png", width='stretch')
        else:
            st.markdown("<h2 style='color:#38bdf8; text-align:center;'>NASAQ PRO</h2>", unsafe_allow_html=True)
        
        st.markdown(f"<p style='text-align:center; color:#94a3b8;'>مرحباً، {st.session_state.emp_name}</p>", unsafe_allow_html=True)
        st.divider()
        
        # القائمة الجانبية المضمونة
        if st.session_state.role == "Admin":
            options = ["📊 لوحة القيادة", "🤖 المساعد الذكي", "➕ طلب جديد", "📦 الورشة", "🧾 المالية", "👥 العملاء", "👨‍💼 الفريق", "⚙️ الإعدادات"]
        else:
            options = ["🏠 شاشتي الرئيسية", "🤖 المساعد الذكي"]
            
        choice = st.radio("القائمة الرئيسية:", options, label_visibility="collapsed")
        
        st.divider()
        # زر تسجيل الخروج
        if st.button("🚪 تسجيل الخروج", width='stretch'):
            st.session_state.logged_in = False
            st.rerun()

    # ربط الصفحات
    mapping = {
        "📊 لوحة القيادة": "dashboard", "🤖 المساعد الذكي": "ai_assistant", "➕ طلب جديد": "new_order",
        "📦 الورشة": "orders", "🧾 المالية": "accounts", "👥 العملاء": "clients",
        "👨‍💼 الفريق": "employees", "⚙️ الإعدادات": "categories"
    }
    
    page_key = mapping.get(choice)
    if page_key == "ai_assistant":
        PAGES["ai_assistant"]()
    elif page_key:
        PAGES[page_key](conn)

# التشغيل
if not st.session_state.logged_in:
    login_screen()
else:
    main_portal()
