import streamlit as st
from streamlit_option_menu import option_menu
from web_ui import (
    dashboard, new_order, orders, marketing, 
    clients, supply_chain, hr_system, finance
)

# إعداد الصفحة بهوية "نَسق"
st.set_page_config(page_title="نَسق ERP | Module Group", layout="wide", page_icon="🎯")

# CSS للحركة والأيقونات العائمة
st.markdown("""
    <style>
    @keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }
    .main { animation: fadeIn 1s; }
    .stMetric { background: white; padding: 15px; border-radius: 15px; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1); }
    .wa-float {
        position:fixed; width:60px; height:60px; bottom:40px; left:40px;
        background-color:#25d366; color:#FFF; border-radius:50px; text-align:center;
        font-size:30px; box-shadow: 2px 2px 3px #999; z-index:100;
    }
    </style>
    <a href="https://wa.me/966XXXXXXXXX" class="wa-float" target="_blank">
        <i class="fa fa-whatsapp" style="margin-top:16px;"></i>
    </a>
    """, unsafe_allow_html=True)

with st.sidebar:
    st.image("assets/logo.png", width=180)
    choice = option_menu(
        "نظام نَسق المطور",
        ["الرئيسية", "العمليات", "المالية", "العملاء", "الموردين والورش", "الموارد البشرية", "التسويق"],
        icons=['grid-1x2', 'tools', 'cash-stack', 'people', 'truck', 'person-badge', 'megaphone'],
        menu_icon="cast", default_index=0,
        styles={
            "container": {"padding": "5!important", "background-color": "#fafafa"},
            "icon": {"color": "#3b82f6", "font-size": "20px"}, 
            "nav-link-selected": {"background-color": "#3b82f6"},
        }
    )

# التوجيه الذكي
conn = db.get_connection()
if choice == "الرئيسية": dashboard.render_dashboard(conn)
elif choice == "العمليات": orders.render_orders(conn)
elif choice == "المالية": finance.render_finance(conn)
elif choice == "العملاء": clients.render_clients(conn)
elif choice == "الموردين والورش": supply_chain.render_supply_chain(conn)
elif choice == "الموارد البشرية": hr_system.render_hr(conn)
