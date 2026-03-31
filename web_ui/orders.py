import streamlit as st
import pandas as pd
from datetime import datetime
import streamlit.components.v1 as components

# استيراد الدوال الخاصة بتوليد المستندات (تأكد من وجود هذه الملفات في مجلد utils)
try:
    from utils.invoice import generate_invoice_html
    from utils.work_order import generate_work_order_html
except ImportError:
    st.error("⚠️ تنبيه: ملفات التوليد (invoice/work_order) غير موجودة في مجلد utils")

def render_orders(conn):
    # تنسيق الواجهة لتكون بهوية نَسق الاحترافية
    st.markdown("""
        <style>
        .main-title { text-align: right; background: linear-gradient(90deg, #fb923c, #1e293b); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-size: 32px; font-weight: bold; }
        .status-card { background-color: #f8fafc; border-right: 5px solid #fb923c; padding: 15px; border-radius: 8px; margin-bottom: 20px; }
        </style>
        <div class="status-card">
            <h1 class="main-title">📦 إدارة العمليات وأوامر التشغيل</h1>
            <p style="color: #64748b; text-align: right;">متابعة سير الإنتاج في نَسق، تحديث حالات التصميم والتركيب، وإصدار المستندات الرسمية.</p>
        </div>
    """, unsafe_allow_html=True)

    try:
        cursor = conn.cursor()
        
        # 1. جلب بيانات الموظفين المكلفين (المصممين، الفنيين، التركيب)
        cursor.execute("SELECT emp_name FROM employees WHERE role = 'Designer'")
        designers_list = [r[0] for r in cursor.fetchall()] or ["بدون مصمم"]
        
        cursor.execute("SELECT emp_name FROM employees WHERE role = 'Technician'")
        tech_list = [r[0] for r in cursor.fetchall()] or ["بدون فني"]
        
        cursor.execute("SELECT emp_name FROM employees WHERE role = 'Installer'")
        installers_list = [r[0] for r in cursor.fetchall()] or ["بدون فريق تركيب"]

        # 2. جلب الطلبات وعرضها في جدول تفاعلي
        query = "SELECT * FROM orders ORDER BY id DESC"
        df = pd.read_sql(query, conn)
        
        if df.empty:
            st.info("📭 لا توجد طلبات مسجلة حالياً. ابدأ بتسجيل أول طلب من صفحة 'طلب جديد'.")
            return

        # عرض ملخص سريع للحالات (Metrics)
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("إجمالي الطلبات", len(df))
        m2.metric("قيد التصميم", len(df[df['current_stage'] == 'التصميم']))
        m3.metric("في الإنتاج", len(df[df['current_stage'] == 'الطباعة والإنتاج']))
        m4.metric("بانتظار التركيب", len(df[df['current_stage'] == 'التركيب']))

        st.markdown("### 📋 سجل العمليات المفتوح")
        st.dataframe(df, use_container_width=True, hide_index=True)

        st.divider()

        # 3. مركز التحكم في الطلب (تحديث البيانات والطباعة)
        if 'work_order_sn' in df.columns:
            order_sns = df['work_order_sn'].unique().tolist()
            selected_sn = st.selectbox("🎯 اختر رقم الطلب للتحكم فيه:", order_sns)
            
            order_data = df[df['work_order_sn'] == selected_sn].iloc[0]
            
            col_action, col_print = st.columns([2, 1])

            with col_action:
                with st.expander(f"📝 تحديث سير العمل للطلب: {selected_sn}", expanded=True):
                    c1, c2, c3 = st.columns(3)
                    def get_idx(lst, val): return lst.index(val) if val in lst else 0

                    new_des = c1.selectbox("المصمم:", designers_list, index=get_idx(designers_list, order_data['designer']))
                    new_tech = c2.selectbox("الفني:", tech_list, index=get_idx(tech_list, order_data['technician']))
                    new_inst = c3.selectbox("التركيب:", installers_list, index=get_idx(installers_list, order_data['installer']))

                    c4, c5 = st.columns(2)
                    stages = ["التصميم", "الطباعة والإنتاج", "التركيب", "جاهز للتسليم"]
                    new_stage = c4.selectbox("المرحلة الحالية:", stages, index=get_idx(stages, order_data['current_stage']))
                    
                    statuses = ["نشط", "مكتمل", "قيد الانتظار", "ملغي"]
                    new_status = c5.selectbox("حالة الطلب:", statuses, index=get_idx(statuses, order_data['status']))

                    new_details = st.text_area("ملاحظات التنفيذ الإضافية:", value=order_data['details'])

                    if st.button("💾 حفظ تحديثات الإنتاج", use_container_width=True, type="primary"):
                        cursor.execute("""
                            UPDATE orders 
                            SET designer=%s, technician=%s, installer=%s, current_stage=%s, status=%s, details=%s 
                            WHERE work_order_sn=%s
                        """, (new_des, new_tech, new_inst, new_stage, new_status, new_details, selected_sn))
                        conn.commit()
                        st.success(f"✅ تم تحديث بيانات {selected_sn} بنجاح!")
                        st.rerun()

            with col_print:
                st.markdown("### 🖨️ مركز المخرجات")
                # زر أمر التشغيل (للفنيين والمصممين)
                if st.button("📑 طباعة أمر التشغيل", use_container_width=True):
                    cursor.execute("SELECT * FROM orders WHERE work_order_sn = %s", (selected_sn,))
                    order_dict = dict(zip([d[0] for d in cursor.description], cursor.fetchone()))
                    html_wo = generate_work_order_html(order_dict)
                    components.html(f"{html_wo} <script>window.onload = function() {{ window.print(); }}</script>", height=500, scrolling=True)
                
                # زر الفاتورة الضريبية (للعميل)
                if st.button("🧾 طباعة الفاتورة الضريبية", use_container_width=True):
                    cursor.execute("SELECT * FROM orders WHERE work_order_sn = %s", (selected_sn,))
                    order_dict_inv = dict(zip([d[0] for d in cursor.description], cursor.fetchone()))
                    
                    # جلب بيانات العميل الضريبية (السجل والرقم الضريبي)
                    cursor.execute("SELECT * FROM clients WHERE client_name = %s", (order_dict_inv['client_name'],))
                    client_row = cursor.fetchone()
                    client_data = dict(zip([d[0] for d in cursor.description], client_row)) if client_row else None
                    
                    html_inv = generate_invoice_html(order_dict_inv, client_data)
                    components.html(f"{html_inv} <script>window.onload = function() {{ window.print(); }}</script>", height=500, scrolling=True)

        else:
            st.error("⚠️ خطأ تقني: عمود 'work_order_sn' غير موجود في قاعدة البيانات.")

    except Exception as e:
        st.error(f"❌ فشل محرك العمليات: {e}")
