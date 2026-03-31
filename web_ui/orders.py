import streamlit as st
import pandas as pd
from datetime import datetime
import streamlit.components.v1 as components

# استيراد الدوال الخاصة بتوليد المستندات
from utils.invoice import generate_invoice_html
from utils.work_order import generate_work_order_html

def render_orders(conn):
    st.markdown("""
        <div style="text-align: right;">
            <h1 style="color: #1e293b;">📦 إدارة العمليات وأوامر التشغيل</h1>
            <p style="color: #64748b;">متابعة سير الإنتاج، تحديث الحالات، وإصدار الفواتير الضريبية.</p>
        </div>
    """, unsafe_allow_html=True)

    try:
        # التأكد من تحديث الجلسة مع قاعدة البيانات
        cursor = conn.cursor()
        
        # 1. جلب بيانات الموظفين للقوائم المنسدلة
        cursor.execute("SELECT emp_name FROM employees WHERE role = 'Designer'")
        designers_list = [r[0] for r in cursor.fetchall()] or ["بدون مصمم"]
        
        cursor.execute("SELECT emp_name FROM employees WHERE role = 'Technician'")
        tech_list = [r[0] for r in cursor.fetchall()] or ["بدون فني"]
        
        cursor.execute("SELECT emp_name FROM employees WHERE role = 'Installer'")
        installers_list = [r[0] for r in cursor.fetchall()] or ["بدون فريق تركيب"]

        # 2. سحب بيانات الطلبات
        query = "SELECT * FROM orders ORDER BY id DESC"
        df = pd.read_sql(query, conn)
        
        if df.empty:
            st.warning("📭 لا توجد طلبات مسجلة حالياً في نظام نَسق.")
            return

        # عرض الجدول الرئيسي (تنسيق عريض)
        st.markdown("### 📋 سجل الطلبات المفتوحة")
        st.dataframe(df, use_container_width=True, hide_index=True)

        st.divider()

        # 3. محرك التحكم والتعديل
        st.markdown("### ⚙️ تحديث حالة أمر العمل")
        
        # اختيار أمر العمل بناءً على الرقم التسلسلي (SN)
        if 'work_order_sn' in df.columns:
            order_sns = df['work_order_sn'].unique().tolist()
            selected_sn = st.selectbox("🎯 اختر رقم أمر العمل للتعديل عليه:", order_sns)
            
            # جلب بيانات الصف المختار كـ Series
            order_data = df[df['work_order_sn'] == selected_sn].iloc[0]
            
            with st.expander(f"📝 تعديل بيانات الطلب: {selected_sn}", expanded=True):
                col_e1, col_e2, col_e3 = st.columns(3)
                
                # إسناد الموظفين مع تحديد القيمة الحالية
                def get_index(lst, val): return lst.index(val) if val in lst else 0

                new_des = col_e1.selectbox("المصمم المكلف:", designers_list, index=get_index(designers_list, order_data['designer']))
                new_tech = col_e2.selectbox("الفني المكلف:", tech_list, index=get_index(tech_list, order_data['technician']))
                new_inst = col_e3.selectbox("فريق التركيب:", installers_list, index=get_index(installers_list, order_data['installer']))

                col_e4, col_e5 = st.columns(2)
                stages = ["التصميم", "الطباعة والإنتاج", "التركيب", "جاهز للتسليم"]
                new_stage = col_e4.selectbox("المرحلة الحالية:", stages, index=get_index(stages, order_data['current_stage']))
                
                statuses = ["نشط", "مكتمل", "قيد الانتظار", "ملغي"]
                new_status = col_e5.selectbox("الحالة العامة:", statuses, index=get_index(statuses, order_data['status']))

                new_details = st.text_area("تحديث ملاحظات التنفيذ:", value=order_data['details'])

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

            # 4. مركز المستندات والطباعة
            st.markdown("### 🖨️ طباعة المستندات (نَسق)")
            c1, c2 = st.columns(2)

            # تحويل البيانات لقاموس لضمان الدقة في الدوال الخارجية
            order_dict = order_data.to_dict()

            if c1.button("📑 أمر تشغيل ورشة", use_container_width=True):
                html_wo = generate_work_order_html(order_dict)
                st.download_button("📥 تحميل PDF (HTML)", data=html_wo, file_name=f"WO_{selected_sn}.html", mime="text/html")
                components.html(html_wo, height=600, scrolling=True)

            if c2.button("🧾 فاتورة ضريبية", use_container_width=True):
                # جلب بيانات العميل للـ QR والضريبة
                cursor.execute("SELECT * FROM clients WHERE phone = %s", (str(order_data['phone']),))
                client_data = cursor.fetchone()
                
                html_inv = generate_invoice_html(order_dict, client_data)
                st.download_button("📥 تحميل الفاتورة", data=html_inv, file_name=f"INV_{selected_sn}.html", mime="text/html")
                components.html(html_inv, height=600, scrolling=True)
        else:
            st.error("⚠️ خطأ: عمود 'work_order_sn' غير موجود في قاعدة البيانات.")

    except Exception as e:
        st.error(f"❌ حدث خطأ في محرك العمليات: {e}")
