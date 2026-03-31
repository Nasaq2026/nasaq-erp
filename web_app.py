import streamlit as st
from streamlit_option_menu import option_menu
import warnings
import os
import sys

# 1. إعدادات الصفحة المتقدمة لعام 2026
st.set_page_config(
    page_title="نَسق ERP | عالم الدعاية والإعلان", 
    layout="wide", 
    page_icon="🎯",
    initial_sidebar_state="expanded"
)
warnings.filterwarnings('ignore', category=UserWarning)

# ضمان رؤية المجلدات الفرعية
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 2. استيراد المنظومات (مع إضافة الواجهات الذكية الجديدة)
try:
    from utils.db_manager import db
    from web_ui import (
        dashboard, new_order, orders, orders_view, # أضفنا orders_view هنا
        marketing, clients, finance, supply_chain, hr_system, settings, invoices
    )
except ImportError as e:
    st.error(f"⚠️ نقص في ملفات النظام: {e}")
    st.stop()

# 3. CSS "نَسق" الاحترافي (ألوان الهوية: برتقالي، أسود، رمادي)
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;700&display=swap');
    html, body, [class*="css"] { font-family: 'Cairo', sans-serif; text-align: right; }
    
    /* تنسيق الهوية البصرية لنَسق */
    :root {
        --nasaq-orange: #fb923c;
        --nasaq-dark: #1e293b;
    }

    /* تأثيرات الحركة (Animations) */
    @keyframes slideIn { from { transform: translateY(20px); opacity: 0; } to { transform: translateY(0); opacity: 1; } }
    .main .block-container { animation: slideIn 0.8s ease-out; }
    
    /* تصميم البطاقات العلوية (KPIs) */
    div[data-testid="stMetric"] {
        background-color: #ffffff;
        border-right: 5px solid var(--nasaq-orange);
        border-radius: 12px;
        box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1);
        padding: 15px !important;
    }

    /* الزر العائم للواتساب الاحترافي */
    .wa-float {
        position:fixed; width:60px; height:60px; bottom:20px; left:20px;
        background-color:#25d366; color:#FFF; border-radius:50px; text-align:center;
        font-size:30px; box-shadow: 2px 2px 20px rgba(0,0,0,0.3); z-index:100;
        display: flex; align-items: center; justify-content: center; text-decoration: none;
    }
    .wa-float:hover { background-color: #128c7e; color: white; transform: scale(1.1); transition: 0.3s; }
    </style>
    
    <a href="https://wa.me/9665XXXXXXXX" class="wa-float" target="_blank">
        <span>💬</span>
    </a>
    """, unsafe_allow_html=True)

# 4. القائمة الجانبية الذكية (Side Navigation)
with st.sidebar:
    base_dir = os.path.dirname(os.path.abspath(__file__))
    logo_path = os.path.join(base_dir, "assets", "logo.png")
    
    if os.path.exists(logo_path):
        st.image(logo_path, width=200)
    else:
        st.markdown(f"<h1 style='text-align:center; color:#fb923c;'>نَسق ERP</h1>", unsafe_allow_html=True)
    
    st.markdown("<hr style='border-color: #fb923c;'>", unsafe_allow_html=True)
    
    # القائمة التفاعلية الجديدة
    choice = option_menu(
        "لوحة التحكم",
        ["الرئيسية (العمليات)", "سجل الفواتير", "طلب جديد", "الداشبورد المالي", "قاعدة العملاء", "الموردين والورش", "الموارد البشرية", "المسوق الذكي", "الإعدادات"],
        icons=['kanban', 'receipt', 'plus-square-fill', 'pie-chart-fill', 'people-fill', 'truck-flatbed', 'person-lines-fill', 'megaphone-fill', 'gear-wide-connected'],
        menu_icon="cast", default_index=0,
        styles={
            "container": {"padding": "5!important", "background-color": "#f8fafc"},
            "icon": {"color": "#fb923c", "font-size": "20px"}, 
            "nav-link": {"font-size": "15px", "text-align": "right", "margin":"8px", "--hover-color": "#fff7ed"},
            "nav-link-selected": {"background-color": "#1e293b", "color": "#fb923c", "font-weight": "700", "border-right": "4px solid #fb923c"},
        }
    )

# 5. التوجيه الذكي للمنظومات (Routing Logic)
try:
    conn = db.get_connection()

    # الربط بالواجهة الذكية الجديدة التي تحتوي على البطاقات والتعميد
    if choice == "الرئيسية (العمليات)":
        orders_view.render_orders_view(conn) # استدعاء الواجهة الذكية بدلاً من القديمة
        
    elif choice == "سجل الفواتير":
        invoices.render_invoices(conn)

    elif choice == "طلب جديد":
        new_order.render_new_order(conn)
        
    elif choice == "الداشبورد المالي":
        dashboard.render_dashboard(conn)
        
    elif choice == "قاعدة العملاء":
        clients.render_clients(conn)
        
    elif choice == "الموردين والورش":
        supply_chain.render_supply_chain(conn)
        
    elif choice == "الموارد البشرية":
        hr_system.render_hr(conn)
        
    elif choice == "المسوق الذكي":
        marketing.render_marketing(conn)
        
    elif choice == "الإعدادات":
        settings.render_settings()
        
except Exception as e:
    st.error(f"❌ حدث خطأ في النظام: {e}")
