# web_ui/installer.py
import streamlit as st

def render_installer(conn, emp_name):
    st.markdown(f"""
        <div style="text-align: right;">
            <h1 style="color: #1e293b;">🚛 قسم التركيبات الميدانية</h1>
            <p style="color: #64748b;">أهلاً بك يا <b>{emp_name}</b>. المهام المطلوب تنفيذها في الموقع:</p>
        </div>
    """, unsafe_allow_html=True)

    try:
        conn.rollback()
        cursor = conn.cursor()
        
        # جلب مهام التركيب النشطة لهذا الموظف
        cursor.execute("""
            SELECT id, work_order_sn, client_name, dimensions, details, material_type 
            FROM orders 
            WHERE current_stage = 'التركيب' AND status = 'نشط' AND installer = %s
            ORDER BY id ASC
        """, (emp_name,))
        tasks = cursor.fetchall()

        if not tasks:
            st.success("🎉 لا توجد مهام تركيب حالياً. بالتوفيق في طريقك!")
            return

        for task in tasks:
            order_id, sn, client, dims, details, mat = task
            
            with st.expander(f"🚛 تركيب رقم: {sn} | العميل: {client}", expanded=True):
                st.markdown(f"**📏 المقاسات:** `{dims if dims else '---'}` | **💎 الخامة:** `{mat if mat else '---'}`")
                st.info(f"📝 **ملاحظات الموقع:** {details if details else 'لا توجد.'}")
                
                # زر إنهاء المهمة
                if st.button(f"✅ تم التركيب (إغلاق الطلب)", key=f"inst_btn_{order_id}", width="stretch"):
                    cursor.execute("UPDATE orders SET current_stage = 'مكتمل', status = 'مكتمل' WHERE id = %s", (order_id,))
                    conn.commit()
                    st.success(f"🚀 ممتاز! تم إنهاء الطلب {sn} بنجاح.")
                    st.balloons()
                    st.rerun()

    except Exception as e:
        st.error(f"❌ خطأ في واجهة التركيب: {e}")
