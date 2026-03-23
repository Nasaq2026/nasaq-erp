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

# منع التحذيرات المزعجة
warnings.simplefilter('ignore', UserWarning)

# إعدادات الصفحة الرئيسية
st.set_page_config(
    page_title="نَسق ERP | الإدارة الذكية للمطبوعات", 
    page_icon="🎯", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 2. ستايل "نَسق" الفخم (تم تنظيفه لضمان عدم حدوث أخطاء إزاحة) ---
NASQ_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700;800&display=swap');

html, body, [data-testid="stAppViewContainer"], [data-testid="stSidebar"] {
    direction: rtl;
    text-align: right;
    font-family: 'Cairo', sans-serif !important;
}

/* ستايل القائمة الجانبية */
[data-testid="stSidebar"] {
    background-color: #0f172a !important;
    border-left: 1px solid #1e293b;
}

/* تنسيق الخيارات في القائمة الجانبية */
div[data-testid="stSidebarUserContent"] .stRadio div[role="radiogroup"] {
    display: flex;
    flex-direction: column;
    gap: 12px;
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
    transition: 0.4s all cubic-bezier(0.4, 0, 0.2, 1);
    margin: 0 !important;
    cursor: pointer;
}

/* تأثير عند اختيار العنصر */
div[data-testid="stSidebarUserContent"] .stRadio div[role="radiogroup"] label[data-selected="true"] {
    background-color: #38bdf8 !important;
    color: #0f172a !important;
    font-weight: 800 !important;
    box-shadow: 0 10px 20px rgba(56, 189, 248, 0.4);
    transform: scale(1.02);
}

/* إخفاء الهيدر الافتراضي لستريمليت */
header {visibility: hidden;}
footer {visibility: hidden;}
</style>
"""
st.markdown(NASQ_CSS, unsafe_allow_html=True)

# --- 3. إدارة الاتصال بقاعدة البيانات (Supabase) ---
@st.cache_resource(ttl=300)
def init_connection():
    try:
        # بيانات الربط الخاصة بقاعدة بيانات نَسق
        db_uri = "postgresql://postgres.jfqmcgicbdrhrtkhuwws:Nasaq268609@aws-1-ap-northeast-1.pooler.supabase.com:6543/postgres"
        return psycopg2.connect(db_uri, sslmode="require", connect_timeout=15)
    except Exception as e:
        st.error(f"❌ فشل الاتصال بالسيرفر: {e}")
        return None

conn = init_connection()

# --- 4. محرك تحميل الصفحات الديناميكي ---
def load_system_modules():
    """تحميل كافة موديولات النظام من مجلد web_ui"""
    pages = {}
    # خريطة الربط بين المفتاح الداخلي وبين (مسار الملف، اسم الدالة)
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
            # استيراد الموديول ديناميكياً
            module = __import__(path, fromlist=[func_name])
            pages[key] = getattr(module, func_name)
        except Exception as e:
            # دالة احتياطية في حال تعثر تحميل موديول معين
            pages[key] = lambda *args, **kwargs: st.error(f"⚠️ الموديول '{key}' غير جاهز أو به خطأ برمجبي داخلي.")
            
    return pages

PAGES = load_system_modules()

# --- 5. إدارة الجلسة (Session State) ---
if "logged_in" not in st.session_state:
    st.session_state.update({"logged_in": False, "emp_name": "", "role": "", "emp_id": None})

# --- 6. واجهة تسجيل الدخول ---
def show_login_screen():
    st.write("<br><br><br>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1, 1.5, 1])
    with c2:
        if os.path.exists("logo.png"):
            st.image("logo.png", width=300)
        
        st.subheader("🔐 بوابة دخول نظام نَسق")
        with st.form("login_form"):
            user_serial = st.text_input("رقم الموظف التسلسلي")
            user_pass = st.text_input("كلمة المرور", type="password")
            
            if st.form_submit_button("دخول آمن للنظام", use_container_width=True):
                if conn:
                    cursor = conn.cursor()
                    query = "SELECT emp_name, role, id FROM employees WHERE serial_number = %s AND password = %s"
                    cursor.execute(query, (user_serial, user_pass))
                    user_data = cursor.fetchone()
                    
                    if user_data:
                        st.session_state.update({
                            "logged_in": True, 
                            "emp_name": user_data[0], 
                            "role": user_data[1],
                            "emp_id": user_data[2]
                        })
                        st.success(f"مرحباً بك يا {user_data[0]}")
                        st.rerun()
                    else:
                        st.error("بيانات الدخول غير صحيحة، يرجى التحقق.")
                else:
                    st.warning("تعذر الوصول لقاعدة البيانات حالياً.")

# --- 7. بوابة النظام الرئيسية (بعد الدخول) ---
def show_main_portal():
    with st.sidebar:
        if os.path.exists("logo.png"):
            st.image("logo.png", use_container_width=True)
        
        st.markdown(f"<p style='text-align:center; color:#38bdf8;'>👤 {st.session_state.emp_name}<br><small>({st.session_state.role})</small></p>", unsafe_allow_html=True)
        st.divider()
        
        # بناء القائمة بناءً على الصلاحيات
        if st.session_state.role == "Admin":
            menu_options = [
                "📊 لوحة القيادة", "🤖 المساعد الذكي", "➕ طلب جديد", 
                "📦 الورشة والطلبات", "🧾 الحسابات والتحصيل", "📢 محرك التسويق", 
                "📲 واتساب التحصيل", "👥 قاعدة العملاء", "👨‍💼 إدارة الفريق", "⚙️ الإعدادات"
            ]
        else:
            menu_options = ["🏠 شاشتي الرئيسية", "🤖 المساعد الذكي"]
            
        choice = st.radio("القائمة الرئيسية:", menu_options, label_visibility="collapsed")
        
        st.divider()
        if st.button("🚪 تسجيل الخروج", use_container_width=True):
            st.session_state.logged_in = False
            st.rerun()

    # خريطة توجيه القائمة (Navigation Logic)
    nav_map = {
        "📊 لوحة القيادة": "dashboard",
        "🤖 المساعد الذكي": "ai_assistant",
        "➕ طلب جديد": "new_order",
        "📦 الورشة والطلبات": "orders",
        "🧾 الحسابات والتحصيل": "accounts",
        "📢 محرك التسويق": "marketing",
        "📲 واتساب التحصيل": "whatsapp",
        "👥 قاعدة العملاء": "clients",
        "👨‍💼 إدارة الفريق": "employees",
        "⚙️ الإعدادات": "categories",
        "🏠 شاشتي الرئيسية": "my_role_screen"
    }
    
    selected_page = nav_map.get(choice)
    
    # تنفيذ عرض الصفحة المختارة
    if selected_page == "my_role_screen":
        role = st.session_state.role
        if role == "Designer": PAGES["designer"](conn, st.session_state.emp_name)
        elif role == "Technician": PAGES["tech"](conn, st.session_state.emp_name)
        elif role == "Installer": PAGES["installer"](conn, st.session_state.emp_name)
        else: st.info("لا توجد شاشة مخصصة لهذا الدور، يرجى مراجعة المسؤول.")
    elif selected_page:
        # الصفحات التي تحتاج اتصال قاعدة البيانات
        if selected_page == "ai_assistant":
            PAGES[selected_page]()
        else:
            PAGES[selected_page](conn)

# --- 8. نقطة التشغيل النهائية ---
if not st.session_state.logged_in:
    show_login_screen()
else:
    show_main_portal()
