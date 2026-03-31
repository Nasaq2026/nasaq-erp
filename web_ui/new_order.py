# ... (نفس الاستيرادات) ...

def render_new_order(conn):
    st.title("➕ إضافة طلب تشغيل (نظام نَسق)")
    
    try:
        cursor = conn.cursor()

        # 1. جلب الأقسام مع معالجة الـ JSON
        cursor.execute("SELECT name, config_json FROM categories ORDER BY id ASC")
        rows = cursor.fetchall()
        categories_data = {}
        for r in rows:
            # التأكد من نوع البيانات (dict أو str)
            config = r[1]
            categories_data[r[0]] = config if isinstance(config, dict) else json.loads(config)
        
        # ... (كود جلب الموظفين والعملاء كما هو) ...

        # 4. تفاصيل العمل (تعديل بسيط لقراءة الحقول)
        st.markdown("### ⚙️ تفاصيل المواصفات الفنية")
        category = st.selectbox("القسم / نوع الخدمة *", list(categories_data.keys()))
        
        dynamic_values = {}
        if category in categories_data:
            fields = categories_data[category]
            # ملاحظة: تأكد أن التنسيق في قاعدة البيانات هو قائمة من الحقول
            # إذا كان التنسيق {'key': 'value'} سنحتاج لتعديل الـ Loop
            if isinstance(fields, dict):
                cols = st.columns(2)
                for i, (label, options) in enumerate(fields.items()):
                    with cols[i % 2]:
                        dynamic_values[label] = st.text_input(label, value=str(options))
            else:
                # الكود الأصلي الخاص بك إذا كان التنسيق List of Lists
                cols = st.columns(2)
                for i, field in enumerate(fields):
                    label, f_type, options = field[0], field[1], field[2]
                    with cols[i % 2]:
                        if f_type == "combo":
                            dynamic_values[label] = st.selectbox(label, options)
                        else:
                            dynamic_values[label] = st.text_input(label, placeholder=str(options))

        # ... (كود الحسابات المالية كما هو) ...

        if st.button("💾 حفظ الطلب وإرسال التكليف", type="primary", use_container_width=True):
            if c_name and c_phone and price > 0:
                # حساب القيم الضريبية
                vat = price * 0.15
                total = price + vat
                wo_sn = f"WO-{datetime.now().strftime('%m%d%H%M')}"
                
                # تنفيذ الحفظ (تأكد من ترتيب الأعمدة في قاعدة البيانات)
                sql = """
                    INSERT INTO orders (
                        client_name, phone, price, vat, total_with_vat, paid, cost, 
                        status, current_stage, category, details, designer, 
                        technician, installer, requires_install, work_order_sn, 
                        estimated_hours, expected_delivery
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, 'نشط', 'التصميم', %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """
                cursor.execute(sql, (
                    c_name, c_phone, price, vat, total, paid, cost, 
                    category, specs_summary, assigned_des, assigned_tec, 
                    assigned_inst, req_install, wo_sn, est_hours, expected_delivery
                ))
                conn.commit()
                st.success(f"🚀 تم الحفظ بنجاح! رقم أمر العمل: {wo_sn}")
                st.balloons()
    except Exception as e:
        st.error(f"❌ حدث خطأ: {e}")
