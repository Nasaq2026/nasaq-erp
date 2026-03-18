# web_ui/installer.py
import streamlit as st

def render_installer(conn, emp_name):
    st.title("🛠️ قسم التركيبات الميدانية")
    st.info("اللوحات والطلبات الجاهزة للتركيب عند العملاء:")
    
    try:
        conn.rollback()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, work_order_sn, client_name, details, dimensions 
            FROM orders 
            WHERE current_stage = 'التركيب' AND status = 'نشط' AND installer = %s
        """, (emp_name,))
        tasks = cursor.fetchall()
        
        if not tasks:
            st.success("🎉 لا توجد مهام تركيب حالياً.")
            return

        for task in tasks:
            order_id, sn, client, details, dims = task
            with st.expander(f"🛠️ أمر: {sn} | العميل: {client}"):
                st.write(f"**المقاسات:** {dims or '---'}")
                st.write(f"**ملاحظات التركيب:** {details or '---'}")
                
                if st.button("✅ تم التركيب بنجاح (إنهاء الطلب)", key=f"inst_{order_id}"):
                    cursor.execute("UPDATE orders SET current_stage = 'مكتمل', status = 'مكتمل' WHERE id = %s", (order_id,))
                    conn.commit()
                    st.success("🏆 تم إقفال الطلب بنجاح. عاش يا أبطال!")
                    st.rerun()
    except Exception as e:
        st.error(f"خطأ: {e}")