import streamlit as st
import pandas as pd
from datetime import datetime
import streamlit.components.v1 as components
import urllib.parse

# استيراد الدوال الخاصة بتوليد المستندات
from utils.invoice import generate_invoice_html
from utils.work_order import generate_work_order_html

def render_orders(conn):
    st.markdown("""
        <div style="text-align: right;">
            <h1 style="color: #1e293b;">📦 إدارة العمليات وأوامر التشغيل</h1>
            <p style="color: #64748b;">متابعة سير الإنتاج، تحديث الحالات، وإصدار الفواتير الضريبية لـ "موديول".</p>
        </div>
    """, unsafe_allow_html=True)

    try:
        cursor = conn.cursor()
        
        # 1. جلب بيانات الموظفين للقوائم (تأكد من وجودهم في جدول employees)
        cursor.execute("SELECT emp_name FROM employees WHERE role = 'Designer'")
        designers_list = [r[0] for r in cursor.fetchall()] or ["محمود"]
        
        cursor.execute("SELECT emp_name FROM employees WHERE role = 'Technician'")
        tech_list = [r[0] for r in cursor.fetchall()] or ["أومر علي"]
        
        cursor.execute("SELECT emp_name FROM employees WHERE role = 'Installer'")
        installers_list = [r[0] for r in cursor.fetchall()] or ["فريق موديول"]

        # 2. سحب البيانات للعرض في الجدول
        query = "SELECT * FROM orders ORDER BY id DESC"
        df = pd.read_sql(query, conn)
        
        if df.empty:
            st.warning("📭 لا توجد طلبات مسجلة حالياً في نظام نَسق.")
            return

        st.markdown("### 📋 سجل الطلبات المفتوحة")
        st.dataframe(df, use_container_width=True, hide_index=True)

        st.divider()

        # 3. محرك التحكم والتعديل
        if 'work_order_sn' in df.columns:
            order_sns = df['work_order_sn'].unique().tolist()
            selected_sn = st.selectbox("🎯 اختر رقم أمر العمل للتعديل أو الطباعة:", order_sns)
            
            # جلب بيانات الصف المختار من الـ DataFrame
            order_data_raw = df[df['work_order_sn'] == selected_sn].iloc[0]
            
            with st.expander(f"📝 إجراءات الطلب: {selected_sn}", expanded=True):
                col_e1, col_e2, col_e3 = st.columns(3)
                
                def get_index(lst, val): return lst.index(val) if val in lst else 0

                new_des = col_e1.selectbox("المصمم:", designers_list, index=get_index(designers_list, order_data_raw.get('designer')))
                new_tech = col_e2.selectbox("الفني:", tech_list, index=get_index(tech_list, order_data_raw.get('technician')))
                new_inst = col_e3.selectbox("فريق التركيب:", installers_list, index=get_index(installers_list, order_data_raw.get('installer')))

                col_e4, col_e5 = st.columns(2)
                stages = ["التصميم", "الطباعة والإنتاج", "التركيب", "جاهز للتسليم"]
                new_stage = col_e4.selectbox("المرحلة:", stages, index=get_index(stages, order_data_raw.get('current_stage')))
                
                statuses = ["نشط", "مكتمل", "قيد الانتظار", "ملغي"]
                new_status = col_e5.selectbox("الحالة:", statuses, index=get_index(statuses, order_data_raw.get('status')))

                new_details = st.text_area("تحديث الملاحظات:", value=order_data_raw.get('details', ''))

                if st.button("💾 حفظ التحديثات", use_container_width=True, type="primary"):
                    update_sql = """
                        UPDATE orders 
                        SET designer = %s, technician = %s, installer = %s, 
                            current_stage = %s, status = %s, details = %s
                        WHERE work_order_sn = %s
                    """
                    cursor.execute(update_sql, (new_des, new_tech, new_inst, new_stage, new_status, new_details, selected_sn))
                    conn.commit()
                    st.success(f"✅ تم تحديث الطلب {selected_sn} بنجاح!")
                    st.rerun()

            st.divider()

            # 4. مركز المستندات والطباعة (هنا يكمن الحل)
            st.markdown("### 🖨️ طباعة المستندات (نسخة موديول المعتمدة)")
            c1, c2 = st.columns(2)

            if c1.button("📑 أمر تشغيل ورشة", use_container_width=True):
                # جلب البيانات التقنية حصراً
                cursor.execute("""
                    SELECT work_order_sn, client_name, details, category, 
                           material_type, dimensions, expected_delivery, designer, technician
                    FROM orders WHERE work_order_sn = %s
                """, (selected_sn,))
                res_wo = cursor.fetchone()
                keys_wo = ['work_order_sn', 'client_name', 'details', 'category', 'material_type', 'dimensions', 'expected_delivery', 'designer', 'technician']
                order_dict_wo = dict(zip(keys_wo, res_wo))
                
                html_wo = generate_work_order_html(order_dict_wo)
                st.download_button("📥 تحميل PDF امر العمل", data=html_wo, file_name=f"WO_{selected_sn}.html", mime="text/html")
                components.html(html_wo, height=600, scrolling=True)

            if c2.button("🧾 فاتورة ضريبية", use_container_width=True):
                # جلب البيانات المالية الصحيحة (total_with_vat بدلاً من الأصفار)
                cursor.execute("""
                    SELECT work_order_sn, client_name, phone, details, 
                           total_with_vat, paid, (total_with_vat - paid) as debt,
                           category, material_type, dimensions, expected_delivery
                    FROM orders WHERE work_order_sn = %s
                """, (selected_sn,))
                res_inv = cursor.fetchone()
                
                if res_inv:
                    keys_inv = ['work_order_sn', 'client_name', 'phone', 'details', 'total_with_vat', 'paid', 'debt', 'category', 'material_type', 'dimensions', 'expected_delivery']
                    order_dict_inv = dict(zip(keys_inv, res_inv))
                    
                    # جلب بيانات العميل للـ QR
                    cursor.execute("SELECT * FROM clients WHERE phone = %s", (str(order_dict_inv['phone']),))
                    client_data = cursor.fetchone()
                    
                    html_inv = generate_invoice_html(order_dict_inv, client_data)
                    st.download_button("📥 تحميل الفاتورة", data=html_inv, file_name=f"INV_{selected_sn}.html", mime="text/html")
                    components.html(html_inv, height=600, scrolling=True)
                else:
                    st.error("❌ خطأ: لم نجد بيانات مالية لهذا الطلب.")
        else:
            st.error("⚠️ خطأ: عمود 'work_order_sn' مفقود.")

    except Exception as e:
        st.error(f"❌ حدث خطأ في محرك العمليات: {e}")
