# web_ui/orders.py
import streamlit as st
import pandas as pd
from datetime import datetime
import streamlit.components.v1 as components

# استيراد الدوال الاحترافية من المجلدات الخاصة بها
from utils.invoice import generate_invoice_html
from utils.work_order import generate_work_order_html

def render_orders(conn):
    st.markdown("""
        <div style="text-align: right;">
            <h1 style="color: #1e293b;">📦 إدارة الطلبات وأوامر العمل (المدير)</h1>
            <p style="color: #64748b;">متابعة سير العمل، تعديل بيانات الطاقم الفني، وإصدار المستندات الرسمية المعتمدة.</p>
        </div>
    """, unsafe_allow_html=True)

    try:
        conn.rollback()
        cursor = conn.cursor()

        # 1. جلب قوائم الموظفين لتحديث التكليفات
        cursor.execute("SELECT emp_name FROM employees WHERE role = 'Designer'")
        designers_list = [r[0] for r in cursor.fetchall()] or ["بدون مصمم"]
        
        cursor.execute("SELECT emp_name FROM employees WHERE role = 'Technician'")
        tech_list = [r[0] for r in cursor.fetchall()] or ["بدون فني"]
        
        cursor.execute("SELECT emp_name FROM employees WHERE role = 'Installer'")
        installers_list = [r[0] for r in cursor.fetchall()] or ["بدون فريق تركيب"]

        # سحب بيانات الطلبات كاملة
        query = "SELECT * FROM orders ORDER BY id DESC"
        df = pd.read_sql(query, conn)
        
        if df.empty:
            st.warning("📭 لا توجد طلبات مسجلة حالياً في النظام.")
            return

        # عرض الجدول بشكل كامل ممتد
        st.markdown("### 📋 سجل الطلبات الحالي")
        st.dataframe(df, width="stretch", hide_index=True)

        st.divider()

        # ==========================================
        # 2. محرك التعديل والتحكم الذكي
        # ==========================================
        st.markdown("### ⚙️ إدارة وتحكم في أمر العمل")
        
        selected_order_sn = st.selectbox("🎯 اختر رقم (أمر العمل) للتحكم فيه:", df['work_order_sn'].tolist())
        
        # جلب بيانات الصف المختار بدقة
        order_data_row = df[df['work_order_sn'] == selected_order_sn].iloc[0]

        with st.expander(f"📝 تعديل وتكليف الطاقم للطلب: {selected_order_sn}", expanded=True):
            col_e1, col_e2, col_e3 = st.columns(3)
            
            # تحديد القيم الحالية من قاعدة البيانات
            current_des = order_data_row['designer']
            current_tech = order_data_row['technician']
            current_inst = order_data_row['installer']

            new_des = col_e1.selectbox("المصمم المكلف:", designers_list, 
                                       index=designers_list.index(current_des) if current_des in designers_list else 0)
            
            new_tech = col_e2.selectbox("الفني المكلف:", tech_list, 
                                        index=tech_list.index(current_tech) if current_tech in tech_list else 0)
            
            new_inst = col_e3.selectbox("فريق التركيب:", installers_list, 
                                        index=installers_list.index(current_inst) if current_inst in installers_list else 0)

            col_e4, col_e5 = st.columns(2)
            stages = ["التصميم", "الطباعة والإنتاج", "التركيب", "جاهز للتسليم"]
            new_stage = col_e4.selectbox("تغيير المرحلة الحالية:", stages, 
                                         index=stages.index(order_data_row['current_stage']) if order_data_row['current_stage'] in stages else 0)
            
            statuses = ["نشط", "مكتمل", "قيد الانتظار", "ملغي"]
            new_status = col_e5.selectbox("تغيير الحالة العامة:", statuses, 
                                          index=statuses.index(order_data_row['status']) if order_data_row['status'] in statuses else 0)

            new_details = st.text_area("تعديل ملاحظات التنفيذ الفنية:", value=order_data_row['details'])

            if st.button("💾 حفظ التحديثات وإخطار الفريق", width="stretch"):
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
        # 3. نظام الطباعة والتصدير الاحترافي (PDF/HTML)
        # ==========================================
        st.markdown("### 🖨️ مركز طباعة المستندات (نسق)")
        
        # جلب بيانات العميل للـ QR والبيانات الضريبية
        cursor.execute("SELECT * FROM clients WHERE phone = %s", (order_data_row['phone'],))
        client_data = cursor.fetchone()

        c1, c2 = st.columns(2)

        # زر أمر العمل (Work Order)
        if c1.button("📑 توليد أمر تشغيل (ورشة)", width="stretch"):
            # تحويل البيانات لـ List ليتوافق مع دوال التوليد
            row_list = order_data_row.tolist()
            html_wo = generate_work_order_html(row_list)
            
            with st.expander("👁️ معاينة أمر العمل قبل الطباعة", expanded=True):
                components.html(html_wo, height=500, scrolling=True)
                st.download_button("📥 تحميل وحفظ أمر العمل", data=html_wo, file_name=f"WO_{selected_order_sn}.html", mime="text/html", width="stretch")

        # زر الفاتورة الضريبية (Tax Invoice)
        if c2.button("🧾 توليد فاتورة ضريبية", width="stretch"):
            row_list = order_data_row.tolist()
            html_inv = generate_invoice_html(row_list, client_data)
            
            with st.expander("👁️ معاينة الفاتورة الضريبية", expanded=True):
                components.html(html_inv, height=500, scrolling=True)
                st.download_button("📥 تحميل وحفظ الفاتورة", data=html_inv, file_name=f"Invoice_{selected_order_sn}.html", mime="text/html", width="stretch")

    except Exception as e:
        st.error(f"❌ حدث خطأ في محرك إدارة الطلبات: {e}")
