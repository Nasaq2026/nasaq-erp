# web_app.py
import streamlit as st
import os
import sys
import warnings
import json
import psycopg2
from datetime import datetime
from PIL import Image

# --- 🚀 1. إعدادات المسارات وحماية الموديولات ---
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

# ملفات الـ __init__.py الفارغة ضرورية في المجلدات الفرعية

# --- 2. تهيئة الإعدادات الأساسية ---
warnings.simplefilter('ignore', UserWarning)

st.set_page_config(
    page_title="Nasq ERP | الإدارة الذكية", 
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
            pages[key] = lambda *args, **kwargs: st.error(f"⚠️ الملف {key} مفقود أو به خطأ")
    return pages

PAGES = load_system_pages()

# --- 4. ستايل "نَسق" الفخم والمطور (UI الاحترافي) ---
def inject_nasq_ui_css():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700;800&display=swap');
    
    /* 1. التنسيق العام والخط */
    html, body, [data-testid="stSidebar"] *, .stMarkdown, p, h1, h2, h3 {
        font-family: 'Cairo', sans-serif !important;
        direction: rtl; 
        text-align: right;
    }

    /* 2. خلفية القائمة الجانبية (تصميم زجاجي متدرج) */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #101625 0%, #1e293b 100%) !important;
        border-left: 1px solid rgba(56, 189, 248, 0.2);
    }

    /* 3. تنسيق العناوين في القائمة الجانبية */
    .nasq-logo {
        color: #38bdf8;
        text-align: center;
        font-size: 28px;
        font-weight: 800;
        margin-bottom: 5px;
    }
    
    .nasq-role {
        color: rgba(255, 255, 255, 0.8);
        text-align: center;
        font-size: 14px;
        margin-bottom: 25px;
    }

    /* 4. تصميم أزرار القائمة المستوحى من UI الاحترافي */
    div[data-testid="stSidebarUserContent"] .stRadio div[role="radiogroup"] label {
        background-color: transparent !important; /* خلفية شفافة في الحالة العادية */
        border: none !important;
        padding: 12px 20px !important;
        border-radius: 8px !important; /* حواف أنعم */
        margin-bottom: 2px !important; /* تباعد أقل للخيارات المتراصة */
        transition: all 0.2s ease;
        color: white !important;
        display: flex;
        align-items: center;
        cursor: pointer;
    }

    /* 5. تأثير التحليق (Hover) والحالة المختارة (Selected) */
    div[data-testid="stSidebarUserContent"] .stRadio div[role="radiogroup"] label:hover {
        background-color: rgba(255, 255, 255, 0.05) !important;
    }

    div[data-testid="stSidebarUserContent"] .stRadio div[role="radiogroup"] label[data-selected="true"] {
        background-color: rgba(56, 189, 248, 0.15) !important; /* خلفية زرقاء فاتحة عند الاختيار */
        color: #38bdf8 !important; /* لون النص أزرق عند الاختيار */
        font-weight: 700 !important;
    }

    /* 6. إخفاء الراديو بوتون الافتراضي */
    div[data-testid="stRadioButtonCustomObject"] {
        display: none !important;
    }

    /* 7. تنسيق الأزرار (حفظ، خروج) */
    .stButton > button {
        width: 100% !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
        transition: 0.3s;
        border: 1px solid rgba(255, 255, 255, 0.1);
        background-color: rgba(255, 255, 255, 0.03);
        color: white;
    }

    .stButton > button:hover {
        border-color: #38bdf8;
        background-color: rgba(56, 189, 248, 0.1);
    }

    /* 8. إخفاء الهيدر الافتراضي */
    header {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# استدعاء الـ CSS المطور
inject_nasq_ui_css()

# --- 5. الاتصال وإدارة الجلسة ---
@st.cache_resource(ttl=60)
def init_connection():
    try:
        db_uri = "postgresql://postgres.jfqmcgicbdrhrtkhuwws:Nasaq268609@aws-1-ap-northeast-1.pooler.supabase.com:6543/postgres"
        return psycopg2.connect(db_uri, sslmode="require", connect_timeout=15)
    except:
        return None

conn = init_connection()

if "logged_in" not in st.session_state:
    st.session_state.update({"logged_in": False, "emp_name": "", "role": ""})

# --- 6. بوابات النظام ---
def login_screen():
    st.write("<br><br><br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        st.markdown('<div class="nasq-logo">Nasq ERP</div>', unsafe_allow_html=True)
        with st.form("login_form"):
            st.markdown("<p style='text-align: center; color: rgba(255,255,255,0.7);'>تسجيل الدخول للنظام المطور</p>", unsafe_allow_html=True)
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
                    else: st.error("بيانات الدخول غير صحيحة")

def main_portal():
    with st.sidebar:
        # 1. الهيدر الجديد الاحترافي
        st.markdown(f'<div class="nasq-logo">Nasq ERP</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="nasq-role">{st.session_state.role} | أهلاً {st.session_state.emp_name}</div>', unsafe_allow_html=True)
        st.divider()
        
        # 2. القائمة المستوحاة من UI الاحترافي (مع الأيقونات)
        if st.session_state.role == "Admin":
            options = ["📊 لوحة القيادة", "🤖 المساعد الذكي", "➕ طلب جديد", "📦 الورشة", "🧾 المالية", "👥 العملاء", "👨‍💼 الفريق", "⚙️ الإعدادات"]
        else:
            options = ["🏠 شاشتي الرئيسية", "🤖 المساعد الذكي"]
            
        choice = st.radio("القائمة:", options, label_visibility="collapsed")
        
        st.divider()
        # 3. زر تسجيل الخروج بتصميم الـ UI الاحترافي
        if st.button("🚪 تسجيل الخروج", use_container_width=True):
            st.session_state.logged_in = False
            st.rerun()

    # الربط البرمجي للشاشات
    mapping = {
        "📊 لوحة القيادة": "dashboard", "🤖 المساعد الذكي": "ai_assistant", "➕ طلب جديد": "new_order",
        "📦 الورشة": "orders", "🧾 المالية": "accounts", "👥 العملاء": "clients",
        "👨‍💼 الفريق": "employees", "⚙️ الإعدادات": "categories", "🏠 شاشتي الرئيسية": "my_screen"
    }
    
    page_key = mapping.get(choice)
    if page_key == "my_screen":
        role = st.session_state.role
        if role == "Designer": PAGES["designer"](conn, st.session_state.emp_name)
        elif role == "Technician": PAGES["tech"](conn, st.session_state.emp_name)
        elif role == "Installer": PAGES["installer"](conn, st.session_state.emp_name)
    elif page_key:
        PAGES[page_key](conn if page_key != "ai_assistant" else None)

# --- 7. التشغيل ---
if not st.session_state.logged_in:
    login_screen()
else:
    main_portal()
