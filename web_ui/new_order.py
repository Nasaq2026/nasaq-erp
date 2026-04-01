import streamlit as st
from datetime import datetime
from utils.add_client_modal import add_client_modal_dialog

def render_new_order(conn):
    st.markdown("<h2 style='text-align: right; color: #fb923c;'>🚀 إنشاء طلب جديد - نَسق</h2>", unsafe_allow_html=True)
    
    cursor = conn.cursor()
    # جلب قائمة العملاء
    cursor.execute("SELECT client_name, phone FROM clients ORDER BY id DESC")
    clients_dict = {row[0]: row[1] for row in cursor.fetchall()}
    
    col_c, col_b = st.columns([4, 1])
    selected_client = col_c.selectbox("👤 اختر العميل:", ["-- اختر عميل --"] + list(clients_dict.keys()))
    if col_b.button("➕ عميل جديد", use_container_width=True):
        add_client_modal_dialog(conn)

    st.divider()

    # تفاصيل المنتج والمالية
    r1_c1, r1_c2, r1_c3 = st.columns([2, 1, 1])
    p_name = r1_c1.text_input("وصف المنتج/المشروع")
    cat = r1_c2.selectbox("القسم", ["حروف مضيئة", "مطبوعات", "أكريليك", "استكرات"])
    mat = r1_c3.text_input("الخامة")

    r2_c1, r2_c2, r2_c3, r2_c4 = st.columns(4)
    qty = r2_c1.number_input("الكمية", min_value=1.0, value=1.0)
    u_price = r2_c2.number_input("سعر الوحدة", min_value=0.0)
    
    total = (qty * u_price) * 1.15 # حساب الضريبة تلقائياً
    paid = r2_c3.number_input("المبلغ المدفوع", min_value=0.0)
    rem = total - paid
    
    r2_c4.metric("المتبقي للتحصيل", f"{rem:,.2f} ر.س", delta_color="inverse")

    st.warning(f"💰 الإجمالي النهائي (ضريبة 15%): {total:,.2f} ر.س")
    notes = st.text_area("📝 ملاحظات فنية للمصنع:")

    if st.button("💾 تعميد الطلب وحفظ البيانات", type="primary", use_container_width=True):
        if selected_client != "-- اختر عميل --" and p_name:
            # توليد رقم متسلسل فريد NSQ-السنة-رقم عشوائي
            sn = f"NSQ-{datetime.now().strftime('%y%m%d%H%M')}"
            try:
                cursor.execute("""
                    INSERT INTO orders (work_order_sn, client_name, phone, project_name, category, material_type, qty, unit_price, total_price, paid_amount, remaining_amount, details)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (sn, selected_client, clients_dict[selected_client], p_name, cat, mat, qty, u_price, total, paid, rem, notes))
                conn.commit()
                st.success(f"تم الحفظ بنجاح! رقم الطلب: {sn}")
                st.balloons()
            except Exception as e:
                st.error(f"خطأ في الحفظ: {e}")
        else:
            st.error("الرجاء اختيار عميل وكتابة وصف للمشروع")
