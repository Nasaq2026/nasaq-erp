import streamlit as st

@st.dialog("👤 تسجيل عميل جديد - نَسق")
def add_client_modal_dialog(conn):
    st.markdown("""
        <style>
        div[data-testid="stDialogContent"] { border-top: 10px solid #fb923c; border-radius: 20px; direction: rtl; }
        .field-label { font-weight: bold; color: #1e293b; margin-bottom: 5px; display: block; }
        </style>
    """, unsafe_allow_html=True)

    with st.form("professional_client_form", clear_on_submit=True):
        st.subheader("📋 البيانات الأساسية")
        c1, c2 = st.columns(2)
        name = c1.text_input("اسم العميل / المؤسسة *")
        phone = c2.text_input("رقم الجوال *")

        st.divider()
        st.subheader("📑 البيانات القانونية والضريبية")
        c3, c4 = st.columns(2)
        vat_number = c3.text_input("الرقم الضريبي (15 خانة)")
        cr_number = c4.text_input("رقم السجل التجاري")
        
        st.subheader("📍 الموقع والعنوان الوطني")
        national_address = st.text_area("العنوان الوطني (مثلاً: 1234 الرياض - حي الملقا - 7890)")

        submit = st.form_submit_button("حفظ بيانات العميل ✅", width='stretch', type="primary")

        if submit:
            if name and phone:
                try:
                    cursor = conn.cursor()
                    query = """
                        INSERT INTO clients (client_name, phone, vat_number, cr_number, address) 
                        VALUES (%s, %s, %s, %s, %s)
                    """
                    cursor.execute(query, (name, phone, vat_number, cr_number, national_address))
                    conn.commit()
                    st.success("تم الحفظ! سيظهر العميل الآن في القائمة المنسدلة.")
                    st.rerun()
                except Exception as e:
                    st.error(f"خطأ: {e}")
            else:
                st.warning("يرجى إدخال الاسم والجوال")
