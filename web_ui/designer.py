# web_ui/designer.py
import streamlit as st
import pandas as pd

def render_designer(conn, emp_name):
    st.title("🎨 مساحة عمل المصمم")
    st.info(f"أهلاً بك يا {emp_name}. هذه الطلبات بانتظار إبداعك الفني!")

    try:
        conn.rollback()
        cursor = conn.cursor()
        
        # جلب الطلبات التي في مرحلة التصميم ومسندة لهذا المصمم
        query = """
            SELECT id, work_order_sn, client_name, category, details, file_url 
            FROM orders 
            WHERE current_stage = 'التصميم' AND status = 'نشط' AND designer = %s
        """
        cursor.execute(query, (emp_name,))
        tasks = cursor.fetchall()

        if not tasks:
            st.success("🎉 لا توجد مهام تصميم حالياً. استمتع بوقتك!")
            return

        for task in tasks:
            order_id, sn, client, cat, details, file_url = task
            with st.expander(f"📦 أمر عمل: {sn} | العميل: {client} | القسم: {cat}"):
                st.write(f"**المطلوب:** {details or 'لا توجد ملاحظات إضافية'}")
                
                # تحديث رابط التصميم
                with st.form(f"form_designer_{order_id}"):
                    new_link = st.text_input("🔗 رابط ملف التصميم (Google Drive / Dropbox):", 
                                            value=file_url if file_url else "")
                    
                    if st.form_submit_button("✅ اعتماد التصميم وإرساله للإنتاج"):
                        if new_link.strip():
                            cursor.execute("""
                                UPDATE orders 
                                SET file_url = %s, current_stage = 'الطباعة والإنتاج' 
                                WHERE id = %s
                            """, (new_link, order_id))
                            conn.commit()
                            st.success("🚀 تم إرسال العمل بنجاح لقسم الإنتاج!")
                            st.rerun()
                        else:
                            st.error("⚠️ يرجى وضع رابط الملف أولاً قبل الاعتماد.")
    except Exception as e:
        st.error(f"حدث خطأ في واجهة المصمم: {e}")