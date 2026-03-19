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

# --- 2. تهيئة الإعدادات (نظام 2026) ---
warnings.simplefilter('ignore', UserWarning)
st.set_page_config(
    page_title="Nasq ERP | الملكي PRO", 
    page_icon="🎯", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 3. استيراد الصفحات بأمان ---
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
            pages[key] = lambda *args, **kwargs: st.error(f"⚠️ الملف {key} غير موجود")
    return pages

PAGES = load_system_pages()

# --- 4. ستايل نَسق PRO (إصلاح الألوان والوضوح 100%) ---
def inject_nasq_royal_css():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700;800&display=swap');
    
    /* 1. إجبار اللون الأبيض الناصع على كل النصوص */
    html, body, [data-testid="stSidebar"] *, .stMarkdown, p, h1, h2, h3, label, span, summary {
        font-family: 'Cairo', sans-serif !important;
        direction: rtl; text-align: right;
        color: #ffffff !important; /* اللون الأبيض الناصع المطلوب */
    }

    /* 2. القائمة الجانبية (خلفية داكنة ملكية) */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0f172a 0%, #1e293b 100%) !important;
        border-left: 2px solid rgba(56, 189, 248, 0.3);
    }

    /* 3. تنسيق خيارات القائمة (الأزرار الزجاجية) */
    div[data-testid="stSidebarUserContent"] .stRadio div[role="radiogroup"] label {
        background-color: rgba(255, 255, 255, 0.07) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        padding: 15px 20px !important;
        border-radius: 12px !important;
        margin-bottom: 10px !important;
        transition: 0.3s all ease;
    }

    /* تأثير الوهج عند الاختيار */
    div[data-testid="stSidebarUserContent"] .stRadio div[role="radiogroup"] label[data-selected="true"] {
        background: rgba(56, 189, 248, 0.25) !important;
        border-color: #38bdf8 !important;
        box-shadow: 0 0 15px rgba(56, 189, 248, 0.4);
    }

    /* 4. إخفاء الراديو بوتون الافتراضي */
    div[data-testid="stRadioButtonCustomObject"] { display: none !important; }

    /* 5. تنسيق الشات والـ Expander ليكون واضحاً جداً */
    .stExpander {
        background: rgba(255, 255, 255, 0.05) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 12px !important;
    }
    
    header {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

inject_nasq_royal_css()

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

# --- 6. الهيدر المطور (أزرار منسدلة حقيقية) ---
def render_header_ui():
    col_logo, col_space, col_tools = st.columns([1, 1.5, 1.5])
    with col_tools:
        c1, c2, c3 = st.columns([1, 1, 2])
        with c1:
            with st.popover("🔔"):
                st.markdown("<b style='color:#0f172a;'>🔔 التنبيهات الأخيرة</b>", unsafe_allow_html=True)
                if conn:
                    cursor = conn.cursor()
                    cursor.execute("SELECT work_order_sn, current_stage FROM orders ORDER BY id DESC LIMIT 3")
                    for row in cursor.fetchall():
                        st.caption(f"الطلب {row[0]} أصبح في {row[1]}")
        with c2:
            with st.popover("📩"):
                st.markdown("<b style='color:#0f172a;'>📩 البريد الداخلي</b>", unsafe_allow_html=True)
                if conn:
                    cursor = conn.cursor()
                    cursor.execute("SELECT sender_name, message FROM internal_messages ORDER BY id DESC LIMIT 3")
                    for row in cursor.fetchall():
                        st.info(f"**{row[0]}:** {row[1]}")
        with c3:
            st.markdown(f"""
                <div style="background:rgba(255,255,255,0.1); padding:8px 15px; border-radius:10px; border:1px solid rgba(255,255,255,0.2); display:flex; align-items:center; gap:10px;">
                    <div style="text-align:left"><div style="font-size:14px; font-weight:bold; color:#ffffff;">{st.session_state.emp_name}</div><div style="font-size:10px; color:#38bdf8;">{st.session_state.role}</div></div>
                    <div style="font-size:24px;">👤</div>
                </div>
            """, unsafe_allow_html=True)

# --- 7. الشات الداخلي الاحترافي ---
def render_pro_chat(conn):
    with st.sidebar:
        st.divider()
        with st.expander("💬 غرفة العمليات (شات داخلي)", expanded=True):
            if conn:
                try:
                    cursor = conn.cursor()
                    cursor.execute("SELECT sender_name, message, sender_role FROM internal_messages ORDER BY id DESC LIMIT 6")
                    msgs = cursor.fetchall()
                    for m in reversed(msgs):
                        color = "#38bdf8" if m[2] == "Admin" else "#00ff88"
                        st.markdown(f"<div style='border-bottom:1px solid rgba(255,255,255,0.1); padding:5px 0;'><small style='color:{color}; font-weight:bold;'>{m[0]}:</small><div style='color:#ffffff; font-size:13px;'>{m[1]}</div></div>", unsafe_allow_html=True)
                    
                    with st.form("sidebar_chat_form", clear_on_submit=True):
                        # تم حل مشكلة الـ label والـ width
                        t = st.text_input("نص الرسالة", placeholder="اكتب هنا...", label_visibility="collapsed")
                        if st.form_submit_button("إرسال 🚀", width='stretch'):
                            cursor.execute("INSERT INTO internal_messages (sender_name, sender_role, message) VALUES (%s, %s, %s)", 
                                           (st.session_state.emp_name, st.session_state.role, t))
                            conn.commit()
                            st.rerun()
                except: 
                    if conn: conn.rollback()

# --- 8. بوابة التحكم المركزية ---
def main_portal():
    render_header_ui()
    render_pro_chat(conn)
    with st.sidebar:
        st.markdown('<h2 style="color:#ffffff; text-align:center; font-weight:800; margin-bottom:20px;">NASAQ PRO</h2>', unsafe_allow_html=True)
        options = ["📊 لوحة القيادة", "🤖 المساعد الذكي", "➕ طلب جديد", "📦 الورشة", "🧾 المالية", "👥 العملاء", "👨‍💼 الفريق", "⚙️ الإعدادات"]
        choice = st.radio("خيارات النظام", options, label_visibility="collapsed")
        st.divider()
        if st.button("🚪 تسجيل الخروج", width='stretch'):
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

# --- 9. التشغيل النهائي ---
if not st.session_state.logged_in:
    col1, col2, col3 = st.columns([1,1.2,1])
    with col2:
        st.markdown("<h1 style='text-align:center; color:white;'>نظام نَسق ERP</h1>", unsafe_allow_html=True)
        with st.form("login_app"):
            s = st.text_input("الرقم الوظيفي", placeholder="A-1001")
            p = st.text_input("كلمة المرور", type="password")
            if st.form_submit_button("دخول آمن", width='stretch'):
                if conn:
                    cursor = conn.cursor()
                    cursor.execute("SELECT emp_name, role FROM employees WHERE serial_number = %s AND password = %s", (s, p))
                    user = cursor.fetchone()
                    if user:
                        st.session_state.update({"logged_in": True, "emp_name": user[0], "role": user[1]})
                        st.rerun()
else:
    main_portal()
