# nasaq-erp/utils/add_client_modal.py

import streamlit as st

# دالة النافذة المنبثقة (Dialog) لإضافة عميل
@st.dialog("👤 إضافة عميل جديد لنَسق")
def add_client_modal_dialog(conn):
    st.markdown("""
        <style>
        /* ستايل خاص بالديالوج ليتناسب مع هوية نَسق */
        div[data-testid="stDialogContent"] {
            border-right: 12px solid #fb923c !important;
            border-radius: 15px !important;
            direction: rtl !important;
        }
        div[data-testid="stDialogContent"] h2 { text-align: right !important; }
        </style>
    """, unsafe_allow_html=True)
    
    st.write("قم بتعبئة بيانات العميل الجديد ليتم إضافته لقاعدة البيانات فوراً.")
    
    # استخدام st.container لضمان ترتيب العناصر داخل المنبثقة
    with st.form("quick_add_client", clear_on_submit=True):
        c1, c2 = st.columns(2)
        with c1:
            name = st.text_input("اسم العميل / المؤسسة *")
        with c2:
            phone = st.text_input("رقم الجوال *", placeholder="05xxxxxxxx")
        
        email = st.text_input("البريد الإلكتروني (اختياري)")
        address = st.text_area("العنوان / مدينة العميل")
        
        st.markdown("---")
        # زر الحفظ بلون نَسق البرتقالي
        submit = st.form_submit_button("حفظ العميل في القاعدة ✅", width='stretch')

        if submit:
            if name and phone:
                try:
                    cursor = conn.cursor()
                    # استعلام الإدخال (تأكد أن أسماء الأعمدة تطابق جدول clients عندك)
                    query = "INSERT INTO clients (client_name, phone, email, address) VALUES (%s, %s, %s, %s)"
                    cursor.execute(query, (name, phone, email, address))
                    conn.commit()
                    
                    st.success(f"✅ تم إضافة العميل {name} بنجاح!")
                    st.rerun() # تحديث الصفحة لإظهار العميل الجديد في القائمة المنسدلة
                except Exception as e:
                    st.error(f"❌ خطأ في قاعدة البيانات: {e}")
            else:
                st.warning("⚠️ يرجى إدخال الاسم ورقم الجوال على الأقل.")
