# nasaq-erp/utils/add_client_modal.py

import streamlit as st

# ==========================================
# 🎨 1. تنسيق هوية "نَسق" البصرية (CSS المنبثقة)
# ==========================================
MODAL_STYLE = """
<style>
/* تنسيق الديالوج ليصبح كـ Card احترافية */
div[data-testid="stDialog"] div[data-testid="stDialogContent"] {
    background-color: #ffffff;
    border-radius: 20px;
    padding: 30px;
    box-shadow: 0 20px 25px -5px rgba(0,0,0,0.1), 0 10px 10px -5px rgba(0,0,0,0.04);
    border-right: 12px solid #fb923c; /* خط نَسق البرتقالي المميز */
}

/* تنسيق العناوين داخل المنبثقة */
div[data-testid="stDialogContent"] h2 { color: #1e293b; font-family: 'Cairo', sans-serif; text-align: right; margin-bottom: 25px; }
div[data-testid="stDialogContent"] small { color: #64748b; text-align: right; display: block; }

/* تنسيق زر الحفظ الاحترافي */
div[data-testid="stDialogContent"] button[kind="primary"] {
    background-color: #fb923c !important; /* برتقالي نَسق */
    color: white !important;
    border-radius: 10px !important;
    height: 3em !important;
    border: none !important;
    font-weight: bold !important;
}
div[data-testid="stDialogContent"] button[kind="secondary"] {
    border-radius: 10px !important;
}
</style>
"""

# ==========================================
# 🛠️ 2. تعريف الدالة المنبثقة (The Dialog)
# ==========================================
@st.dialog("👤 إضافة عميل جديد") # العنوان يظهر في صدر الديالوج
def add_client_modal_dialog(conn):
    # تطبيق الستايل الاحترافي لنَسق
    st.markdown(MODAL_STYLE, unsafe_allow_html=True)
    
    st.markdown("<small>يرجى تعبئة بيانات العميل أو المنشأة بعناية لضمان دقة الفواتير والتعميد.</small><br>", unsafe_allow_html=True)
    
    with st.form("add_client_form", clear_on_submit=True):
        # القسم الأول: البيانات الشخصية
        c1, c2 = st.columns(2)
        name = c1.text_input("اسم العميل / المؤسسة *", placeholder="مثال: مؤسسة نَسق للدعاية")
        last_name = c2.text_input("اللقب / العائلة (اختياري)")
        
        # القسم الثاني: بيانات التواصل والشركة
        c3, c4 = st.columns(2)
        phone = c3.text_input("رقم الجوال (السعودية) *", placeholder="05xxxxxxxx")
        email = c4.text_input("البريد الإلكتروني", placeholder="client@domain.com")
        
        company = st.text_input("اسم الشركة / المنشأة")
        
        # القسم الثالث: تفاصيل إضافية
        address = st.text_area("العنوان بالتفصيل (لشحنات البنرات/اللوحات)")
        
        reference = st.text_input("مرجع / ملاحظة إضافية")

        st.markdown("---")
        
        # الأزرار في الأسفل
        submit = st.form_submit_button("حفظ العميل ✅", width='stretch', type="primary")

        # منطق الحفظ والتأكيد
        if submit:
            if name and phone:
                try:
                    cursor = conn.cursor()
                    query = """
                        INSERT INTO clients (client_name, phone, email, address, company, reference) 
                        VALUES (%s, %s, %s, %s, %s, %s)
                    """
                    full_name = f"{name} {last_name}".strip()
                    cursor.execute(query, (full_name, phone, email, address, company, reference))
                    conn.commit()
                    st.balloons()
                    st.success(f"تم تسجيل العميل {full_name} بنجاح! 🎉")
                    st.rerun() # لإغلاق المنبثقة وتحديث الصفحة الرئيسية
                except Exception as e:
                    st.error(f"❌ حدث خطأ أثناء الحفظ في قاعدة البيانات: {e}")
            else:
                st.warning("⚠️ يرجى تعبئة الحقول الأساسية (الاسم ورقم الجوال)")
