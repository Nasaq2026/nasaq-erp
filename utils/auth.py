import hashlib
import streamlit as st
from utils.db_manager import db

class AuthManager:
    def __init__(self):
        # ملح أمني (Salt) لزيادة قوة التشفير
        self.salt = "Nasaq_Moudesign_2026_Secret"

    def hash_password(self, password):
        """تشفير كلمة المرور باستخدام SHA-256 مع الـ Salt"""
        if not password:
            return ""
        salted_password = str(password).strip() + self.salt
        return hashlib.sha256(salted_password.encode()).hexdigest()

    def verify_login(self, username, password):
        """التحقق النهائي والمتسامح مع المسافات وحالة الأحرف"""
        try:
            # تنظيف المدخلات
            u_name = str(username).strip()
            u_pass = str(password).strip()

            # البحث باستخدام LOWER لضمان عدم الحساسية لحالة الأحرف (Admin أو admin)
            query = "SELECT emp_name, password, role FROM employees WHERE LOWER(emp_name) = LOWER(%s)"
            result = db.execute_query(query, (u_name,), fetch=True)
            
            if result and len(result) > 0:
                user = result[0]
                stored_password = str(user['password']).strip()
                
                # التحقق المزدوج
                if u_pass == stored_password or self.hash_password(u_pass) == stored_password:
                    return {
                        'emp_name': user['emp_name'],
                        'role': user['role']
                    }
            else:
                # إذا لم يجد المستخدم، اطبع تنبيه مخفي للمطور (Logs)
                print(f"User {u_name} not found in database.")
                
        except Exception as e:
            st.error(f"⚠️ خطأ تقني في الاتصال: {e}")
        
        return None

    def create_user_session(self, user_data):
        """إنشاء جلسة عمل للمستخدم في Streamlit"""
        st.session_state.authenticated = True
        st.session_state.user_name = user_data['emp_name']
        st.session_state.user_role = user_data['role']

    def logout(self):
        """تسجيل الخروج ومسح الجلسة"""
        st.session_state.authenticated = False
        st.session_state.user_name = None
        st.session_state.user_role = None
        st.rerun()

# نسخة جاهزة للاستخدام
auth = AuthManager()
