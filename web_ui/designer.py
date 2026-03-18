# web_ui/designer.py
import streamlit as st

def render_designer(conn, emp_name):
    # عنوان احترافي يتناسب مع الهوية الجديدة
    st.markdown(f"""
        <div style="text-align: right;">
            <h1 style="color: #1e293b;">🎨 مساحة عمل المصمم</h1>
            <p style="color: #64748b;">أهلاً بك يا <b>{emp_name}</b>. هذه الطلبات بانتظار إبداعك الفني!</p>
        </div>
    """, unsafe_allow_html=True)

    try:
        conn.rollback()
        cursor = conn.cursor()
        
        # جلب الطلبات التي في مرحلة التصميم ومسندة لهذا المصمم
        query = """
            SELECT id, work_order_sn, client_name, category, details, file_url 
            FROM orders 
            WHERE current_stage = 'التصميم' AND status = 'نشط' AND designer = %s
            ORDER BY id ASC
        """
        cursor.execute(query, (emp_name,))
        tasks = cursor.fetchall()

        if not tasks:
            st.success("🎉 لا توجد مهام تصميم حالياً. استمتع بوقتك أو راجع الأعمال السابقة!")
            return

        # عرض المهام على شكل كروت قابلة للتوسيع
        for task in tasks:
            order_id, sn, client, cat, details, file_url = task
            
            with st.expander(f"📦 أمر عمل: {sn} | العميل: {client} | القسم: {cat}", expanded=True):
                st.markdown(f"**📝 تفاصيل المطلوب:**")
                st.info(details if details else "لا توجد ملاحظات إضافية من الإدارة.")
                
                # نموذج تسليم العمل
                with st.form(f"form_designer_{order_id}"):
                    st.markdown("**🚀 تسليم التصميم النهائي:**")
                    new_link = st.text_input("🔗 رابط ملف التصميم (Google Drive / Dropbox / WeTransfer):", 
                                             value=file_url if file_url else "",
                                             placeholder="اضع الرابط هنا...")
                    
                    # ✅ تحديث الزر للكود الجديد width="stretch"
                    submit_design = st.form_submit_button("✅ اعتماد التصميم وإرساله لقسم الإنتاج", width="stretch")
                    
                    if submit_design:
                        if new_link.strip():
                            cursor.execute("""
                                UPDATE orders 
                                SET file_url = %s, current_stage = 'الطباعة والإنتاج' 
                                WHERE id = %s
                            """, (new_link, order_id))
                            conn.commit()
                            st.success(f"🚀 ممتاز! تم إرسال الطلب {sn} بنجاح إلى قسم الإنتاج.")
                            st.balloons()
                            st.rerun()
                        else:
                            st.error("⚠️ خطأ: يجب وضع رابط ملف التصميم قبل الضغط على زر الاعتماد.")

    except Exception as e:
        st.error(f"❌ حدث خطأ في واجهة المصمم: {e}")
