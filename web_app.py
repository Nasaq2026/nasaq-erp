import streamlit as st
from streamlit_option_menu import option_menu
import warnings

# استيراد منظومات نَسق المحدثة
# تأكد من أن dashboard.py و marketing.py و clients.py مصححة
from utils.db_manager import db
from web_ui import (
    dashboard, new_order, orders, tracking_page,
    marketing, clients, settings
)

# 1. إعداد الصفحة والتحذيرات
st.set_page_config(page_title="نَسق ERP | Module Group", layout="wide", page_icon="🎯")
warnings.filterwarnings('ignore', category=UserWarning)

# 2. CSS للحركة والأيقونة العائمة (كما في ملفك)
st.markdown("""
    <style>
    @keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }
    .main { animation: fadeIn 1s; }
    .stMetric { background: white; padding: 15px; border-radius: 15px; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1); }
    .stButton>button { border-radius: 10px; transition: 0.3s; }
    .stButton>button:hover { transform: scale(1.05); }
    /* أيقونة واتساب عائمة */
    .wa-float {
        position:fixed; width:60px; height:60px; bottom:40px; right:40px;
        background-color:#25d366; color:#FFF; border-radius:50px; text-align:center;
        font-size:30px; box-shadow: 2px 2px 3px #999; z-index:100;
    }
    </style>
    <a href="https://wa.me/966XXXXXXXXX" class="wa-float" target="_blank">
        <i class="fa fa-whatsapp" style="margin-top:16px;"></i>
    </a>
    """, unsafe_allow_html=True)

# 3. القائمة الجانبية (Side Navigation)
with st.sidebar:
    st.image("assets/logo.png", width=180) # تأكد من وجود شعار Module
    st.markdown("---")
    
    choice = option_menu(
        "نظام نَسق المطور",
        # تعديل القائمة: إضافة "لوحة التحكم (الإحصائيات)"
        ["الرئيسية (العمليات)", "طلب جديد", "لوحة الإحصائيات (الداشبورد)", "تتبع الطلبات", "المسوق الذكي", "قاعدة العملاء", "الإعدادات"],
        icons=['grid-1x2', 'plus-circle', 'bar-chart-line', 'search', 'megaphone', 'people', 'sliders'],
        menu_icon="cast", default_index=0,
        styles={
            "container": {"padding": "5!important", "background-color": "#fafafa"},
            "icon": {"color": "#3b82f6", "font-size": "20px"}, 
            "nav-link": {"font-weight": "600", "font-family": "'Cairo', sans-serif"},
            "nav-link-selected": {"background-color": "#3b82f6", "color": "white"},
        }
    )

# 4. التوجيه الذكي (Routing)
try:
    conn = db.get_connection()

    if choice == "الرئيسية (العمليات)":
        orders.render_orders(conn)
        
    elif choice == "طلب جديد":
        new_order.render_new_order(conn)
        
    elif choice == "لوحة الإحصائيات (الداشبورد)":
        # تعديل التوجيه لاستدعاء الداشبورد الاحترافي (الذي يظهر الأرباح)
        dashboard.render_dashboard(conn)
        
    elif choice == "تتبع الطلبات":
        tracking_page.render_tracking(conn)
        
    elif choice == "المسوق الذكي":
        marketing.render_marketing(conn)
        
    elif choice == "قاعدة العملاء":
        clients.render_clients(conn)
        
    elif choice == "الإعدادات":
        settings.render_settings()
        
except Exception as e:
    st.error(f"❌ حدث خطأ غير متوقع في نظام التوجيه: {e}")
