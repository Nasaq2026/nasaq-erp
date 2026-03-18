# web_ui/new_order.py
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import re

# ⏱️ أزمنة العمليات القياسية (بالساعات) لعام 2026
OPERATION_TIMES = {
    'تصميم لوجو': 5.0,
    'تصميم بوستر': 2.0,
    'مطبوعات ورقية': 1.0,
    'ستيكر وعلامات تجارية': 0.5, 
    'لوحات محلات': 4.0,
    'حروف بارزة': 6.0,
    'قص ليزر / أكريليك': 0.25,
    'افتراضي': 1.0
}

def render_new_order(conn):
    st.markdown("""
        <div style="text-align: right;">
            <h1 style="color: #1e293b; margin-bottom: 0;">➕ إضافة طلب تشغيل (نظام ذكي)</h1>
            <p style="color: #64748b;">نظام جدولة تلقائي يحسب موعد التسليم بناءً على ضغط الورشة الحالي.</p>
        </div>
    """, unsafe_allow_html=True)

    try:
        conn.rollback()
        cursor = conn.cursor()

        # جلب القوائم الفنية
        cursor.execute("SELECT name FROM designers")
        designers_list = [r[0] for r in cursor.fetchall()] or ["بدون مصمم"]
        
        cursor.execute("SELECT emp_name FROM employees WHERE role = 'Technician'")
        tech_list = [r[0] for r in cursor.fetchall()] or ["بدون فني"]
        
        cursor.execute("SELECT emp_name FROM employees WHERE role = 'Installer'")
        installers_list = [r[0] for r in cursor.fetchall()] or ["بدون فريق تركيب"]

        # ==========================================
        # 1. بيانات العميل (محرك البحث الذكي)
        # ==========================================
        st.markdown("### 👤 بيانات العميل")
        
        cursor.execute("SELECT phone, client_name, tax_number, cr_number, national_address, orders_count FROM clients")
        clients_data = cursor.fetchall()
        client_dict = {f"{r[0]} - {r[1]}": r for r in clients_data if r[0]}
        
        client_options = ["✨ إضافة عميل جديد (اكتب البيانات بالأسفل)"] + list(client_dict.keys())
        selected_client = st.selectbox("🔍 ابحث برقم الجوال أو اسم العميل:", client_options)

        pre_name, pre_phone, pre_tax, pre_cr, pre_addr = "", "", "", "", ""
        if selected_client != "✨ إضافة عميل جديد (اكتب البيانات بالأسفل)":
            data = client_dict[selected_client]
            pre_phone, pre_name = data[0], data[1]
            pre_tax, pre_cr, pre_addr = data[2] or "", data[3] or "", data[4] or ""
            
            if data[5] >= 3:
                st.info(f"🌟 عميل مميز (VIP) - إجمالي طلباته السابقة: {data[5]}")
            else:
                st.success("✅ عميل مسجل مسبقاً في قاعدة البيانات")

        col_c1, col_c2, col_c3 = st.columns(3)
        c_name = col_c1.text_input("اسم العميل *", value=pre_name)
        c_phone = col_c2.text_input("رقم الجوال *", value=pre_phone)
        c_tax = col_c3.text_input("الرقم الضريبي", value=pre_tax)
        
        col_c4, col_c5 = st.columns(2)
        c_cr = col_c4.text_input("السجل التجاري", value=pre_cr)
        c_addr = col_c5.text_input("العنوان الوطني", value=pre_addr)

        st.divider()

        # ==========================================
        # 2. تفاصيل العمل الفني
        # ==========================================
        st.markdown("### 🛠️ تفاصيل العمل والمقاسات")
        col_t1, col_t2 = st.columns(2)
        category = col_t1.selectbox("القسم الإنشائي *", list(OPERATION_TIMES.keys())[:-1])
        mat_type = col_t2.text_input("نوع الخامة المستخدمة")
        
        dims = st.text_input("المقاسات (مثال: 2*3 متر)")
        details = st.text_area("تفاصيل التصميم وملاحظات الإنتاج")

        st.divider()

        # ==========================================
        # 3. محرك حساب الجدولة (Smart Scheduling)
        # ==========================================
        st.markdown("### 👥 إسناد المهام والموعد المتوقع")
        col_m1, col_m2, col_m3 = st.columns(3)
        des = col_m1.selectbox("المصمم المكلف", designers_list)
        tec = col_m2.selectbox("الفني المكلف", tech_list)
        inst = col_m3.selectbox("فريق التركيب", installers_list)
        
        req_install = st.checkbox("يتطلب تركيب ميداني (Site Installation)")

        # 🧠 خوارزمية حساب الوقت التلقائية
        base_time = OPERATION_TIMES.get(category, OPERATION_TIMES['افتراضي'])
        if "ستيكر" in category or "بنر" in category:
            try:
                numbers = [float(n) for n in re.findall(r'\d+\.?\d*', dims)]
                if len(numbers) >= 2:
                    area = numbers[0] * numbers[1]
                    base_time = area * OPERATION_TIMES[category]
            except: pass
            
        estimated_hours = base_time

        cursor.execute("SELECT SUM(estimated_hours) FROM orders WHERE status = 'نشط' AND (designer = %s OR technician = %s)", (des, tec))
        res = cursor.fetchone()
        backlog_hours = float(res[0]) if res and res[0] else 0.0

        total_wait_hours = backlog_hours + estimated_hours
        days_to_add = int(total_wait_hours // 8) # افتراض 8 ساعات عمل يومياً
        hours_to_add = total_wait_hours % 8
        expected_delivery = datetime.now() + timedelta(days=days_to_add, hours=hours_to_add)
        formatted_date = expected_delivery.strftime("%Y-%m-%d | %I:%M %p")

        # تنبيهات مرئية للمدير عن حالة الضغط
        if total_wait_hours <= 8:
            st.success(f"🟢 التسليم المتوقع: متاح خلال 24 ساعة ({formatted_date})")
        elif total_wait_hours <= 24:
            st.warning(f"🟡 التسليم المتوقع: خلال 3 أيام عمل ({formatted_date})")
        else:
            st.error(f"🔴 تنبيه: ضغط عمل مرتفع! الموعد المتوقع: ({formatted_date})")

        st.divider()

        # ==========================================
        # 4. الحسابات المالية والحفظ
        # ==========================================
        st.markdown("### 💰 المبالغ المالية")
        col_f1, col_f2, col_f3 = st.columns(3)
        price = col_f1.number_input("السعر المتفق عليه (بدون ضريبة) *", min_value=0.0, step=10.0)
        cost = col_f2.number_input("التكلفة المباشرة (خامات + عمالة)", min_value=0.0, step=10.0)
        paid = col_f3.number_input("المبلغ المدفوع كعربون", min_value=0.0, step=10.0)

        # ✅ زر الحفظ المحدث لمعايير Streamlit 2026
        if st.button("💾 حفظ الطلب وإصدار أمر التشغيل", width="stretch"):
            if c_name and c_phone and price > 0:
                # تحديث سجل العميل
                if selected_client != "✨ إضافة عميل جديد (اكتب البيانات بالأسفل)":
                    cursor.execute("UPDATE clients SET orders_count = orders_count + 1 WHERE phone=%s", (c_phone,))
                else:
                    cursor.execute("""
                        INSERT INTO clients (client_name, phone, tax_number, cr_number, national_address, orders_count) 
                        VALUES (%s, %s, %s, %s, %s, 1) ON CONFLICT (phone) DO NOTHING
                    """, (c_name, c_phone, c_tax, c_cr, c_addr))

                # حسابات الضريبة والربح
                vat = price * 0.15
                total = price + vat
                profit = price - cost
                wo_sn = f"WO-{datetime.now().strftime('%m%d%H%M')}"

                # الحفظ النهائي في قاعدة البيانات
                sql = """
                    INSERT INTO orders (client_name, phone, price, vat, total_with_vat, paid, cost, profit, status, 
                    current_stage, category, details, designer, technician, installer, requires_install, 
                    work_order_sn, material_type, dimensions, estimated_hours, expected_delivery) 
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, 'نشط', 'التصميم', %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """
                cursor.execute(sql, (c_name, c_phone, price, vat, total, paid, cost, profit, category, details, des, tec, inst, req_install, wo_sn, mat_type, dims, estimated_hours, expected_delivery))
                conn.commit()
                
                st.session_state.last_order_count += 1
                st.success(f"🚀 تم حفظ الطلب بنجاح برقم {wo_sn}! تم إخطار فريق العمل.")
                st.balloons()
                st.rerun()
            else:
                st.error("⚠️ بيانات ناقصة: يرجى التأكد من كتابة اسم العميل، الجوال، وسعر البيع.")

    except Exception as e:
        st.error(f"❌ خطأ تقني في النظام: {e}")
