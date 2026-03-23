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
st.set_page_config(page_title="نَسق ERP | الإدارة الذكية", page_icon="🎯", layout="wide", initial_sidebar_state="expanded")

# --- 3. ستايل نَسق (نسخة مضغوطة لتفادي أخطاء الإزاحة 100%) ---
NASQ_CSS = "<style>@import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700;800&display=swap');html,body,[data-testid='stAppViewContainer'],[data-testid='stSidebar']{direction:rtl;text-align:right;font-family:'Cairo',sans-serif!important;}[data-testid='stSidebar']{background-color:#0f172a!important;border-left:1px solid #1e293b;}div[data-testid='stSidebarUserContent'] .stRadio div[role='radiogroup']{display:flex;flex-direction:column;gap:8px;padding:0 10px;}div[data-testid='stSidebarUserContent'] .stRadio div[role='radiogroup'] label{color:white!important;background-color:rgba(255,255,255,0.05)!important;border:1px solid rgba(255,255,255,0.1)!important;padding:15px 20px!important;border-radius:12px!important;width:100%!important;display:flex!important;align-items:center;transition:0.3s all ease;margin:0!important;}div[data-testid='stSidebarUserContent'] .stRadio div[role='radiogroup'] label[data-selected='true']{background-color:#38bdf8!important;color:#0f172a!important;font-weight:700!important;}header{visibility:hidden;}</style>"
st.markdown(NASQ_CSS, unsafe_allow_html=True)

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
        "marketing": ("web_ui.marketing", "render_marketing"),
        "whatsapp": ("web_ui.whatsapp_sender", "render_whatsapp_sender"),
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
        except Exception as e:
            pages[key] = lambda *args, **kwargs: st.error(f"⚠️ خطأ تحميل {key}: {e}")
    return pages

PAGES = load_system_pages()

if "logged_in" not in st.session_state:
    st.session_state.update({"logged_in": False, "emp_name": "", "role": ""})

