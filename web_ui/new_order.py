# web_ui/new_order.py
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import json
import re

def render_new_order(conn):
    st.title("➕ إضافة طلب تشغيل (النظام المطور)")
    
    try:
        cursor = conn.cursor()

        # ==========================================
        # 1. جلب البيانات الأساسية (الأقسام والموظفين)
        # ==========================================
        cursor.execute("SELECT name, config_json FROM categories ORDER BY id ASC")
        categories_data = {r[0]: json.loads(r[1]) for r in cursor.fetchall()}
        
        cursor.execute("SELECT emp_name, role FROM employees")
        emps = cursor.fetchall()
        designers = [r[0] for r in emps if r[1] in ["Designer", "Admin"]]
        techs = [r[0] for r in emps if r[1] in ["Technician", "Admin"]]
        installers = [r[0] for r in emps if r[1] in ["Installer", "Admin"]]

        # ==========================================
        # 2. بيانات العميل والبحث الذكي
        # ==========================================
        st.markdown("### 👤 بيانات العميل")
        cursor.execute("SELECT phone, client_name, tax_number, cr_number, national_address, orders_count FROM clients")
        clients_list = cursor.fetchall()
        client_dict = {f"{r[0]} - {r[1]}": r for r in clients_list if r[0]}
        
        selected_client = st.selectbox("🔍 ابحث عن عميل سابق أو أضف جديد:", ["✨ عميل جديد"] + list(client_dict.keys()))

        # تجهيز القيم تلقائياً عند اختيار عميل
        p_name, p_phone, p_tax, p_cr, p_addr, p_count = "", "", "", "", "", 0
        if selected_client != "✨ عميل جديد":
            data = client_dict[selected_client]
            p_phone, p_name, p_tax, p_cr, p_addr, p_count = data
            if p_count >= 3:
                st.warning("🌟 هذا العميل مميز (VIP) - يرجى الاهتمام بالأولوية")
            else:
                st.info("✅ عميل حالي")

        col_c1, col_c2, col_c3 = st.columns(3)
        c_name = col_c1.text_input("اسم العميل *", value=p_name)
        c_phone = col_c2.text_input("رقم الجوال *", value=p_phone)
        c_tax = col_c3.text_input("الرقم الضريبي", value=p_tax)
        
        col_c4, col_c5 = st.columns(2)
        c_cr = col_c4.text_input("السجل التجاري", value=p_cr)
        c_addr = col_c5.text_input("العنوان الوطني", value=p_addr)

        st.divider()

        # ==========================================
        # 3. إسناد المهام (التكليف)
        # ==========================================
        st.markdown("### 👥 إسناد المهام")
        col_m1, col_m2, col_m3 = st.columns(3)
        assigned_des = col_m1.selectbox("المصمم المكلّف", ["غير محدد"] + designers)
        assigned_tec = col_m2.selectbox("فني الطباعة/القص", ["غير محدد"] + techs)
        assigned_inst = col_m3.selectbox("عامل التركيب", ["غير محدد"] + installers)
        req_install = st.checkbox("يتطلب تركيب ميداني ✅")

        st.divider()

        # ==========================================
        # 4. تفاصيل العمل (ديناميكية بالكامل)
        # ==========================================
        st.markdown("### ⚙️ تفاصيل المواصفات الفنية")
        category = st.selectbox("القسم / نوع الخدمة *", list(categories_data.keys()))
        
        # توليد الحقول بناءً على القسم المختار
        dynamic_values = {}
        if category in categories_data:
            fields = categories_data[category]
            # توزيع الحقول في أعمدة (2 في كل صف)
            cols = st.columns(2)
            for i, field in enumerate(fields):
                label, f_type, options = field[0], field[1], field[2]
                with cols[i % 2]:
                    if f_type == "combo":
                        dynamic_values[label] = st.selectbox(label, options)
                    else:
                        dynamic_values[label] = st.text_input(label, placeholder=str(options))

        st.divider()

        # ==========================================
        # 5. حساب الوقت (سم) والمالية
        # ==========================================
        st.markdown("### 💰 المالية وموعد التسليم")
        
        # خوارزمية حساب الوقت بناءً على الحقول الديناميكية (سم)
        w, h = 1.0, 1.0
        for label, val in dynamic_values.items():
            try:
                if "عرض" in label: w = float(val) / 100
                if "طول" in label: h = float(val) / 100
            except: pass
        
        # معادلة الوقت: (المساحة * 2 ساعة) + ساعة تجهيز
        est_hours = (w * h * 2) + 1
        expected_delivery = datetime.now() + timedelta(hours=est_hours)
        
        st.write(f"⏳ **موعد التسليم المتوقع:** {expected_delivery.strftime('%Y-%m-%d | %I:%M %p')}")

        col_f1, col_f2, col_f3 = st.columns(3)
        price = col_f1.number_input("السعر (بدون ضريبة) *", min_value=0.0)
        cost = col_f2.number_input("التكلفة المتوقعة", min_value=0.0)
        paid = col_f3.number_input("المبلغ المدفوع", min_value=0.0)

        # تجميع المواصفات لنص واحد للتخزين في خانة details
        specs_summary = "\n".join([f"{k}: {v}" for k, v in dynamic_values.items()])

        if st.button("💾 حفظ الطلب وإرسال التكليف للموظفين", type="primary", use_container_width=True):
            if c_name and c_phone and price > 0:
                # 1. تحديث/إضافة العميل
                cursor.execute("""
                    INSERT INTO clients (client_name, phone, tax_number, cr_number, national_address, orders_count)
                    VALUES (%s, %s, %s, %s, %s, 1)
                    ON CONFLICT (phone) DO UPDATE SET orders_count = clients.orders_count + 1
                """, (c_name, c_phone, c_tax, c_cr, c_addr))

                # 2. حفظ الطلب
                wo_sn = f"WO-{datetime.now().strftime('%m%d%H%M')}"
                vat = price * 0.15
                sql = """
                    INSERT INTO orders (client_name, phone, price, vat, total_with_vat, paid, cost, profit, status, 
                    current_stage, category, details, designer, technician, installer, requires_install, 
                    work_order_sn, estimated_hours, expected_delivery) 
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, 'نشط', 'التصميم', %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """
                cursor.execute(sql, (
                    c_name, c_phone, price, vat, price+vat, paid, cost, price-cost, 
                    category, specs_summary, assigned_des, assigned_tec, assigned_inst, 
                    req_install, wo_sn, est_hours, expected_delivery
                ))
                conn.commit()
                st.success(f"🚀 تم الحفظ! رقم الطلب: {wo_sn}")
                st.balloons()
            else:
                st.error("⚠️ يرجى إكمال البيانات الأساسية (الاسم، الجوال، السعر)")

    except Exception as e:
        conn.rollback()
        st.error(f"❌ خطأ: {e}")
