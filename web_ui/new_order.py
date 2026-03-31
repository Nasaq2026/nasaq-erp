import streamlit as st
from datetime import datetime
from utils.add_client_modal import add_client_modal_dialog

def render_new_order(conn):
    # تنسيق CSS مخصص ليشبه أنظمة ERP العالمية
    st.markdown("""
        <style>
        .main-card { background: white; padding: 25px; border-radius: 15px; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1); border: 1px solid #e2e8f0; }
        .section-header { color: #1e293b; border-bottom: 2px solid #fb923c; padding-bottom: 10px; margin-bottom: 20px; font-weight: bold; }
        .price-summary { background: #f8fafc; border-radius: 12px; padding: 20px; border: 1px dashed #cbd5e1; }
        </style>
    """, unsafe_allow_html=True)

    st.markdown("<div class='section-header'>🚀 إنشاء أمر تشغيل / فاتورة جديدة</div>", unsafe_allow_html=True)

    with st.container():
        # --- الجزء الأول: رأس الفاتورة (العميل) ---
        col_client, col_btn = st.columns([4, 1])
        
        # جلب قائمة العملاء
        cursor = conn.cursor()
        cursor.execute("SELECT client_name FROM clients ORDER BY id DESC")
        clients = [row[0] for row in cursor.fetchall()]

        with col_client:
            selected_client = st.selectbox("👤 اختر العميل (أو ابحث بالاسم):", ["-- اختر عميل --"] + clients)
        with col_btn:
            st.write("") # موازنة المسافة
            if st.button("➕ عميل جديد", type="primary", use_container_width=True):
                add_client_modal_dialog(conn)

        st.divider()

        # --- الجزء الثاني: تفاصيل المشروع (الصفوف) ---
        st.markdown("**🛠️ تفاصيل المواد والخدمات**")
        
        # تصميم يشبه نظام الصفوف في الصور
        r1_c1, r1_c2, r1_c3 = st.columns([2, 1, 1])
        project_name = r1_c1.text_input("وصف المنتج / الخدمة", placeholder="مثلاً: لوحة حروف باردة - فرع جيزان")
        category = r1_c2.selectbox("القسم", ["حروف مضيئة", "مطبوعات", "أكريليك", "استكرات"])
        material = r1_c3.text_input("الخامة المستخدمة")

        r2_c1, r2_c2, r2_c3 = st.columns(3)
        qty = r2_c1.number_input("الكمية", min_value=1.0, value=1.0)
        unit_price = r2_c2.number_input("سعر الوحدة (ريال)", min_value=0.0, value=0.0)
        
        # الحسابات التلقائية
        subtotal = qty * unit_price
        tax = subtotal * 0.15
        total = subtotal + tax

        # --- الجزء الثالث: ملخص الحساب (Price Box) ---
        st.markdown("<div class='price-summary'>", unsafe_allow_html=True)
        m1, m2, m3 = st.columns(3)
        m1.metric("المجموع الفرعي", f"{subtotal:,.2f} ر.س")
        m2.metric("ضريبة (15%)", f"{tax:,.2f} ر.س")
        m3.subheader(f"الإجمالي: {total:,.2f} ر.س")
        st.markdown("</div>", unsafe_allow_html=True)

        st.divider()
        
        # --- الجزء الرابع: الملاحظات والتعميد ---
        notes = st.text_area("📝 ملاحظات فنية للمصمم والفني (المقاسات، الألوان، طريقة التركيب):")
        
        if st.button("💾 حفظ الطلب وإصدار أمر التشغيل", type="primary", use_container_width=True):
            if selected_client != "-- اختر عميل --" and project_name:
                # كود الحفظ في الداتابيز
                cursor.execute("""
                    INSERT INTO orders (client_name, project_name, service_type, total_price, status, created_at)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, (selected_client, project_name, category, total, 'التصميم', datetime.now()))
                conn.commit()
                st.balloons()
                st.success(f"تم تعميد الطلب للعميل {selected_client} بنجاح!")
            else:
                st.error("يرجى اختيار عميل وكتابة وصف للمنتج")