# --- 6. بوابة الدخول ---
def login_screen():
    st.write("<br><br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 1.2, 1])
    with col2:
        if os.path.exists("logo.png"): st.image("logo.png", width=250)
        with st.form("login"):
            u = st.text_input("رقم الموظف")
            p = st.text_input("كلمة المرور", type="password")
            if st.form_submit_button("دخول", use_container_width=True):
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
        if os.path.exists("logo.png"): st.image("logo.png", width='stretch')
        st.divider()
        if st.session_state.role == "Admin":
            options = ["📊 لوحة القيادة", "🤖 المساعد الذكي", "➕ طلب جديد", "📦 الورشة", "🧾 الحسابات", "📢 التسويق", "📲 واتساب التحصيل", "👥 العملاء", "👨‍💼 الفريق", "⚙️ الإعدادات"]
        else:
            options = ["🏠 شاشتي الرئيسية", "🤖 المساعد الذكي"]
        choice = st.radio("القائمة:", options, label_visibility="collapsed")
        st.divider()
        if st.button("🚪 خروج", use_container_width=True):
            st.session_state.logged_in = False
            st.rerun()

    mapping = {
        "📊 لوحة القيادة": "dashboard", "🤖 المساعد الذكي": "ai_assistant", "➕ طلب جديد": "new_order",
        "📦 الورشة": "orders", "🧾 الحسابات": "accounts", "📢 التسويق": "marketing",
        "📲 واتساب التحصيل": "whatsapp", "👥 العملاء": "clients", "👨‍💼 الفريق": "employees", 
        "⚙️ الإعدادات": "categories", "🏠 شاشتي الرئيسية": "my_screen"
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
if not st.session_state.logged_in: login_screen()
else: main_portal()
flex-direction: column; 
gap: 8px; 
padding: 0 10px;
}
div[data-testid="stSidebarUserContent"] .stRadio div[role="radiogroup"] label {
color: white !important; 
background-color: rgba(255, 255, 255, 0.05) !important;
border: 1px solid rgba(255, 255, 255, 0.1) !important; 
padding: 15px 20px !important;
border-radius: 12px !important; 
width: 100% !important; 
display: flex !important;
align-items: center; 
transition: 0.3s all ease; 
margin: 0 !important;
}
div[data-testid="stSidebarUserContent"] .stRadio div[role="radiogroup"] label[data-selected="true"] {
background-color: #38bdf8 !important; 
color: #0f172a !important; 
font-weight: 700 !important;
}
header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

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
        "marketing": ("web_ui.marketing", "render_marketing"),
        "whatsapp": ("web_ui.whatsapp_sender", "render_whatsapp_sender"),
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
        except Exception as e:
            pages[key] = lambda *args, **kwargs: st.error(f"⚠️ خطأ تحميل {key}: {e}")
    return pages

PAGES = load_system_pages()

if "logged_in" not in st.session_state:
    st.session_state.update({"logged_in": False, "emp_name": "", "role": ""})

# --- 6. بوابة الدخول ---
def login_screen():
    st.write("<br><br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 1.2, 1])
    with col2:
        if os.path.exists("logo.png"): st.image("logo.png", width=250)
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
        if os.path.exists("logo.png"): st.image("logo.png", width='stretch')
        st.divider()
        if st.session_state.role == "Admin":
            options = ["📊 لوحة القيادة", "🤖 المساعد الذكي", "➕ طلب جديد", "📦 الورشة", "🧾 الحسابات", "📢 التسويق", "📲 واتساب التحصيل", "👥 العملاء", "👨‍💼 الفريق", "⚙️ الإعدادات"]
        else:
            options = ["🏠 شاشتي الرئيسية", "🤖 المساعد الذكي"]
        choice = st.radio("القائمة:", options, label_visibility="collapsed")
        st.divider()
        if st.button("🚪 خروج", width='stretch'):
            st.session_state.logged_in = False
            st.rerun()

    mapping = {
        "📊 لوحة القيادة": "dashboard", "🤖 المساعد الذكي": "ai_assistant", "➕ طلب جديد": "new_order",
        "📦 الورشة": "orders", "🧾 الحسابات": "accounts", "📢 التسويق": "marketing",
        "📲 واتساب التحصيل": "whatsapp", "👥 العملاء": "clients", "👨‍💼 الفريق": "employees", 
        "⚙️ الإعدادات": "categories", "🏠 شاشتي الرئيسية": "my_screen"
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

if not st.session_state.logged_in: login_screen()
else: main_portal()
        align-items: center; transition: 0.3s all ease; margin: 0 !important;
    }
    div[data-testid="stSidebarUserContent"] .stRadio div[role="radiogroup"] label[data-selected="true"] {
        background-color: #38bdf8 !important; color: #0f172a !important; font-weight: 700 !important;
    }
    header {visibility: hidden;}
</style>
"""
st.markdown(NASQ_STYLE, unsafe_allow_html=True)

# --- 4. الاتصال بقاعدة البيانات ---
@st.cache_resource(ttl=60)
def init_connection():
    try:
        db_uri = "postgresql://postgres.jfqmcgicbdrhrtkhuwws:Nasaq268609@aws-1-ap-northeast-1.pooler.supabase.com:6543/postgres"
        return psycopg2.connect(db_uri, sslmode="require", connect_timeout=15)
    except: return None

conn = init_connection()

# --- 5. تحميل الصفحات (تأكد من مطابقة أسماء الدوال) ---
def load_system_pages():
    pages = {}
    modules = {
        "dashboard": ("web_ui.dashboard", "render_dashboard"),
        "ai_assistant": ("web_ui.ai_assistant", "render_ai_assistant"),
        "new_order": ("web_ui.new_order", "render_new_order"),
        "orders": ("web_ui.orders", "render_orders"),
        "accounts": ("web_ui.accounts", "render_accounts"), # صفحة الحسابات
        "marketing": ("web_ui.marketing", "render_marketing"), # صفحة التسويق
        "whatsapp": ("web_ui.whatsapp_sender", "render_whatsapp_sender"), # صفحة التحصيل
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
        except Exception as e:
            pages[key] = lambda *args, **kwargs: st.error(f"⚠️ خطأ في تحميل {key}: {e}")
    return pages

PAGES = load_system_pages()

if "logged_in" not in st.session_state:
    st.session_state.update({"logged_in": False, "emp_name": "", "role": ""})

# --- 6. الدخول والمنصة ---
def login_screen():
    st.write("<br><br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 1.2, 1])
    with col2:
        if os.path.exists("logo.png"): st.image("logo.png", width=250)
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

def main_portal():
    with st.sidebar:
        if os.path.exists("logo.png"): st.image("logo.png", width='stretch')
        st.divider()
        if st.session_state.role == "Admin":
            options = ["📊 لوحة القيادة", "🤖 المساعد الذكي", "➕ طلب جديد", "📦 الورشة", "🧾 الحسابات", "📢 التسويق", "📲 واتساب التحصيل", "👥 العملاء", "👨‍💼 الفريق", "⚙️ الإعدادات"]
        else:
            options = ["🏠 شاشتي الرئيسية", "🤖 المساعد الذكي"]
        choice = st.radio("القائمة:", options, label_visibility="collapsed")
        st.divider()
        if st.button("🚪 خروج", width='stretch'):
            st.session_state.logged_in = False
            st.rerun()

    mapping = {
        "📊 لوحة القيادة": "dashboard", "🤖 المساعد الذكي": "ai_assistant", "➕ طلب جديد": "new_order",
        "📦 الورشة": "orders", "🧾 الحسابات": "accounts", "📢 التسويق": "marketing",
        "📲 واتساب التحصيل": "whatsapp", "👥 العملاء": "clients", "👨‍💼 الفريق": "employees", 
        "⚙️ الإعدادات": "categories", "🏠 شاشتي الرئيسية": "my_screen"
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

if not st.session_state.logged_in: login_screen()
else: main_portal()

    div[data-testid="stSidebarUserContent"] .stRadio div[role="radiogroup"] {
        display: flex;
        flex-direction: column;
        gap: 8px;
        padding: 0 10px;
    }

    div[data-testid="stSidebarUserContent"] .stRadio div[role="radiogroup"] label {
        color: white !important;
        background-color: rgba(255, 255, 255, 0.05) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        padding: 15px 20px !important;
        border-radius: 12px !important;
        width: 100% !important;
        display: flex !important;
        align-items: center;
        transition: 0.3s all ease;
        margin: 0 !important;
    }

    div[data-testid="stSidebarUserContent"] .stRadio div[role="radiogroup"] label[data-selected="true"] {
        background-color: #38bdf8 !important;
        color: #0f172a !important;
        border-color: #38bdf8 !important;
        font-weight: 700 !important;
        box-shadow: 0 4px 15px rgba(56, 189, 248, 0.3);
    }

    header {visibility: hidden;}
</style>
"""

st.markdown(NASQ_CSS, unsafe_allow_html=True)

# --- 4. الاتصال بقاعدة البيانات ---
@st.cache_resource(ttl=60)
def init_connection():
    try:
        db_uri = "postgresql://postgres.jfqmcgicbdrhrtkhuwws:Nasaq268609@aws-1-ap-northeast-1.pooler.supabase.com:6543/postgres"
        return psycopg2.connect(db_uri, sslmode="require", connect_timeout=15)
    except:
        return None

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
        "marketing": ("web_ui.marketing", "render_marketing"),
        "whatsapp": ("web_ui.whatsapp_sender", "render_whatsapp_sender"),
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
        except:
            pages[key] = lambda *args, **kwargs: st.error(f"⚠️ الملف {key} مفقود")
    return pages

PAGES = load_system_pages()

if "logged_in" not in st.session_state:
    st.session_state.update({"logged_in": False, "emp_name": "", "role": ""})

# --- 6. شاشة الدخول ---
def login_screen():
    st.write("<br><br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 1.2, 1])
    with col2:
        if os.path.exists("logo.png"):
            st.image("logo.png", width=250)
        with st.form("login_form"):
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
                    else:
                        st.error("بيانات خاطئة")

# --- 7. بوابة النظام الرئيسية ---
def main_portal():
    with st.sidebar:
        if os.path.exists("logo.png"):
            st.image("logo.png", width='stretch')
        st.divider()
        
        if st.session_state.role == "Admin":
            options = ["📊 لوحة القيادة", "🤖 المساعد الذكي", "➕ طلب جديد", "📦 الورشة", "🧾 المالية", "📢 التسويق", "📲 واتساب التحصيل", "👥 العملاء", "👨‍💼 الفريق", "⚙️ الإعدادات"]
        else:
            options = ["🏠 شاشتي الرئيسية", "🤖 المساعد الذكي"]
            
        choice = st.radio("القائمة:", options, label_visibility="collapsed")
        
        st.divider()
        if st.button("🚪 خروج", width='stretch'):
            st.session_state.logged_in = False
            st.rerun()

    mapping = {
        "📊 لوحة القيادة": "dashboard", "🤖 المساعد الذكي": "ai_assistant", "➕ طلب جديد": "new_order",
        "📦 الورشة": "orders", "🧾 المالية": "accounts", "📢 التسويق": "marketing",
        "📲 واتساب التحصيل": "whatsapp", "👥 العملاء": "clients", "👨‍💼 الفريق": "employees", 
        "⚙️ الإعدادات": "categories", "🏠 شاشتي الرئيسية": "my_screen"
    }
    
    page_key = mapping.get(choice)
    
    if page_key == "ai_assistant":
        PAGES["ai_assistant"]()
    elif page_key == "my_screen":
        role = st.session_state.role
        if role == "Designer": PAGES["designer"](conn, st.session_state.emp_name)
        elif role == "Technician": PAGES["tech"](conn, st.session_state.emp_name)
        elif role == "Installer": PAGES["installer"](conn, st.session_state.emp_name)
    elif page_key:
        PAGES[page_key](conn)

# --- 8. التشغيل ---
if not st.session_state.logged_in:
    login_screen()
else:
    main_portal()
