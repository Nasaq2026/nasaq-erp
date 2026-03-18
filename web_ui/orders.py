# web_ui/orders.py
import streamlit as st
import pandas as pd
from datetime import datetime

def render_orders(conn):
    st.markdown("""
        <div style="text-align: right;">
            <h1 style="color: #1e293b;">📦 إدارة الطلبات وأوامر العمل (المدير)</h1>
            <p style="color: #64748b;">متابعة سير العمل، تعديل بيانات الطاقم الفني، وإصدار المستندات الرسمية.</p>
        </div>
    """, unsafe_allow_html=True)

    try:
        conn.rollback()
        cursor = conn.cursor()

        # 1. جلب قوائم الموظفين
        cursor.execute("SELECT emp_name FROM employees WHERE role = 'Designer'")
        designers_list = [r[0] for r in cursor.fetchall()] or ["بدون مصمم"]
        
        cursor.execute("SELECT emp_name FROM employees WHERE role = 'Technician'")
        tech_list = [r[0] for r in cursor.fetchall()] or ["بدون فني"]
        
        cursor.execute("SELECT emp_name FROM employees WHERE role = 'Installer'")
        installers_list = [r[0] for r in cursor.fetchall()] or ["بدون فريق تركيب"]

        # سحب بيانات الطلبات
        query = "SELECT * FROM orders ORDER BY id DESC"
        df = pd.read_sql(query, conn)
        
        if df.empty:
            st.warning("📭 لا توجد طلبات مسجلة حالياً.")
            return

        # ✅ عرض الجدول بالكود الجديد width="stretch"
        st.dataframe(df, width="stretch", hide_index=True)

        st.divider()

        # ==========================================
        # 2. محرك التعديل والتحكم
        # ==========================================
        st.markdown("### ⚙️ تعديل بيانات أمر العمل")
        
        selected_order_sn = st.selectbox("🎯 اختر رقم (أمر العمل) للتعديل عليه:", df['work_order_sn'].tolist())
        
        order_data = df[df['work_order_sn'] == selected_order_sn].iloc[0]

        with st.expander(f"📝 تعديل تفاصيل الطلب رقم: {selected_order_sn}", expanded=True):
            col_e1, col_e2, col_e3 = st.columns(3)
            
            # تحديد القيم الحالية
            current_des = order_data['designer']
            current_tech = order_data['technician']
            current_inst = order_data['installer']

            new_des = col_e1.selectbox("المصمم المكلف:", designers_list, 
                                       index=designers_list.index(current_des) if current_des in designers_list else 0)
            
            new_tech = col_e2.selectbox("الفني المكلف:", tech_list, 
                                        index=tech_list.index(current_tech) if current_tech in tech_list else 0)
            
            new_inst = col_e3.selectbox("فريق التركيب:", installers_list, 
                                        index=installers_list.index(current_inst) if current_inst in installers_list else 0)

            col_e4, col_e5 = st.columns(2)
            stages = ["التصميم", "الطباعة والإنتاج", "التركيب", "جاهز للتسليم"]
            new_stage = col_e4.selectbox("تغيير المرحلة الحالية:", stages, 
                                         index=stages.index(order_data['current_stage']) if order_data['current_stage'] in stages else 0)
            
            statuses = ["نشط", "مكتمل", "قيد الانتظار", "ملغي"]
            new_status = col_e5.selectbox("تغيير الحالة العامة:", statuses, 
                                          index=statuses.index(order_data['status']))

            new_details = st.text_area("تعديل التفاصيل الفنية:", value=order_data['details'])

            # ✅ تحديث الزر للكود الجديد width="stretch"
            if st.button("💾 حفظ التعديلات الجديدة", width="stretch"):
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
        # 3. الطباعة والتصدير
        # ==========================================
        st.markdown("### 🖨️ المستندات والطباعة")
        c1, c2, c3, c4 = st.columns(4)

        # ✅ تحديث كافة الأزرار للكود الجديد width="stretch"
        if c1.button("📑 تجهيز أمر عمل", width="stretch"):
            html_wo = generate_wo_html(order_data)
            st.download_button("📥 تحميل PDF/HTML", data=html_wo, file_name=f"WO_{selected_order_sn}.html", width="stretch")

        if c2.button("🧾 تجهيز فاتورة", width="stretch"):
            html_inv = generate_inv_html(order_data)
            st.download_button("📥 تحميل الفاتورة", data=html_inv, file_name=f"Invoice_{selected_order_sn}.html", width="stretch")

    except Exception as e:
        st.error(f"حدث خطأ في النظام: {e}")

# --- دوال التوليد ---
def generate_wo_html(data):
    # كود HTML مبسط لأمر العمل
    return f"<html><body dir='rtl'><h1>أمر عمل: {data['work_order_sn']}</h1></body></html>"

def generate_inv_html(data):
    # كود HTML مبسط للفاتورة
    return f"<html><body dir='rtl'><h1>فاتورة ضريبية: {data['work_order_sn']}</h1></body></html>"
