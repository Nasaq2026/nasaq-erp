import streamlit as st
from streamlit_option_menu import option_menu
import warnings
import os
import sys

# 1. إعدادات الصفحة
st.set_page_config(
    page_title="نَسق ERP | عالم الدعاية والإعلان", 
    layout="wide", 
    page_icon="🎯",
    initial_sidebar_state="expanded"
)
warnings.filterwarnings('ignore', category=UserWarning)
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 2. استيراد المنظومات
try:
    from utils.db_manager import db
    from web_ui import (
        dashboard, new_order, orders, orders_view, 
        marketing, clients, finance, supply_chain, hr_system, settings, invoices
    )
except ImportError as e:
    st.error(f"⚠️ نقص في ملفات النظام: {e}")
    st.stop()

# --- دالة الإصلاح الذاتي لقاعدة البيانات ---
def fix_database_schema(conn):
    cursor = conn.cursor()
    # إضافة الأعمدة الجديدة إذا لم تكن موجودة لتجنب خطأ "column does not exist"
    columns_to_add = [
        ("work_order_sn", "VARCHAR(50)"),
        ("unit_price", "DECIMAL DEFAULT 0"),
        ("total_price", "DECIMAL DEFAULT 0"),
        ("paid_amount", "DECIMAL DEFAULT 0"),
        ("remaining_amount", "DECIMAL DEFAULT 0"),
        ("current_stage", "VARCHAR(50) DEFAULT 'التصميم'"),
        ("material_type", "VARCHAR(100)")
    ]
    for col_name, col_type in columns_to_add:
        try:
            cursor.execute(f"ALTER TABLE orders ADD COLUMN {col_name} {col_type};")
            conn.commit()
        except:
            conn.rollback() # العمود موجود مسبقاً، تخطى

# 3. CSS نَسق (مختصر للوضوح)
st.markdown("""<style>... (نفس الستايل الخاص بك) ...</style>""", unsafe_allow_html=True)

# 4. القائمة الجانبية
with st.sidebar:
    choice = option_menu(
        "لوحة التحكم",
        ["الرئيسية (العمليات)", "سجل الفواتير", "طلب جديد", "الداشبورد المالي", "قاعدة العملاء", "الموردين والورش", "الموارد البشرية", "المسوق الذكي", "الإعدادات"],
        icons=['kanban', 'receipt', 'plus-square-fill', 'pie-chart-fill', 'people-fill', 'truck-flatbed', 'person-lines-fill', 'megaphone-fill', 'gear-wide-connected'],
        menu_icon="cast", default_index=0
    )

# 5. التوجيه الذكي
try:
    conn = db.get_connection()
    fix_database_schema(conn) # تشغيل الإصلاح التلقائي عند كل بداية

    if choice == "الرئيسية (العمليات)":
        orders_view.render_orders_view(conn)
    elif choice == "طلب جديد":
        new_order.render_new_order(conn)
    # ... باقي الروابط كما هي في كودك ...
        
except Exception as e:
    st.error(f"❌ حدث خطأ في النظام: {e}")
