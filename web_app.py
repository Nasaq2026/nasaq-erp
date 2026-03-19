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
    page_title="Nasq ERP | Pro UI", 
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
        except Exception as e:
            pages[key] = lambda *args, **kwargs: st.error(f"❌ خطأ في تحميل {key}: {e}")
    return pages

PAGES = load_system_pages()

# --- 4. ستايل NASAQ PRO الملكي (UI المطور والاحترافي) ---
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
    .icon-wrapper { position: relative; font-size: 22px; cursor: pointer; transition: 0.3s; color: white; }
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
        padding: 12px 20px !important; border-radius: 10px !important;
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
        position: fixed; top: 100px; left: 20px; width: 300px;
        background: rgba(30, 41, 59, 0.85); backdrop-filter: blur(15px);
        border: 1px solid rgba(56, 189, 248, 0.4); border-radius: 15px;
        padding: 15px; z-index: 9999; animation: slideIn 0.5s cubic-bezier(0.175, 0.885, 0.32, 1.275);
        box-shadow: 0 10px 30px rgba(0,0,0,0.5);
    }
    @keyframes slideIn { from { transform: translateX(-110%); opacity: 0; } to { transform: translateX(0); opacity: 1; } }

    header {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

inject_nasq_pro_css()

# --- 5. الاتصال بقاعدة البيانات ---
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
def render_top_bar(msg_count=0, notif_count=0):
    col_empty, col_info = st.columns([2, 1.2])
    with col_info:
        st.markdown(f"""
            <div class="top-bar">
                <div class="top-bar-icons">
                    <div class="icon-wrapper">📩<span class="badge-pro">{msg_count}</span></div>
                    <div class="icon-wrapper">🔔<span class="badge-pro">{notif_count}</span></div>
                </div>
                <div style="display: flex; align-items: center; gap: 12px; border-right: 1px solid rgba(255,255,255,0.1); padding-right: 15px;">
                    <div style="text-align: left;">
                        <div style="color: #38bdf8; font-weight: 800; font-size: 15px;">{st.session_state.emp_name}</div>
                        <div style="color: #94a3b8; font-size: 11px;">{st.session_state.role} | متصل</div>
                    </div>
                    <div style="font-size: 32px; background: rgba(56,189,248,0.1); border-radius: 50%; padding: 5px;">👤</div>
                </div>
            </div>
        """, unsafe_allow_html=True)

def show_floating_notification(conn):
    if st.session_state.role == "Admin" and conn:
        try:
            cursor = conn.cursor()
            # جلب آخر طلب تم تحويله للتركيب أو اكتمل
            cursor.execute("""
                SELECT work_order_sn, current_stage, client_name 
                FROM orders 
                WHERE current_stage IN ('التركيب', 'مكتمل') 
                ORDER BY id DESC LIMIT 1
            """)
            update = cursor.fetchone()
            if update:
                st.markdown(f"""
                    <div class="glass-notif">
                        <div style="display: flex; align-items: flex-start; gap: 12px;">
                            <div style="font-size: 24px;">🚀</div>
                            <div>
                                <b style="color: #38bdf8; font-size: 15px;">تنبيه نشاط الموظفين</b><br>
                                <div style="color: white; font-size: 13px; margin-top: 4px;">
                                    أكمل القسم العمل على طلب العميل <b>{update[2]}</b> 
                                    (رقم: {update[0]}) وهو الآن في مرحلة <span style="color:#10B981;">{update[1]}</span>.
                                </div>
                            </div>
                        </div>
                    </div>
                """, unsafe_allow_html=True)
        except: pass

# --- 7. المراسلات الداخلية (قاعدة بيانات حقيقية) ---
def render_internal_chat(conn):
    with st.sidebar:
        st.divider()
        with st.expander("💬 غرفة المراسلات الداخلية", expanded=False):
            if conn:
                cursor = conn.cursor()
                # جلب آخر 10 رسائل
                cursor.execute("SELECT sender_name, message, timestamp FROM internal_messages ORDER BY id DESC LIMIT 10")
                msgs = cursor.fetchall()
                
                for m in reversed(msgs):
                    st.markdown(f"""
                        <div style="background: rgba(255,255,255,0.03); padding: 8px; border-radius: 8px; margin-bottom: 5px; border-right: 3px solid #38bdf8;">
                            <small style="color: #38bdf8;"><b>{m[0]}</b> • {m[2].strftime('%H:%M')}</small><br>
                            <span style="font-size: 13px; color: #cbd5e1;">{m[1]}</span>
                        </div>
                    """, unsafe_allow_html=True)
                
                with st.form("chat_form", clear_on_submit=True):
                    text = st.text_input("", placeholder="اكتب رسالة للفريق...", label_visibility="collapsed")
                    if st.form_submit_button("إرسال 🚀", width='stretch'):
                        if text:
                            cursor.execute("INSERT INTO internal_messages (sender_name, sender_role, message) VALUES (%s, %s, %s)",
                                           (st.session_state.emp_name, st.session_state.role, text))
                            conn.commit()
                            st.rerun()

# --- 8. شاشة الدخول ---
def login_screen():
    st.write("<br><br><br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 1.2, 1])
    with col2:
        st.markdown('<h1 style="color:#38bdf8; text-align:center; font-size: 40px; font-weight: 800;">NASAQ ERP</h1>', unsafe_allow_html=True)
        with st.form("login"):
            serial = st.text_input("رقم الموظف")
            password = st.text_input("كلمة المرور", type="password")
            if st.form_submit_button("دخول آمن للمنظومة 🚀", width="stretch"):
                if conn:
                    cursor = conn.cursor()
                    cursor.execute("SELECT emp_name, role FROM employees WHERE serial_number = %s AND password = %s", (serial, password))
                    user = cursor.fetchone()
                    if user:
                        st.session_state.update({"logged_in": True, "emp_name": user[0], "role": user[1]})
                        st.rerun()
                    else: st.error("عذراً، بيانات الدخول غير صحيحة")

# --- 9. بوابات النظام ---
def main_portal():
    # جلب عدد الرسائل غير المقروءة (مثال)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM internal_messages")
    msg_count = cursor.fetchone()[0]
    
    # عرض العناصر العلوية والاشعارات
    render_top_bar(msg_count=msg_count, notif_count=2)
    show_floating_notification(conn)
    render_internal_chat(conn)
    
    with st.sidebar:
        st.markdown('<h2 style="color: #38bdf8; text-align: center; margin-bottom:0; font-weight:800;">NASAQ PRO</h2>', unsafe_allow_html=True)
        st.markdown(f"<p style='text-align:center; color:#94a3b8; font-size:12px;'>نظام الإدارة المتكامل 2026</p>", unsafe_allow_html=True)
        st.divider()
        
        if st.session_state.role == "Admin":
            options = ["📊 لوحة القيادة", "🤖 المساعد الذكي", "➕ طلب جديد", "📦 الورشة", "🧾 المالية", "👥 العملاء", "👨‍💼 الفريق", "⚙️ الإعدادات"]
        else:
            options = ["🏠 شاشتي الرئيسية", "🤖 المساعد الذكي"]
            
        choice = st.radio("القائمة:", options, label_visibility="collapsed")
        
        st.divider()
        if st.button("🚪 تسجيل الخروج من النظام", width="stretch"):
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
