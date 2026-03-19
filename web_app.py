# web_app.py
import streamlit as st
import psycopg2
import warnings
from datetime import datetime
import os
import sys
from PIL import Image

# --- 🚀 1. حل مشاكل المسارات ---
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

# --- 2. تهيئة الإعدادات ---
warnings.simplefilter('ignore', UserWarning)
st.set_page_config(
    page_title="نَسق ERP | الإدارة الذكية", 
    page_icon="🎯", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 3. استيراد الشاشات الآمن ---
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
            pages[key] = lambda *args: st.error(f"⚠️ الملف {key} مفقود")
    return pages

PAGES = load_system_pages()

# --- 4. ستايل "نَسق" الفخم (CSS المطور) ---
def inject_creative_css():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700&display=swap');
    
    /* الخط العام والاتجاه */
    html, body, [data-testid="stSidebar"] *, .stMarkdown {
        font-family: 'Cairo', sans-serif !important;
        direction: rtl; text-align: right;
    }

    /* خلفية القائمة الجانبية */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0c1221 0%, #1e293b 100%) !important;
        border-left: 1px solid rgba(56, 189, 248, 0.2);
    }

    /* تصميم أزرار القائمة (الراديو بوتون المطور) */
    div[data-testid="stSidebarUserContent"] .stRadio div[role="radiogroup"] label {
        background-color: rgba(255, 255, 255, 0.05) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        padding: 12px 15px !important;
        border-radius: 12px !important;
        margin-bottom: 8px !important;
        transition: all 0.3s ease;
        color: white !important;
    }

    /* تأثير الحلق عند الاختيار */
    div[data-testid="stSidebarUserContent"] .stRadio div[role="radiogroup"] label[data-selected="true"] {
        background: rgba(56, 189, 248, 0.2) !important;
        border-color: #38bdf8 !important;
        box-shadow: 0 4px 15px rgba(56, 189, 248, 0.3);
    }

    /* إخفاء الدائرة الأصلية للراديو */
    div[data-testid="stRadioButtonCustomObject"] { display: none !important; }

    /* أزرار الحفظ والخروج */
    .stButton > button {
        width: 100% !important;
        border-radius: 10px !important;
        font-weight: bold !important;
        transition: 0.3s;
    }
    
    /* إخفاء الهيدر الافتراضي */
    header {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

inject_creative_css()

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

# --- 6. شاشات النظام ---
def login_screen():
    st.write("<br><br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 1.2, 1])
    with col2:
        st.markdown("<h1 style='text-align: center; color: #38bdf8;'>NASAQ ERP</h1>", unsafe_allow_html=True)
        with st.form("login"):
            serial = st.text_input("رقم الموظف")
            password = st.text_input("كلمة المرور", type="password")
            if st.form_submit_button("دخول آمن 🚀"):
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
        st.markdown(f"<h2 style='color: #38bdf8; text-align: center;'>نَسق | {st.session_state.role}</h2>", unsafe_allow_html=True)
        st.write(f"<p style='text-align:center;'>مرحباً، {st.session_state.emp_name}</p>", unsafe_allow_html=True)
        st.divider()
        
        if st.session_state.role == "Admin":
            options = ["📊 لوحة القيادة", "🤖 المساعد الذكي", "➕ طلب جديد", "📦 الورشة", "🧾 المالية", "👥 العملاء", "👨‍💼 الفريق", "⚙️ الإعدادات"]
        else:
            options = ["🏠 شاشتي", "🤖 المساعد الذكي"]
            
        choice = st.radio("القائمة:", options, label_visibility="collapsed")
        
        st.divider()
        if st.button("🚪 خروج"):
            st.session_state.logged_in = False
            st.rerun()

    # الربط البرمجي
    mapping = {
        "📊 لوحة القيادة": "dashboard", "🤖 المساعد الذكي": "ai_assistant", "➕ طلب جديد": "new_order",
        "📦 الورشة": "orders", "🧾 المالية": "accounts", "👥 العملاء": "clients",
        "👨‍💼 الفريق": "employees", "⚙️ الإعدادات": "categories", "🏠 شاشتي": "my_screen"
    }
    
    page_key = mapping.get(choice)
    if page_key == "my_screen":
        role = st.session_state.role
        if role == "Designer": PAGES["designer"](conn, st.session_state.emp_name)
        elif role == "Technician": PAGES["tech"](conn, st.session_state.emp_name)
        elif role == "Installer": PAGES["installer"](conn, st.session_state.emp_name)
    elif page_key:
        PAGES[page_key](conn if page_key != "ai_assistant" else None)

# --- التشغيل ---
if not st.session_state.logged_in:
    login_screen()
else:
    main_portal()
