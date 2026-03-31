import psycopg2
from psycopg2.extras import RealDictCursor
import streamlit as st

class DatabaseManager:
    def __init__(self):
        # جلب بيانات الاتصال من Secrets الخاصة بـ Streamlit
        self.db_url = st.secrets["postgres_url"]

    def get_connection(self):
        """إنشاء اتصال آمن بقاعدة البيانات"""
        try:
            conn = psycopg2.connect(self.db_url)
            return conn
        except Exception as e:
            st.error(f"❌ خطأ في الاتصال بقاعدة البيانات: {e}")
            return None

    def execute_query(self, query, params=None, fetch=False):
        """تنفيذ استعلام (إدخال، تحديث، حذف، أو جلب بيانات)"""
        conn = self.get_connection()
        if not conn:
            return None
        
        try:
            # استخدام RealDictCursor يجعل النتائج تعود كقاموس {column: value}
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(query, params)
                if fetch:
                    result = cur.fetchall()
                else:
                    conn.commit()
                    result = True
            return result
        except Exception as e:
            st.error(f"⚠️ خطأ أثناء تنفيذ الاستعلام: {e}")
            conn.rollback()
            return None
        finally:
            conn.close()

# تعريف نسخة واحدة ليتم استخدامها في كل البرنامج
db = DatabaseManager()
