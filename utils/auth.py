import hashlib
import streamlit as st
from utils.db_manager import db

class AuthManager:
    def __init__(self):
        # ملح أمني (Salt) لزيادة قوة التشفير - يمكنك تغييره ليكون خاصاً بك
        self.salt = "Nasaq_Moudesign_2026_Secret"

    def hash_password(self, password):
        """تشفير كلمة المرور باستخدام SHA-256 مع الـ Salt"""
        salted_password = password + self.salt
        return hashlib.sha256(salted_password.encode()).hexdigest()

    def verify_login(self, username, password):
        """التحقق من صحة بيانات الدخول"""
        hashed_pw = self.hash_password(password)
        
        query = "SELECT emp_name, role FROM employees WHERE emp_name = %s AND password = %s"
        result = db.execute_query(query, (username, hashed_pw), fetch=True)
        
        if result and len(result) > 0:
            return result[0]  # يعيد اسم الموظف ودوره (Admin, Designer, etc.)
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
