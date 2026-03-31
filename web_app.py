import streamlit as st
from streamlit_option_menu import option_menu
import warnings
import os
import sys

# 1. إعدادات الصفحة والتحذيرات
st.set_page_config(
    page_title="نَسق ERP | Module Group", 
    layout="wide", 
    page_icon="🎯",
    initial_sidebar_state="expanded"
)
warnings.filterwarnings('ignore', category=UserWarning)

# ضمان رؤية المجلدات الفرعية
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 2. محاولة استيراد المنظومات (مع معالجة الأخطاء لضمان استقرار التشغيل)
try:
    from utils.db_manager import db
    from web_ui import (
        dashboard, new_order, orders, tracking_page,
        marketing, clients, finance, supply_chain, hr_system, settings
    )
except ImportError as e:
    st.error(f"⚠️ نقص في ملفات النظام: {e}")
    st.stop()

# 3. CSS المطور للحركة، الأيقونات العائمة، وتنسيق الواجهة
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;700&display=swap');
    html, body, [class*="css"] { font-family: 'Cairo', sans-serif; }
    
    @keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }
    .main { animation: fadeIn 1s; }
    
    /* تنسيق البطاقات الإحصائية */
    .stMetric { 
        background: #ffffff; 
        padding: 20px; 
        border-radius: 15px; 
        box-shadow: 0 10px 15px -3px rgba(0,0,0,0.1);
        border-right: 5px solid #3b82f6;
    }
    
    /* الزر العائم للواتساب */
    .wa-float {
        position:fixed; width:60px; height:60px; bottom:40px; left:40px;
        background-color:#25d366; color:#FFF; border-radius:50px; text-align:center;
        font-size:30px; box-shadow: 2px 2px 10px rgba(0,0,0,0.2); z-index:100;
        transition: 0.3s;
    }
    .wa-float:hover { transform: scale(1.1); color: white; }
    </style>
    
    <a href="https://wa.me/966XXXXXXXXX" class="wa-float" target="_blank">
        <div style="margin-top:14px;">💬</div>
    </a>
    """, unsafe_allow_html=True)

# 4. القائمة الجانبية الذكية (Side Navigation)
with st.sidebar:
    # حل مشكلة الصورة: البحث عن المسار المطلق وتجنب الانهيار
    base_dir = os.path.dirname(os.path.abspath(__file__))
    logo_path = os.path.join(base_dir, "assets", "logo.png")
    
    if os.path.exists(logo_path):
        st.image(logo_path, width=180)
    else:
        st.markdown("<h2 style='text-align:center; color:#3b82f6;'>نَسق ERP 🎯</h2>", unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    choice = option_menu(
        "منظومة موديول",
        ["الرئيسية (العمليات)", "طلب جديد", "الداشبورد المالي", "قاعدة العملاء", "الموردين والورش", "الموارد البشرية", "المسوق الذكي", "الإعدادات"],
        icons=['grid-1x2', 'plus-circle', 'graph-up-arrow', 'people', 'truck', 'person-badge', 'megaphone', 'sliders'],
        menu_icon="app-indicator", default_index=0,
        styles={
            "container": {"padding": "5!important", "background-color": "#fafafa"},
            "icon": {"color": "#3b82f6", "font-size": "18px"}, 
            "nav-link": {"font-size": "14px", "text-align": "right", "margin":"5px", "--hover-color": "#e2e8f0"},
            "nav-link-selected": {"background-color": "#3b82f6", "font-weight": "700"},
        }
    )

# 5. التوجيه الذكي للمنظومات (Routing Logic)
try:
    conn = db.get_connection()

    if choice == "الرئيسية (العمليات)":
        orders.render_orders(conn)
        
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
    st.error(f"❌ خطأ في الاتصال بقاعدة البيانات أو تحميل الصفحة: {e}")
