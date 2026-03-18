# web_ui/orders.py
import streamlit as st
import pandas as pd
import urllib.parse
from datetime import datetime
import base64
import qrcode
import io

def render_orders(conn):
    st.title("📦 إدارة الطلبات وأوامر العمل (المدير)")
    st.info("هذه الشاشة مخصصة للمتابعة، تعديل بيانات الطاقم الفني، وإصدار المستندات.")

    try:
        conn.rollback()
        cursor = conn.cursor()

        # 1. جلب البيانات والقوائم المساعدة (المصممين، الفنيين، التركيب)
        cursor.execute("SELECT emp_name FROM employees WHERE role = 'Designer'")
        designers_list = [r[0] for r in cursor.fetchall()]
        
        cursor.execute("SELECT emp_name FROM employees WHERE role = 'Technician'")
        tech_list = [r[0] for r in cursor.fetchall()]
        
        cursor.execute("SELECT emp_name FROM employees WHERE role = 'Installer'")
        installers_list = [r[0] for r in cursor.fetchall()]

        # سحب بيانات الطلبات
        query = "SELECT * FROM orders ORDER BY id DESC"
        df = pd.read_sql(query, conn)
        
        if df.empty:
            st.warning("📭 لا توجد طلبات مسجلة حالياً.")
            return

        # عرض الجدول بشكل أنيق
        st.dataframe(df, use_container_width=True, hide_index=True)

        st.divider()

        # ==========================================
        # 2. محرك التعديل والتحكم (The Controller)
        # ==========================================
        st.markdown("### ⚙️ تعديل بيانات أمر العمل")
        
        selected_order_sn = st.selectbox("🎯 اختر رقم (أمر العمل) للتعديل عليه:", df['work_order_sn'].tolist())
        
        # استخراج بيانات الطلب المختار
        order_data = df[df['work_order_sn'] == selected_order_sn].iloc[0]

        # إنشاء نموذج التعديل السريع
        with st.expander(f"📝 تعديل تفاصيل الطلب رقم: {selected_order_sn}", expanded=True):
            col_e1, col_e2, col_e3 = st.columns(3)
            
            # تحديد القيم الحالية كافتراضية
            new_des = col_e1.selectbox("المصمم المكلف:", designers_list, 
                                       index=designers_list.index(order_data['designer']) if order_data['designer'] in designers_list else 0)
            
            new_tech = col_e2.selectbox("الفني المكلف:", tech_list, 
                                        index=tech_list.index(order_data['technician']) if order_data['technician'] in tech_list else 0)
            
            new_inst = col_e3.selectbox("فريق التركيب:", installers_list, 
                                        index=installers_list.index(order_data['installer']) if order_data['installer'] in installers_list else 0)

            col_e4, col_e5 = st.columns(2)
            new_stage = col_e4.selectbox("تغيير المرحلة الحالية:", ["التصميم", "الطباعة والإنتاج", "التركيب", "جاهز للتسليم"], 
                                         index=["التصميم", "الطباعة والإنتاج", "التركيب", "جاهز للتسليم"].index(order_data['current_stage']) if order_data['current_stage'] in ["التصميم", "الطباعة والإنتاج", "التركيب", "جاهز للتسليم"] else 0)
            
            new_status = col_e5.selectbox("تغيير الحالة العامة:", ["نشط", "مكتمل", "قيد الانتظار", "ملغي"], 
                                          index=["نشط", "مكتمل", "قيد الانتظار", "ملغي"].index(order_data['status']))

            new_details = st.text_area("تعديل التفاصيل الفنية:", value=order_data['details'])

            if st.button("💾 حفظ التعديلات الجديدة", type="primary", use_container_width=True):
                cursor.execute("""
                    UPDATE orders 
                    SET designer = %s, technician = %s, installer = %s, 
                        current_stage = %s, status = %s, details = %s
                    WHERE work_order_sn = %s
                """, (new_des, new_tech, new_inst, new_stage, new_status, new_details, selected_order_sn))
                conn.commit()
                st.success(f"✅ تم تحديث بيانات أمر العمل {selected_order_sn} بنجاح!")
                st.rerun()

        st.divider()

        # ==========================================
        # 3. الطباعة والتصدير (نفس كودك السابق)
        # ==========================================
        st.markdown("### 🖨️ المستندات والطباعة")
        c1, c2, c3, c4 = st.columns(4)

        if c1.button("📑 تجهيز أمر عمل", use_container_width=True):
            html_wo = generate_wo_html(order_data)
            st.download_button("📥 تحميل PDF/HTML", data=html_wo, file_name=f"WO_{selected_order_sn}.html")

        if c2.button("🧾 تجهيز فاتورة", use_container_width=True):
            html_inv = generate_inv_html(order_data)
            st.download_button("📥 تحميل الفاتورة", data=html_inv, file_name=f"Invoice_{selected_order_sn}.html")

        # ... (باقي دوال الواتساب وإكسل كما هي في كودك السابق)

    except Exception as e:
        st.error(f"حدث خطأ: {e}")

# --- دوال التوليد (تأكد من وجودها في الأسفل كما في ملفك الأصلي) ---
def generate_wo_html(data):
    # كود HTML لأمر العمل...
    return "..."
def generate_inv_html(data):
    # كود HTML للفاتورة...
    return "..."