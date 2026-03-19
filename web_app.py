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

# --- 2. تهيئة الإعدادات ---
warnings.simplefilter('ignore', UserWarning)
st.set_page_config(
    page_title="Nasq ERP | PRO 2026", 
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
            pages[key] = lambda *args, **kwargs: st.error(f"❌ خطأ في تحميل {key}")
    return pages

PAGES = load_system_pages()

# --- 4. ستايل NASAQ PRO (UI الملكي المطور) ---
def inject_nasq_pro_css():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700;800&display=swap');
    
    html, body, [data-testid="stSidebar"] *, .stMarkdown, p, h1, h2, h3 {
        font-family: 'Cairo', sans-serif !important;
        direction: rtl; text-align: right;
    }

    /* الهيدر العلوي الاحترافي */
    .top-bar {
        display: flex; justify-content: space-between; align-items: center;
        padding: 10px 25px; background: rgba(15, 23, 42, 0.6);
        backdrop-filter: blur(12px); border-radius: 15px;
        border: 1px solid rgba(56, 189, 248, 0.2); margin-bottom: 25px;
    }
    .top-bar-icons { display: flex; gap: 20px; align-items: center; }
    .icon-wrapper { position: relative; font-size: 22px; cursor: pointer; transition: 0.3s; }
    .icon-wrapper:hover { transform: scale(1.1); color: #38bdf8; }
    .badge-pro {
        position: absolute; top: -5px; right: -8px; background: #ef4444;
        color: white; font-size: 10px; padding: 1px 5px; border-radius: 50%; border: 1px solid #0f172a;
    }

    /* القائمة الجانبية الفخمة */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0f172a 0%, #1e293b 100%) !important;
        border-left: 1px solid rgba(56, 189, 248, 0.1);
    }

    /* أزرار القائمة التفاعلية */
    div[data-testid="stSidebarUserContent"] .stRadio div[role="radiogroup"] label {
        background-color: transparent !important; border: none !important;
        padding: 12px 20px !important; border-radius: 12px !important;
        margin-bottom: 4px !important; color: rgba(255, 255, 255, 0.7) !important;
        transition: all 0.3s ease;
    }
    div[data-testid="stSidebarUserContent"] .stRadio div[role="radiogroup"] label[data-selected="true"] {
        background: rgba(56, 189, 248, 0.15) !important;
        color: #38bdf8 !important; font-weight: 700 !important;
        border-right: 4px solid #38bdf8 !important;
    }
    div[data-testid="stRadioButtonCustomObject"] { display: none !important; }

    /* الإشعارات العائمة الزجاجية */
    .glass-notif {
        position: fixed; top: 80px; left: 20px; width: 280px;
        background: rgba(30, 41, 59, 0.7); backdrop-filter: blur(10px);
        border: 1px solid rgba(56, 189, 248, 0.3); border-radius: 12px;
        padding: 15px; z-index: 1000; animation: slideIn 0.5s ease;
        box-shadow: 0 8px 32px rgba(0,0,0,0.3);
    }
    @keyframes slideIn { from { transform: translateX(-110%); } to { transform: translateX(0); } }

    header {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

inject_nasq_pro_css()

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

# --- 6. مكونات الواجهة الاحترافية (الهيدر والإشعارات) ---
def render_top_bar():
    col_empty, col_info = st.columns([2, 1])
    with col_info:
        st.markdown(f"""
            <div class="top-bar">
                <div class="top-bar-icons">
                    <div class="icon-wrapper">📩<span class="badge-pro">3</span></div>
                    <div class="icon-wrapper">🔔<span class="badge-pro">1</span></div>
                </div>
                <div style="display: flex; align-items: center; gap: 10px;">
                    <div style="text-align: left;">
                        <div style="color: #38bdf8; font-weight: bold; font-size: 14px;">{st.session_state.emp_name}</div>
                        <div style="color: #94a3b8; font-size: 11px;">المدير العام</div>
                    </div>
                    <div style="font-size: 24px;">👤</div>
                </div>
            </div>
        """, unsafe_allow_html=True)

def show_floating_notification():
    # نظام محاكاة لإشعار انتهاء العمل (يمكن ربطه بالداتابيز)
    if st.session_state.role == "Admin":
        st.markdown("""
            <div class="glass-notif">
                <div style="display: flex; align-items: center; gap: 10px;">
                    <span style="font-size: 20px;">✅</span>
                    <div>
                        <b style="color: #38bdf8;">تنبيه الإنتاج</b><br>
                        <small style="color: #cbd5e1;">أنهى المصمم <b>أحمد</b> عمل الطلب #1045</small>
                    </div>
                </div>
            </div>
        """, unsafe_allow_html=True)

# --- 7. المراسلات الداخلية (تظهر في كل الصفحات) ---
def render_internal_chat():
    with st.sidebar:
        st.divider()
        with st.expander("💬 مراسلات الفريق الداخلية", expanded=False):
            st.markdown("<small style='color:#94a3b8;'>محادثة مشفرة داخل المؤسسة</small>", unsafe_allow_html=True)
            st.text_area("الرسائل الجارية...", value="أدمن: يا شباب الطلب #1042 مستعجل\nمصمم: جاري العمل عليه يا فندم", height=100, disabled=True)
            msg = st.text_input("اكتب رسالتك...", key="chat_input")
            if st.button("إرسال 🚀", width='stretch'):
                st.toast("تم الإرسال للفريق!")

# --- 8. شاشة الدخول ---
def login_screen():
    st.write("<br><br><br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        st.markdown('<h1 style="color:#38bdf8; text-align:center;">NASAQ ERP</h1>', unsafe_allow_html=True)
        with st.form("login"):
            serial = st.text_input("رقم الموظف")
            password = st.text_input("كلمة المرور", type="password")
            if st.form_submit_button("دخول آمن 🚀", width="stretch"):
                if conn:
                    cursor = conn.cursor()
                    cursor.execute("SELECT emp_name, role FROM employees WHERE serial_number = %s AND password = %s", (serial, password))
                    user = cursor.fetchone()
                    if user:
                        st.session_state.update({"logged_in": True, "emp_name": user[0], "role": user[1]})
                        st.rerun()
                    else: st.error("بيانات خاطئة")

# --- 9. بوابات النظام ---
def main_portal():
    # عرض العناصر العلوية
    render_top_bar()
    show_floating_notification()
    render_internal_chat()
    
    with st.sidebar:
        st.markdown('<h2 style="color: #38bdf8; text-align: center; margin-bottom:0;">NASAQ PRO</h2>', unsafe_allow_html=True)
        st.markdown(f"<p style='text-align:center; color:#94a3b8; font-size:12px;'>نظام الإدارة المتكامل 2026</p>", unsafe_allow_html=True)
        st.divider()
        
        if st.session_state.role == "Admin":
            options = ["📊 لوحة القيادة", "🤖 المساعد الذكي", "➕ طلب جديد", "📦 الورشة", "🧾 المالية", "👥 العملاء", "👨‍💼 الفريق", "⚙️ الإعدادات"]
        else:
            options = ["🏠 شاشتي الرئيسية", "🤖 المساعد الذكي"]
            
        choice = st.radio("القائمة:", options, label_visibility="collapsed")
        
        st.divider()
        if st.button("🚪 تسجيل الخروج", width="stretch"):
            st.session_state.logged_in = False
            st.rerun()

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

# --- 10. التشغيل ---
if not st.session_state.logged_in:
    login_screen()
else:
    main_portal()
