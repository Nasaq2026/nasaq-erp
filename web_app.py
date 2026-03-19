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

# --- 2. تهيئة الإعدادات (ثبات تام) ---
warnings.simplefilter('ignore', UserWarning)
st.set_page_config(
    page_title="نَسق ERP | الإدارة الذكية", 
    page_icon="🎯", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 3. ستايل نَسق الاحترافي (تمديد الأزرار والمحاذاة) ---
def inject_nasq_styled_ui():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700;800&display=swap');
    
    /* ضبط الاتجاه العام للموقع */
    html, body, [data-testid="stAppViewContainer"], [data-testid="stSidebar"] {
        direction: rtl;
        text-align: right;
    }

    /* تنسيق القائمة الجانبية */
    [data-testid="stSidebar"] {
        background-color: #0f172a !important;
        border-left: 1px solid #1e293b;
    }

    /* إجبار القائمة على عرض الأزرار بكامل المساحة المتاحة */
    [data-testid="stSidebarUserContent"] {
        padding: 10px 0px !important;
    }

    /* تمديد الخيارات (Radio Buttons) لتملأ المساحة جهة اليسار */
    div[data-testid="stSidebarUserContent"] .stRadio div[role="radiogroup"] {
        display: flex;
        flex-direction: column;
        gap: 8px;
        padding: 0 10px; /* هوامش بسيطة من الجانبين للفخامة */
    }

    div[data-testid="stSidebarUserContent"] .stRadio div[role="radiogroup"] label {
        color: white !important;
        background-color: rgba(255, 255, 255, 0.05) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        padding: 15px 20px !important; /* زيادة الحشو الداخلي */
        border-radius: 12px !important;
        width: 100% !important; /* تمديد الزر للعرض الكامل */
        display: flex !important;
        align-items: center;
        transition: 0.3s all ease;
        margin: 0 !important;
        cursor: pointer;
    }

    /* تأثير التحديد (Active State) */
    div[data-testid="stSidebarUserContent"] .stRadio div[role="radiogroup"] label[data-selected="true"] {
        background-color: #38bdf8 !important;
        color: #0f172a !important;
        border-color: #38bdf8 !important;
        font-weight: 700 !important;
        box-shadow: 0 4px 15px rgba(56, 189, 248, 0.3);
    }

    /* تحسين الخطوط */
    html, body, [data-testid="stSidebar"] *, .stMarkdown, p, h1, h2, h3, label {
        font-family: 'Cairo', sans-serif !important;
    }

    /* إخفاء الهيدر الافتراضي */
    header {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

inject_nasq_styled_ui()

# --- 4. الاتصال بقاعدة البيانات ---
@st.cache_resource(ttl=60)
def init_connection():
    try:
        db_uri = "postgresql://postgres.jfqmcgicbdrhrtkhuwws:Nasaq268609@aws-1-ap-northeast-1.pooler.supabase.com:6543/postgres"
        return psycopg2.connect(db_uri, sslmode="require", connect_timeout=15)
    except: return None

conn = init_connection()

# --- 5. تحميل الصفحات ---
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
        "categories": ("web_ui.categories", "render_categories"),
        "designer": ("web_ui.designer", "render_designer"),
        "tech": ("web_ui.technician", "render_technician"),
        "installer": ("web_ui.installer", "render_installer")
    }
    for key, (path, func) in modules.items():
        try:
            module = __import__(path, fromlist=[func])
            pages[key] = getattr(module, func)
        except: pages[key] = lambda *args, **kwargs: st.error(f"⚠️ الملف {key} غير متاح")
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
            st.image("logo.png", width=250)
        with st.form("login"):
            u = st.text_input("رقم الموظف")
            p = st.text_input("كلمة المرور", type="password")
            if st.form_submit_button("دخول", width='stretch'):
                if conn:
                    cursor = conn.cursor()
                    cursor.execute("SELECT emp_name, role FROM employees WHERE serial_number = %s AND password = %s", (u, p))
                    user = cursor.fetchone()
                    if user:
                        st.session_state.update({"logged_in": True, "emp_name": user[0], "role": user[1]})
                        st.rerun()
                    else: st.error("بيانات خاطئة")

# --- 7. بوابة النظام الرئيسية ---
def main_portal():
    with st.sidebar:
        if os.path.exists("logo.png"):
            st.image("logo.png", width='stretch')
        st.divider()
        
        st.markdown(f"<p style='text-align:center; color:#94a3b8; font-size:14px;'>مرحباً، {st.session_state.emp_name}</p>", unsafe_allow_html=True)
        
        if st.session_state.role == "Admin":
            options = ["📊 لوحة القيادة", "🤖 المساعد الذكي", "➕ طلب جديد", "📦 الورشة", "🧾 المالية", "👥 العملاء", "👨‍💼 الفريق", "⚙️ الإعدادات"]
        else:
            options = ["🏠 شاشتي الرئيسية", "🤖 المساعد الذكي"]
            
        choice = st.radio("القائمة:", options, label_visibility="collapsed")
        
        st.divider()
        if st.button("🚪 تسجيل الخروج", width='stretch'):
            st.session_state.logged_in = False
            st.rerun()

    # الربط
    mapping = {
        "📊 لوحة القيادة": "dashboard", "🤖 المساعد الذكي": "ai_assistant", "➕ طلب جديد": "new_order",
        "📦 الورشة": "orders", "🧾 المالية": "accounts", "👥 العملاء": "clients",
        "👨‍💼 الفريق": "employees", "⚙️ الإعدادات": "categories", "🏠 شاشتي الرئيسية": "my_screen"
    }
    
    page_key = mapping.get(choice)
    if page_key == "ai_assistant": PAGES["ai_assistant"]()
    elif page_key: PAGES[page_key](conn)

# التشغيل
if not st.session_state.logged_in:
    login_screen()
else:
    main_portal()
