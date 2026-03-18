# web_ui/categories.py
import streamlit as st
import pandas as pd
import json

def render_categories(conn):
    st.title("⚙️ إعدادات الأقسام والخدمات")
    st.info("إضافة، تعديل، أو حذف أقسام العمل وربطها بطرق الحساب المختلفة. (مربوطة بقاعدة البيانات الحية)")

    try:
        conn.rollback()
        cursor = conn.cursor()

        # ==========================================
        # القسم الأول: إضافة أو تعديل قسم (Upsert)
        # ==========================================
        st.markdown("### ➕ إضافة أو تعديل قسم")
        with st.form("category_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                cat_name = st.text_input("اسم القسم (مثال: تصميم لوجو)")
                calc_method = st.selectbox("طريقة الحساب", ["بالمتر", "بالحبة", "مخصص"])
                
            with col2:
                default_json = '[\n  ["نوع الخدمة", "combo", ["خيار1", "خيار2"]],\n  ["الكمية", "entry", ""]\n]'
                config_json = st.text_area("إعدادات القسم (بصيغة JSON)", value=default_json, height=130)

            submit_btn = st.form_submit_button("💾 حفظ القسم", use_container_width=True)

            if submit_btn:
                if cat_name.strip():
                    try:
                        # التحقق من صحة كود JSON قبل الإرسال لقاعدة البيانات
                        json.loads(config_json)
                        
                        # نفس استعلام الـ PostgreSQL الذكي (تحديث لو موجود، إضافة لو جديد)
                        query = """
                            INSERT INTO categories (name, calc_method, config_json) 
                            VALUES (%s, %s, %s) 
                            ON CONFLICT (name) DO UPDATE 
                            SET calc_method = EXCLUDED.calc_method, config_json = EXCLUDED.config_json
                        """
                        cursor.execute(query, (cat_name.strip(), calc_method, config_json.strip()))
                        conn.commit()
                        st.success(f"✅ تم حفظ القسم '{cat_name}' بنجاح!")
                        st.rerun() # تحديث الصفحة لإظهار القسم الجديد
                    except json.JSONDecodeError:
                        st.error("❌ خطأ: تنسيق JSON غير صحيح. تأكد من الأقواس وعلامات التنصيص.")
                else:
                    st.warning("⚠️ يرجى إدخال اسم القسم أولاً.")

        st.divider()

        # ==========================================
        # القسم الثاني: عرض الأقسام والحذف
        # ==========================================
        st.markdown("### 📁 الأقسام المسجلة في النظام")
        
        # جلب البيانات من الداتابيز
        df = pd.read_sql("SELECT id AS \"الرقم\", name AS \"اسم القسم\", calc_method AS \"طريقة الحساب\", config_json AS \"الخصائص (JSON)\" FROM categories ORDER BY id DESC", conn)
        
        if not df.empty:
            st.dataframe(df, use_container_width=True, hide_index=True)
            
            # قسم الحذف (بطريقة آمنة للويب)
            st.markdown("### 🗑️ حذف قسم موجود")
            del_col1, del_col2 = st.columns([3, 1])
            with del_col1:
                cat_to_delete = st.selectbox("اختر القسم المراد حذفه:", df["اسم القسم"].tolist())
            with del_col2:
                st.markdown("<br>", unsafe_allow_html=True) # للمحاذاة العمودية مع القائمة
                if st.button("🗑️ تأكيد الحذف", use_container_width=True):
                    cursor.execute("DELETE FROM categories WHERE name = %s", (cat_to_delete,))
                    conn.commit()
                    st.success(f"✅ تم حذف القسم '{cat_to_delete}' نهائياً!")
                    st.rerun()
        else:
            st.info("لا توجد أقسام مسجلة في قاعدة البيانات حتى الآن.")

    except Exception as e:
        st.error(f"حدث خطأ أثناء إدارة الأقسام: {e}")