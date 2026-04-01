import streamlit as st
import pandas as pd

def render_orders_manager(conn):
    st.markdown("<h2 style='text-align: right; color: #1e293b;'>📦 إدارة العمليات وأوامر التشغيل</h2>", unsafe_allow_html=True)
    
    cursor = conn.cursor()
    # جلب البيانات - استخدمنا استعلام بسيط لتجنب البطء
    try:
        df = pd.read_sql("SELECT * FROM orders ORDER BY id DESC", conn)
    except:
        st.error("مشكلة في الاتصال بقاعدة البيانات")
        return

    if df.empty:
        st.info("لا توجد طلبات مسجلة حالياً.")
        return

    # نظام البحث السريع
    search = st.text_input("🔍 ابحث برقم الطلب أو اسم العميل:")
    if search:
        df = df[df['client_name'].str.contains(search, case=False) | df['work_order_sn'].str.contains(search, case=False)]

    for _, row in df.iterrows():
        # تصميم بطاقة الطلب (Card Design)
        with st.expander(f"📄 {row['work_order_sn']} | {row['client_name']} - [{row['current_stage']}]"):
            c1, c2, c3 = st.columns([2, 1, 1])
            
            with c1:
                st.markdown(f"**المشروع:** {row['project_name']}")
                st.markdown(f"**المالية:** مدفوع: {row['paid_amount']} | <span style='color:red'>متبقي: {row['remaining_amount']}</span>", unsafe_allow_html=True)
                st.caption(f"القسم: {row['category']} | الخامة: {row['material_type']}")
            
            with c2:
                # تحديث المرحلة
                stages = ["التصميم", "الإنتاج", "التركيب", "مكتمل"]
                current_idx = stages.index(row['current_stage']) if row['current_stage'] in stages else 0
                new_stg = st.selectbox("المرحلة:", stages, index=current_idx, key=f"s_{row['id']}")
                if st.button("تحديث الحالة", key=f"u_{row['id']}"):
                    cursor.execute("UPDATE orders SET current_stage=%s WHERE id=%s", (new_stg, row['id']))
                    conn.commit()
                    st.rerun()

            with c3:
                # عمليات الإدارة
                if st.button("🗑️ حذف الطلب", key=f"d_{row['id']}", type="secondary", use_container_width=True):
                    cursor.execute("DELETE FROM orders WHERE id=%s", (row['id'],))
                    conn.commit()
                    st.rerun()
                
                # رابط واتساب سريع
                msg = f"مرحباً {row['client_name']}، طلبكم {row['work_order_sn']} الآن في مرحلة: {row['current_stage']}"
                st.markdown(f"[💬 واتساب تحديث](https://wa.me/{row['phone']}?text={msg})")
