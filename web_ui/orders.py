# ... نفس الاستيرادات السابقة ...

def render_orders(conn):
    # ... نفس كود العنوان ...

    try:
        # استخدام cursor للتأكد من تحديث البيانات
        cursor = conn.cursor()
        
        # سحب البيانات باستخدام pandas
        query = "SELECT * FROM orders ORDER BY id DESC"
        df = pd.read_sql(query, conn)
        
        if df.empty:
            st.warning("📭 لا توجد طلبات مسجلة حالياً في النظام.")
            return

        # عرض الجدول
        st.markdown("### 📋 سجل الطلبات الحالي")
        st.dataframe(df, width=1200, hide_index=True)

        st.divider()

        # إدارة أمر العمل
        st.markdown("### ⚙️ إدارة وتحكم في أمر العمل")
        
        # التأكد من وجود عمود work_order_sn
        if 'work_order_sn' not in df.columns:
            st.error("⚠️ عمود 'work_order_sn' غير موجود في قاعدة البيانات. يرجى تحديث الجدول.")
            return

        selected_order_sn = st.selectbox("🎯 اختر رقم (أمر العمل) للتحكم فيه:", df['work_order_sn'].unique())
        
        # جلب بيانات الصف المختار كقاموس (أسهل للتعامل)
        order_data_row = df[df['work_order_sn'] == selected_order_sn].iloc[0]

        with st.expander(f"📝 تعديل وتكليف الطاقم للطلب: {selected_order_sn}", expanded=True):
            # ... كود الـ Selectboxes (تصميم، فني، تركيب) ...
            # تأكد من إضافة قِيَم افتراضية إذا كانت الخانات فارغة في القاعدة
            current_des = order_data_row.get('designer', 'بدون مصمم')
            # ... (باقي كود التعديل كما هو في ملفك) ...

            if st.button("💾 حفظ التحديثات وإخطار الفريق", use_container_width=True):
                # التحديث باستخدام الأسماء لضمان الدقة
                update_query = """
                    UPDATE orders 
                    SET designer = %s, technician = %s, installer = %s, 
                        current_stage = %s, status = %s, details = %s
                    WHERE work_order_sn = %s
                """
                cursor.execute(update_query, (new_des, new_tech, new_inst, new_stage, new_status, new_details, selected_order_sn))
                conn.commit()
                st.success("✅ تم التحديث!")
                st.rerun()

        st.divider()

        # مركز الطباعة
        st.markdown("### 🖨️ مركز طباعة المستندات (نسق)")
        
        c1, c2 = st.columns(2)

        # تحويل الصف إلى قائمة لإرسالها للدوال (مع التأكد من الترتيب)
        row_list = order_data_row.values.tolist()

        if c1.button("📑 توليد أمر تشغيل (ورشة)", use_container_width=True):
            html_wo = generate_work_order_html(row_list)
            st.download_button("📥 تحميل أمر العمل", data=html_wo, file_name=f"WO_{selected_order_sn}.html", mime="text/html")
            components.html(html_wo, height=600, scrolling=True)

        if c2.button("🧾 توليد فاتورة ضريبية", use_container_width=True):
            # جلب بيانات العميل (تأكد من وجود جدول clients)
            cursor.execute("SELECT * FROM clients WHERE phone = %s", (str(order_data_row['phone']),))
            client_data = cursor.fetchone()
            
            html_inv = generate_invoice_html(row_list, client_data)
            st.download_button("📥 تحميل الفاتورة", data=html_inv, file_name=f"Invoice_{selected_order_sn}.html", mime="text/html")
            components.html(html_inv, height=600, scrolling=True)

    except Exception as e:
        st.error(f"❌ حدث خطأ: {e}")
