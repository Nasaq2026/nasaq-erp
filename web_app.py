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
    page_title="نَسق ERP | الإدارة الذكية", 
    page_icon="🎯", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 3. ستايل نَسق الأصلي (تنظيم ووضوح عالي) ---
def inject_nasq_stable_css():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700;800&display=swap');
    
    /* الخط العربي والاتجاه الصارم لليمين */
    html, body, [data-testid="stSidebar"] *, .stMarkdown {
        font-family: 'Cairo', sans-serif !important;
        direction: rtl;
        text-align: right;
    }

    /* القائمة الجانبية الأصلية بلون داكن ملكي */
    [data-testid="stSidebar"] {
        background-color: #0f172a !important;
        border-left: 1px solid #1e293b;
    }

    /* تنسيق نصوص القائمة لتكون بيضاء وواضحة جداً */
    div[data-testid="stSidebarUserContent"] .stRadio div[role="radiogroup"] label {
        color: #ffffff !important;
        font-size: 16px !important;
        font-weight: 600 !important;
        background-color: #1e293b;
        padding: 12px 15px !important;
        border-radius: 8px;
        margin-bottom: 8px;
        border: 1px solid #334155;
        transition: 0.3s;
    }

    /* تمييز الخيار المختار */
    div[data-testid="stSidebarUserContent"] .stRadio div[role="radiogroup"] label[data-selected="true"] {
        background-color: #38bdf8 !important;
        color: #0f172a !important;
        border-color: #38bdf8;
    }

    /* إخفاء الهيدر الافتراضي المزعج */
    header {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

inject_nasq_stable_css()

# --- 4. الاتصال بقاعدة البيانات ---
@st.cache_resource(ttl=60)
def init_connection():
    try:
        db_uri = "postgresql://postgres.jfqmcgicbdrhrtkhuwws:Nasaq268609@aws-1-ap-northeast-1.pooler.supabase.com:6543/postgres"
        conn = psycopg2.connect(db_uri, sslmode="require", connect_timeout=15)
        return conn
    except: return None

conn = init_connection()

# --- 5. تحميل الصفحات بأمان ---
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
        except:
            pages[key] = lambda *args, **kwargs: st.error(f"⚠️ الملف {key} غير متوفر حالياً")
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
        else:
            st.markdown("<h1 style='text-align:center; color:#38bdf8;'>نَسق ERP</h1>", unsafe_allow_html=True)
            
        with st.form("login_form"):
            serial = st.text_input("رقم الموظف")
            pwd = st.text_input("كلمة المرور", type="password")
            if st.form_submit_button("دخول آمن", width='stretch'):
                if conn:
                    cursor = conn.cursor()
                    cursor.execute("SELECT emp_name, role FROM employees WHERE serial_number = %s AND password = %s", (serial, pwd))
                    user = cursor.fetchone()
                    if user:
                        st.session_state.update({"logged_in": True, "emp_name": user[0], "role": user[1]})
                        st.rerun()
                    else: st.error("عذراً، بيانات الدخول غير صحيحة")

# --- 7. الهيدر العلوي المستقر ---
def render_top_header():
    col_l, col_r = st.columns([1, 1])
    with col_r:
        st.markdown(f"""
            <div style="background:#1e293b; padding:10px 20px; border-radius:12px; border-right:5px solid #38bdf8; text-align:right;">
                <span style="color:#ffffff; font-weight:bold; font-size:16px;">👤 أهلاً بك، {st.session_state.emp_name}</span><br>
                <small style="color:#94a3b8;">رتبة الوصول: {st.session_state.role}</small>
            </div>
        """, unsafe_allow_html=True)
    with col_l:
        # مساحة للأيقونات مستقبلاً بشكل هادئ
        st.write("")

# --- 8. بوابة النظام الرئيسية ---
def main_portal():
    render_top_header()
    
    with st.sidebar:
        # عرض اللوجو الأصلي logo.png في مكانه الصحيح
        if os.path.exists("logo.png"):
            st.image("logo.png", width='stretch')
        else:
            st.markdown("<h2 style='color:#38bdf8; text-align:center;'>نَسق | NASAQ</h2>", unsafe_allow_html=True)
        
        st.divider()
        
        # القائمة الجانبية المنظمة
        if st.session_state.role == "Admin":
            options = ["📊 لوحة القيادة", "🤖 المساعد الذكي", "➕ طلب جديد", "📦 الورشة", "🧾 المالية", "👥 العملاء", "👨‍💼 الفريق", "⚙️ الإعدادات"]
        else:
            options = ["🏠 شاشتي الرئيسية", "🤖 المساعد الذكي"]
            
        choice = st.radio("القائمة الرئيسية", options, label_visibility="collapsed")
        
        st.divider()
        if st.button("🚪 تسجيل الخروج", width='stretch'):
            st.session_state.logged_in = False
            st.rerun()

    # الربط البرمجي بين الخيارات والصفحات
    mapping = {
        "📊 لوحة القيادة": "dashboard", "🤖 المساعد الذكي": "ai_assistant", "➕ طلب جديد": "new_order",
        "📦 الورشة": "orders", "🧾 المالية": "accounts", "👥 العملاء": "clients",
        "👨‍💼 الفريق": "employees", "⚙️ الإعدادات": "categories", "🏠 شاشتي الرئيسية": "my_screen"
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

# --- تشغيل البرنامج ---
if not st.session_state.logged_in:
    login_screen()
else:
    main_portal()
