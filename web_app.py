import streamlit as st
import os
import sys
import warnings
import psycopg2
from datetime import datetime

# --- 1. تهيئة المسارات وبيئة العمل ---
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

# تجاهل التحذيرات غير الهامة
warnings.simplefilter('ignore', UserWarning)

st.set_page_config(
    page_title="نَسق ERP | الإدارة الذكية", 
    page_icon="🎯", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 2. ستايل نَسق الاحترافي المطور (Master CSS) ---
NASQ_UI_THEME = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700;800&display=swap');

/* ضبط الاتجاه العام والخطوط */
html, body, [data-testid="stAppViewContainer"], [data-testid="stSidebar"] {
    direction: rtl;
    text-align: right;
    font-family: 'Cairo', sans-serif !important;
}

/* تصميم القائمة الجانبية الفاخرة */
[data-testid="stSidebar"] {
    background-color: #0b1329 !important; /* لون كحلي داكن ملكي */
    border-left: 1px solid #1e293b;
}

/* تمديد وتنسيق الأزرار (Radio buttons) جهة اليسار بالكامل */
div[data-testid="stSidebarUserContent"] .stRadio div[role="radiogroup"] {
    display: flex;
    flex-direction: column;
    gap: 10px;
    padding: 0 12px;
}

div[data-testid="stSidebarUserContent"] .stRadio div[role="radiogroup"] label {
    color: #e2e8f0 !important;
    background-color: rgba(255, 255, 255, 0.03) !important;
    border: 1px solid rgba(255, 255, 255, 0.08) !important;
    padding: 14px 18px !important;
    border-radius: 12px !important;
    width: 100% !important;
    display: flex !important;
    align-items: center;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    margin: 0 !important;
    cursor: pointer;
}

/* تأثير الإضاءة والظل عند تمرير الماوس */
div[data-testid="stSidebarUserContent"] .stRadio div[role="radiogroup"] label:hover {
    background-color: rgba(56, 189, 248, 0.1) !important;
    border-color: rgba(56, 189, 248, 0.4) !important;
    transform: translateX(-3px); /* حركة انزلاقية خفيفة لليسار */
}

/* تمييز الخيار النشط (Active) */
div[data-testid="stSidebarUserContent"] .stRadio div[role="radiogroup"] label[data-selected="true"] {
    background: linear-gradient(135deg, #38bdf8 0%, #0284c7 100%) !important;
    color: #0f172a !important;
    font-weight: 800 !important;
    box-shadow: 0 8px 25px rgba(56, 189, 248, 0.3);
}

/* إخفاء الزوائد الافتراضية في Streamlit لتبدو كبرنامج حقيقي */
header {visibility: hidden;}
footer {visibility: hidden;}
[data-testid="stHeader"] {background: rgba(0,0,0,0);}
</style>
"""
st.markdown(NASQ_UI_THEME, unsafe_allow_html=True)


# --- 3. إدارة الاتصال بقاعدة البيانات (DB) ---
@st.cache_resource(ttl=60)
def init_connection():
    try:
        db_uri = "postgresql://postgres.jfqmcgicbdrhrtkhuwws:Nasaq268609@aws-1-ap-northeast-1.pooler.supabase.com:6543/postgres"
        return psycopg2.connect(db_uri, sslmode="require", connect_timeout=15)
    except:
        return None

conn = init_connection()


# --- 4. محرك استدعاء الصفحات التلقائي ---
def load_system_modules():
    pages = {}
    modules_map = {
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
    
    for key, (path, func_name) in modules_map.items():
        try:
            module = __import__(path, fromlist=[func_name])
            pages[key] = getattr(module, func_name)
        except Exception:
            pages[key] = lambda *args, **kwargs: st.error(f"⚠️ الموديول {key} يحتاج تحديث في مجلد web_ui")
            
    return pages

PAGES = load_system_modules()

if "logged_in" not in st.session_state:
    st.session_state.update({"logged_in": False, "emp_name": "", "role": ""})


# --- 5. دالة التحية الذكية ---
def get_time_greeting():
    now_hour = datetime.now().hour
    if now_hour < 12:
        return "صباح الخير"
    elif now_hour < 18:
        return "مساء الخير"
    else:
        return "تمنياتنا بليلة سعيدة"


# --- 6. واجهة تسجيل الدخول (تصميم احترافي) ---
def show_login_screen():
    st.write("<br><br><br>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1, 1.3, 1])
    with c2:
        if os.path.exists("logo.png"):
            st.image("logo.png", width=280)
        else:
            st.markdown("<h1 style='text-align:center; color:#38bdf8;'>نَسق للإعلان</h1>", unsafe_allow_html=True)
        
        st.markdown("""
        <div style="background:#1e293b; padding:20px; border-radius:15px; border-bottom:4px solid #38bdf8; text-align:center;">
            <span style="color:white; font-size:18px; font-weight:bold;">🔐 بوابة الدخول الآمن</span>
        </div>
        """, unsafe_allow_html=True)
        
        with st.form("login_form"):
            serial = st.text_input("رقم الموظف التسلسلي")
            pwd = st.text_input("كلمة المرور", type="password")
            if st.form_submit_button("دخول للنظام 🚀", use_container_width=True):
                if conn:
                    cursor = conn.cursor()
                    cursor.execute("SELECT emp_name, role FROM employees WHERE serial_number = %s AND password = %s", (serial, pwd))
                    user = cursor.fetchone()
                    if user:
                        st.session_state.update({"logged_in": True, "emp_name": user[0], "role": user[1]})
                        st.rerun()
                    else:
                        st.error("رقم الموظف أو كلمة المرور غير صحيحة.")
                else:
                    st.error("تعذر الاتصال بالسيرفر، يرجى المحاولة لاحقاً.")


# --- 7. البوابة والواجهة الرئيسية (Master Portal) ---
def show_main_portal():
    # التحية والبيانات أعلى الصفحة
    greeting = get_time_greeting()
    
    # بناء القائمة الجانبية
    with st.sidebar:
        if os.path.exists("logo.png"):
            st.image("logo.png", use_container_width=True)
        st.divider()
        
        # مؤشر حالة الاتصال بالسيرفر (إضافة مميزة)
        status_color = "🟢 متصل بالسيرفر" if conn else "🔴 غير متصل بالسيرفر"
        st.markdown(f"""
        <div style="background: rgba(255,255,255,0.05); padding:10px; border-radius:10px; text-align:center;">
            <small style="color:#94a3b8;">{greeting}، {st.session_state.emp_name}</small><br>
            <span style="color:#38bdf8; font-weight:bold; font-size:12px;">{status_color}</span>
        </div>
        """, unsafe_allow_html=True)
        st.divider()
        
        # بناء القائمة بناءً على الصلاحيات
        if st.session_state.role == "Admin":
            menu = ["📊 لوحة القيادة", "🤖 المساعد الذكي", "➕ طلب جديد", "📦 الورشة", "🧾 الحسابات", "📢 التسويق", "📲 واتساب التحصيل", "👥 العملاء", "👨‍💼 الفريق", "⚙️ الإعدادات"]
        else:
            menu = ["🏠 شاشتي الرئيسية", "🤖 المساعد الذكي"]
            
        choice = st.radio("القائمة", menu, label_visibility="collapsed")
        
        st.divider()
        if st.button("🚪 تسجيل الخروج", use_container_width=True):
            st.session_state.logged_in = False
            st.rerun()

    # خريطة توجيه الخيارات للغات البرمجية
    nav_map = {
        "📊 لوحة القيادة": "dashboard", 
        "🤖 المساعد الذكي": "ai_assistant", 
        "➕ طلب جديد": "new_order",
        "📦 الورشة": "orders", 
        "🧾 الحسابات": "accounts", 
        "📢 التسويق": "marketing",
        "📲 واتساب التحصيل": "whatsapp", 
        "👥 العملاء": "clients", 
        "👨‍💼 الفريق": "employees", 
        "⚙️ الإعدادات": "categories", 
        "🏠 شاشتي الرئيسية": "my_screen"
    }
    
    selected_key = nav_map.get(choice)
    
    # هيدر الصفحة الحالية (إضافة مميزة)
    st.markdown(f"""
    <div style="background:#0f172a; padding:15px 25px; border-radius:12px; border-right:5px solid #38bdf8; margin-bottom:20px;">
        <span style="color:#ffffff; font-size:20px; font-weight:bold;">📍 الواجهة الحالية: {choice}</span>
    </div>
    """, unsafe_allow_html=True)

    # تشغيل الصفحات
    if selected_key == "ai_assistant":
        PAGES["ai_assistant"]()
    elif selected_key == "my_screen":
        role = st.session_state.role
        if role == "Designer": PAGES["designer"](conn, st.session_state.emp_name)
        elif role == "Technician": PAGES["tech"](conn, st.session_state.emp_name)
        elif role == "Installer": PAGES["installer"](conn, st.session_state.emp_name)
        else: st.info("لا توجد واجهة مخصصة لهذه الرتبة، مراجعة الإدارة.")
    elif selected_key:
        PAGES[selected_key](conn)


# --- 8. نقطة البداية ---
if not st.session_state.logged_in:
    show_login_screen()
else:
    show_main_portal()
