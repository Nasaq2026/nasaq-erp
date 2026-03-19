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

# --- 2. تهيئة الإعدادات (نظام 2026 المستقر) ---
warnings.simplefilter('ignore', UserWarning)
st.set_page_config(
    page_title="Nasq ERP | PRO", 
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
        except:
            pages[key] = lambda *args, **kwargs: st.error(f"❌ ملف {key} غير موجود")
    return pages

PAGES = load_system_pages()

# --- 4. ستايل نَسق الأصلي المنظم (CSS بسيط وقوي) ---
def inject_stable_css():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700&display=swap');
    
    /* الخط العربي والاتجاه */
    html, body, [data-testid="stSidebar"] *, .stMarkdown {
        font-family: 'Cairo', sans-serif !important;
        direction: rtl; text-align: right;
    }

    /* ضمان ظهور القائمة الجانبية بوضوح */
    [data-testid="stSidebar"] {
        background-color: #111827 !important;
        min-width: 250px !important;
    }

    /* تنسيق الخيارات في القائمة */
    div[data-testid="stSidebarUserContent"] .stRadio div[role="radiogroup"] label {
        color: #e5e7eb !important;
        background-color: #1f2937 !important;
        padding: 10px 15px !important;
        border-radius: 8px !important;
        margin-bottom: 5px !important;
        border: 1px solid #374151 !important;
    }

    /* إخفاء الهيدر الافتراضي المزعج */
    header {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

inject_stable_css()

# --- 5. الاتصال بقاعدة البيانات ---
@st.cache_resource(ttl=60)
def init_connection():
    try:
        db_uri = "postgresql://postgres.jfqmcgicbdrhrtkhuwws:Nasaq268609@aws-1-ap-northeast-1.pooler.supabase.com:6543/postgres"
        conn = psycopg2.connect(db_uri, sslmode="require", connect_timeout=15)
        # إنشاء جدول المراسلات إذا لم يكن موجوداً
        cursor = conn.cursor()
        cursor.execute("CREATE TABLE IF NOT EXISTS internal_messages (id SERIAL, sender_name TEXT, sender_role TEXT, message TEXT, timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP)")
        conn.commit()
        return conn
    except: return None

conn = init_connection()

if "logged_in" not in st.session_state:
    st.session_state.update({"logged_in": False, "emp_name": "", "role": ""})

# --- 6. مكونات الواجهة ---
def render_header():
    col1, col2 = st.columns([3, 1])
    with col2:
        st.markdown(f"""
            <div style="background:#1f2937; padding:10px; border-radius:10px; border:1px solid #374151; text-align:center;">
                <span style="color:#38bdf8; font-weight:bold;">👤 {st.session_state.emp_name}</span><br>
                <small style="color:#94a3b8;">{st.session_state.role}</small>
            </div>
        """, unsafe_allow_html=True)

# --- 7. بوابات النظام ---
def main_portal():
    render_header()
    
    with st.sidebar:
        st.markdown("<h1 style='color:#38bdf8; text-align:center;'>NASAQ PRO</h1>", unsafe_allow_html=True)
        st.divider()
        
        if st.session_state.role == "Admin":
            options = ["📊 لوحة القيادة", "🤖 المساعد الذكي", "➕ طلب جديد", "📦 الورشة", "🧾 المالية", "👥 العملاء", "👨‍💼 الفريق", "⚙️ الإعدادات"]
        else:
            options = ["🏠 شاشتي الرئيسية", "🤖 المساعد الذكي"]
            
        choice = st.radio("القائمة:", options, label_visibility="collapsed")
        
        # نظام المراسلات البسيط داخل القائمة
        with st.expander("💬 المراسلات"):
            st.caption("الشات الداخلي للفريق")
            if st.button("تحديث 🔄", width='stretch'): st.rerun()

        st.divider()
        if st.button("🚪 خروج", width='stretch'):
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
    elif page_key:
        PAGES[page_key](conn)

# --- 8. التشغيل ---
if not st.session_state.logged_in:
    col1, col2, col3 = st.columns([1,1.2,1])
    with col2:
        st.markdown("<h2 style='text-align:center;'>تسجيل دخول نَسق</h2>", unsafe_allow_html=True)
        with st.form("login"):
            u = st.text_input("رقم الموظف")
            p = st.text_input("كلمة المرور", type="password")
            if st.form_submit_button("دخول", width='stretch'):
                cursor = conn.cursor()
                cursor.execute("SELECT emp_name, role FROM employees WHERE serial_number = %s AND password = %s", (u, p))
                user = cursor.fetchone()
                if user:
                    st.session_state.update({"logged_in": True, "emp_name": user[0], "role": user[1]})
                    st.rerun()
                else: st.error("خطأ في البيانات")
else:
    main_portal()
