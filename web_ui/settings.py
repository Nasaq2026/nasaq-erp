import streamlit as st
from utils.db_manager import db

def render_settings():
    st.title("⚙️ إعدادات النظام والمؤسسة")
    
    # جلب البيانات الحالية من قاعدة البيانات (جدول settings)
    current_settings = db.execute_query("SELECT * FROM settings LIMIT 1", fetch=True)
    
    if current_settings:
        data = current_settings[0]
        
        with st.form("settings_form"):
            col1, col2 = st.columns(2)
            with col1:
                inst_name = st.text_input("اسم المؤسسة", value=data['inst_name'])
                vat_no = st.text_input("الرقم الضريبي", value=data['vat_no'])
                cr_no = st.text_input("السجل التجاري", value=data['cr_no'])
            with col2:
                address = st.text_area("العنوان الوطني", value=data['address'])
                logo_url = st.text_input("رابط الشعار (URL)", value=data['logo_url'])
            
            st.divider()
            st.subheader("إعدادات الضرائب والأسعار")
            vat_pc = st.number_input("نسبة الضريبة (%)", value=float(data['vat_percent']), step=0.1)
            
            if st.form_submit_button("حفظ التعديلات 💾"):
                update_query = """
                    UPDATE settings SET 
                    inst_name=%s, vat_no=%s, cr_no=%s, address=%s, logo_url=%s, vat_percent=%s
                    WHERE id=%s
                """
                db.execute_query(update_query, (inst_name, vat_no, cr_no, address, logo_url, vat_pc, data['id']))
                st.success("✅ تم تحديث إعدادات المؤسسة بنجاح!")
    else:
        st.warning("⚠️ لم يتم العثور على جدول الإعدادات في قاعدة البيانات.")
