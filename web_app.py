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

# --- 2. تهيئة الإعدادات الفخمة ---
warnings.simplefilter('ignore', UserWarning)
st.set_page_config(
    page_title="Nasq ERP | الملكي", 
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
            pages[key] = lambda *args: st.error(f"❌ ملف {key} يحتاج تحديث")
    return pages

PAGES = load_system_pages()

# --- 4. ستايل "نَسق PRO" المطور (CSS احترافي جداً) ---
def inject_nasq_royal_css():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700;800&display=swap');
    
    /* الأساسيات والخطوط العربية */
    html, body, [data-testid="stSidebar"] *, .stMarkdown, p, h1, h2, h3, label {
        font-family: 'Cairo', sans-serif !important;
        direction: rtl; text-align: right;
    }

    /* القائمة الجانبية الزجاجية الداكنة */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0f172a 0%, #1e293b 100%) !important;
        border-left: 1px solid rgba(56, 189, 248, 0.15);
    }

    /* خيارات القائمة (تصميم احترافي بلون عربي واضح) */
    div[data-testid="stSidebarUserContent"] .stRadio div[role="radiogroup"] label {
        background-color: rgba(255, 255, 255, 0.03) !important;
        border: 1px solid rgba(255, 255, 255, 0.05) !important;
        padding: 12px 20px !important;
        border-radius: 12px !important;
        margin-bottom: 8px !important;
        color: #e2e8f0 !important; /* لون أبيض مريح */
        transition: 0.3s;
    }

    div[data-testid="stSidebarUserContent"] .stRadio div[role="radiogroup"] label[data-selected="true"] {
        background: rgba(56, 189, 248, 0.2) !important;
        color: #38bdf8 !important; /* لون أزرق نيون */
        border-right: 4px solid #38bdf8 !important;
        font-weight: 700 !important;
    }

    /* إخفاء دوائر الراديو */
    div[data-testid="stRadioButtonCustomObject"] { display: none !important; }

    /* الهيدر العلوي */
    header {visibility: hidden;}
    .stApp { background-color: #f8fafc; } /* خلفية بيضاء فخمة للمحتوى */

    /* أزرار زجاجية احترافية */
    .stButton > button {
        background: rgba(56, 189, 248, 0.1) !important;
        color: #0f172a !important;
        border: 1px solid #38bdf8 !important;
        border-radius: 10px !important;
        font-weight: 600 !important;
    }
    </style>
    """, unsafe_allow_html=True)

inject_nasq_royal_css()

# --- 5. الاتصال بالقاعدة ---
@st.cache_resource(ttl=60)
def init_connection():
    try:
        db_uri = "postgresql://postgres.jfqmcgicbdrhrtkhuwws:Nasaq268609@aws-1-ap-northeast-1.pooler.supabase.com:6543/postgres"
        conn = psycopg2.connect(db_uri, sslmode="require", connect_timeout=15)
        # التأكد من جدول الرسائل
        cursor = conn.cursor()
        cursor.execute("CREATE TABLE IF NOT EXISTS internal_messages (id SERIAL, sender_name TEXT, sender_role TEXT, message TEXT, timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP)")
        conn.commit()
        return conn
    except: return None

conn = init_connection()

if "logged_in" not in st.session_state:
    st.session_state.update({"logged_in": False, "emp_name": "", "role": ""})

# --- 6. الهيدر المطور (الرسائل والإشعارات المنسدلة) ---
def render_header_ui():
    col_logo, col_space, col_tools = st.columns([1, 2, 1.5])
    
    with col_tools:
        # استخدام Popover كبديل احترافي للقوائم المنسدلة
        c1, c2, c3 = st.columns([1, 1, 2])
        
        with c1:
            with st.popover("🔔"):
                st.markdown("**🔔 آخر التنبيهات**")
                if conn:
                    cursor = conn.cursor()
                    cursor.execute("SELECT work_order_sn, current_stage FROM orders ORDER BY id DESC LIMIT 3")
                    for row in cursor.fetchall():
                        st.caption(f"📦 الطلب {row[0]} انتقل لمرحلة: {row[1]}")
        
        with c2:
            with st.popover("📩"):
                st.markdown("**📩 الرسائل الواردة**")
                if conn:
                    cursor = conn.cursor()
                    cursor.execute("SELECT sender_name, message FROM internal_messages ORDER BY id DESC LIMIT 3")
                    for row in cursor.fetchall():
                        st.info(f"**{row[0]}:** {row[1]}")
        
        with c3:
            st.markdown(f"""
                <div style="display:flex; align-items:center; gap:10px; background:white; padding:5px 15px; border-radius:12px; border:1px solid #e2e8f0;">
                    <div style="text-align:left">
                        <div style="font-size:14px; font-weight:bold; color:#0f172a;">{st.session_state.emp_name}</div>
                        <div style="font-size:10px; color:#64748b;">المدير العام</div>
                    </div>
                    <div style="font-size:24px;">👤</div>
                </div>
            """, unsafe_allow_html=True)

# --- 7. نظام المراسلات المطور (احترافي جداً) ---
def render_pro_chat(conn):
    with st.sidebar:
        st.divider()
        with st.expander("💬 غرفة العمليات (شات داخلي)", expanded=False):
            if conn:
                try:
                    cursor = conn.cursor()
                    cursor.execute("SELECT sender_name, message, sender_role FROM internal_messages ORDER BY id DESC LIMIT 8")
                    msgs = cursor.fetchall()
                    for m in reversed(msgs):
                        align = "right" if m[0] == st.session_state.emp_name else "left"
                        bg = "#38bdf8" if m[2] == "Admin" else "#f1f5f9"
                        txt_color = "white" if m[2] == "Admin" else "#0f172a"
                        st.markdown(f"""
                            <div style="text-align:{align}; margin-bottom:10px;">
                                <small style="color:#64748b;">{m[0]}</small>
                                <div style="background:{bg}; color:{txt_color}; padding:8px 12px; border-radius:12px; display:inline-block; font-size:13px;">
                                    {m[1]}
                                </div>
                            </div>
                        """, unsafe_allow_html=True)
                    
                    with st.form("chat_form", clear_on_submit=True):
                        txt = st.text_input("", placeholder="اكتب ردك هنا...", label_visibility="collapsed")
                        if st.form_submit_button("إرسال 🚀", use_container_width=True):
                            cursor.execute("INSERT INTO internal_messages (sender_name, sender_role, message) VALUES (%s, %s, %s)", 
                                           (st.session_state.emp_name, st.session_state.role, txt))
                            conn.commit()
                            st.rerun()
                except: conn.rollback()

# --- 8. بوابة المدير المحدثة ---
def admin_portal():
    render_header_ui()
    render_pro_chat(conn)
    
    with st.sidebar:
        st.markdown('<h2 style="color:white; text-align:center; font-weight:800;">NASAQ PRO</h2>', unsafe_allow_html=True)
        st.divider()
        options = ["📊 لوحة القيادة", "🤖 المساعد الذكي", "➕ طلب جديد", "📦 الورشة", "🧾 المالية", "👥 العملاء", "👨‍💼 الفريق", "⚙️ الإعدادات"]
        choice = st.radio("القائمة:", options, label_visibility="collapsed")
        if st.button("🚪 تسجيل الخروج", use_container_width=True):
            st.session_state.logged_in = False
            st.rerun()

    mapping = {
        "📊 لوحة القيادة": "dashboard", "🤖 المساعد الذكي": "ai_assistant", "➕ طلب جديد": "new_order",
        "📦 الورشة": "orders", "🧾 المالية": "accounts", "👥 العملاء": "clients",
        "👨‍💼 الفريق": "employees", "⚙️ الإعدادات": "categories"
    }
    page_key = mapping.get(choice)
    if page_key == "ai_assistant": PAGES["ai_assistant"]()
    elif page_key: PAGES[page_key](conn)

# --- التشغيل ---
if not st.session_state.logged_in:
    # (كود شاشة الدخول المعتاد)
    col1, col2, col3 = st.columns([1,1.2,1])
    with col2:
        st.markdown("<h1 style='text-align:center;'>دخول نَسق</h1>", unsafe_allow_html=True)
        with st.form("login"):
            s = st.text_input("الرقم الوظيفي")
            p = st.text_input("كلمة المرور", type="password")
            if st.form_submit_button("دخول", use_container_width=True):
                cursor = conn.cursor()
                cursor.execute("SELECT emp_name, role FROM employees WHERE serial_number = %s AND password = %s", (s, p))
                user = cursor.fetchone()
                if user:
                    st.session_state.update({"logged_in": True, "emp_name": user[0], "role": user[1]})
                    st.rerun()
else:
    if st.session_state.role == "Admin": admin_portal()
    else: st.write("واجهة الموظف قيد التحديث")
