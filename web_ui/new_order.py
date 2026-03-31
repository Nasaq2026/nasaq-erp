import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import json

def render_new_order(conn):
    st.markdown("""
        <div style="text-align: right;">
            <h1 style="color: #1e293b;">➕ إضافة طلب تشغيل (نظام نَسق)</h1>
            <p style="color: #64748b;">تسجيل عميل جديد، تحديد المواصفات الفنية، وإسناد المهام للطاقم.</p>
        </div>
    """, unsafe_allow_html=True)
    
    try:
        cursor = conn.cursor()

        # 1. جلب الأصناف مع معالجة الـ JSONB
        cursor.execute("SELECT name, config_json FROM categories ORDER BY id ASC")
        raw_categories = cursor.fetchall()
        categories_data = {}
        for r in raw_categories:
            name, config = r[0], r[1]
            # التأكد من فك تشفير الـ JSON إذا جاء كنص، أو استخدامه مباشرة إذا جاء كقاموس
            categories_data[name] = config if isinstance(config, (list, dict)) else json.loads(config)
        
        # 2. جلب الموظفين
        cursor.execute("SELECT emp_name, role FROM employees")
        emps = cursor.fetchall()
        designers = [r[0] for r in emps if r[1] in ["Designer", "Admin"]]
        techs = [r[0] for r in emps if r[1] in ["Technician", "Admin"]]
        installers = [r[0] for r in emps if r[1] in ["Installer", "Admin"]]

        # 3. بيانات العميل والبحث الذكي
        st.markdown("### 👤 بيانات العميل")
        cursor.execute("SELECT phone, client_name, tax_number, cr_number, national_address, orders_count FROM clients")
        clients_list = cursor.fetchall()
        client_dict = {f"{r[0]} - {r[1]}": r for r in clients_list if r[0]}
        
        selected_client = st.selectbox("🔍 ابحث عن عميل سابق أو أضف جديد:", ["✨ عميل جديد"] + list(client_dict.keys()))

        p_name, p_phone, p_tax, p_cr, p_addr, p_count = "", "", "", "", "", 0
        if selected_client != "✨ عميل جديد":
            data = client_dict[selected_client]
            p_phone, p_name, p_tax, p_cr, p_addr, p_count = data
            st.info(f"✅ عميل حالي - إجمالي الطلبات: {p_count}")

        col_c1, col_c2, col_c3 = st.columns(3)
        c_name = col_c1.text_input("اسم العميل *", value=p_name)
        c_phone = col_c2.text_input("رقم الجوال *", value=p_phone)
        c_tax = col_c3.text_input("الرقم الضريبي", value=p_tax)
        
        col_c4, col_c5 = st.columns(2)
        c_cr = col_c4.text_input("السجل التجاري", value=p_cr)
        c_addr = col_c5.text_input("العنوان الوطني", value=p_addr)

        st.divider()

        # 4. إسناد المهام
        st.markdown("### 👥 إسناد المهام")
        col_m1, col_m2, col_m3 = st.columns(3)
        assigned_des = col_m1.selectbox("المصمم المكلّف", ["غير محدد"] + designers)
        assigned_tec = col_m2.selectbox("فني الطباعة/القص", ["غير محدد"] + techs)
        assigned_inst = col_m3.selectbox("عامل التركيب", ["غير محدد"] + installers)
        req_install = st.checkbox("يتطلب تركيب ميداني ✅")

        st.divider()

        # 5. تفاصيل العمل الديناميكية
        st.markdown("### ⚙️ تفاصيل المواصفات الفنية")
        if not categories_data:
            st.error("⚠️ لم يتم العثور على أقسام في قاعدة البيانات. يرجى إضافتها من الإعدادات.")
            return

        category = st.selectbox("القسم / نوع الخدمة *", list(categories_data.keys()))
        
        dynamic_values = {}
        fields = categories_data.get(category, [])
        
        if fields:
            cols = st.columns(2)
            for i, field in enumerate(fields):
                # التحقق من هيكلة الـ JSON (توقعنا: [اسم، نوع، خيارات])
                if len(field) >= 3:
                    label, f_type, options = field[0], field[1], field[2]
                    with cols[i % 2]:
                        if f_type == "combo":
                            dynamic_values[label] = st.selectbox(label, options, key=f"{category}_{label}")
                        else:
                            dynamic_values[label] = st.text_input(label, placeholder=str(options), key=f"{category}_{label}")

        st.divider()

        # 6. المالية وموعد التسليم
        st.markdown("### 💰 المالية وموعد التسليم")
        
        # حساب الوقت (تقديري بناءً على المساحة إن وجدت)
        w, h = 1.0, 1.0
        for label, val in dynamic_values.items():
            try:
                if "عرض" in label: w = float(val) / 100
                if "طول" in label: h = float(val) / 100
            except: pass
        
        est_hours = (w * h * 2) + 1
        expected_delivery = datetime.now() + timedelta(hours=est_hours)
        st.write(f"⏳ **موعد التسليم المتوقع:** {expected_delivery.strftime('%Y-%m-%d | %I:%M %p')}")

        col_f1, col_f2, col_f3 = st.columns(3)
        price = col_f1.number_input("السعر (بدون ضريبة) *", min_value=0.0)
        cost = col_f2.number_input("التكلفة المتوقعة", min_value=0.0)
        paid = col_f3.number_input("المبلغ المدفوع", min_value=0.0)

        specs_summary = "\n".join([f"{k}: {v}" for k, v in dynamic_values.items()])

        if st.button("💾 حفظ الطلب وإرسال التكليف", type="primary", use_container_width=True):
            if c_name and c_phone and price > 0:
                # 1. تحديث بيانات العميل
                cursor.execute("""
                    INSERT INTO clients (client_name, phone, tax_number, cr_number, national_address, orders_count)
                    VALUES (%s, %s, %s, %s, %s, 1)
                    ON CONFLICT (phone) DO UPDATE SET orders_count = clients.orders_count + 1
                """, (c_name, c_phone, c_tax, c_cr, c_addr))

                # 2. حفظ الطلب الجديد
                wo_sn = f"WO-{datetime.now().strftime('%m%d%H%M')}"
                vat = price * 0.15
                total = price + vat
                profit = price - cost
                
                sql = """
                    INSERT INTO orders (
                        client_name, phone, price, vat, total_with_vat, paid, cost, profit, status, 
                        current_stage, category, details, designer, technician, installer, 
                        requires_install, work_order_sn, estimated_hours, expected_delivery
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, 'نشط', 'التصميم', %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """
                cursor.execute(sql, (
                    c_name, c_phone, price, vat, total, paid, cost, profit, 
                    category, specs_summary, assigned_des, assigned_tec, assigned_inst, 
                    req_install, wo_sn, est_hours, expected_delivery
                ))
                conn.commit()
                st.success(f"🚀 تم الحفظ! رقم الطلب: {wo_sn}")
                st.balloons()
            else:
                st.error("⚠️ يرجى إكمال البيانات الأساسية (الاسم، الجوال، السعر)")

    except Exception as e:
        if conn: conn.rollback()
        st.error(f"❌ خطأ في النظام: {e}")
