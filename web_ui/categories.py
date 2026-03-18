# web_ui/categories.py
import streamlit as st
import pandas as pd
import json

def render_categories(conn):
    st.markdown("""
        <div style="text-align: right;">
            <h1 style="color: #1e293b;">⚙️ إعدادات الأقسام والخدمات</h1>
            <p style="color: #64748b;">إضافة وتعديل أقسام العمل وربطها بطرق الحساب المختلفة (مربوطة بقاعدة البيانات الحية).</p>
        </div>
    """, unsafe_allow_html=True)

    try:
        conn.rollback()
        cursor = conn.cursor()

        # ==========================================
        # 1. إضافة أو تعديل قسم (Upsert)
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

            # ✅ تحديث الزر للكود الجديد width="stretch"
            submit_btn = st.form_submit_button("💾 حفظ القسم", width="stretch")

            if submit_btn:
                if cat_name.strip():
                    try:
                        json.loads(config_json)
                        query = """
                            INSERT INTO categories (name, calc_method, config_json) 
                            VALUES (%s, %s, %s) 
                            ON CONFLICT (name) DO UPDATE 
                            SET calc_method = EXCLUDED.calc_method, config_json = EXCLUDED.config_json
                        """
                        cursor.execute(query, (cat_name.strip(), calc_method, config_json.strip()))
                        conn.commit()
                        st.success(f"✅ تم حفظ القسم '{cat_name}' بنجاح!")
                        st.rerun()
                    except json.JSONDecodeError:
                        st.error("❌ خطأ: تنسيق JSON غير صحيح. تأكد من الأقواس وعلامات التنصيص.")
                else:
                    st.warning("⚠️ يرجى إدخال اسم القسم أولاً.")

        st.divider()

        # ==========================================
        # 2. عرض الأقسام والحذف
        # ==========================================
        st.markdown("### 📁 الأقسام المسجلة في النظام")
        
        df = pd.read_sql("""
            SELECT 
                id AS "الرقم", 
                name AS "اسم القسم", 
                calc_method AS "طريقة الحساب", 
                config_json AS "الخصائص (JSON)" 
            FROM categories 
            ORDER BY id DESC
        """, conn)
        
        if not df.empty:
            # ✅ تحديث الجدول للكود الجديد width="stretch"
            st.dataframe(df, width="stretch", hide_index=True)
            
            st.markdown("### 🗑️ حذف قسم موجود")
            del_col1, del_col2 = st.columns([3, 1])
            with del_col1:
                cat_options = df["اسم القسم"].tolist()
                cat_to_delete = st.selectbox("اختر القسم المراد حذفه:", cat_options)
            with del_col2:
                st.markdown("<br>", unsafe_allow_html=True)
                # ✅ تحديث زر الحذف للكود الجديد width="stretch"
                if st.button("🗑️ تأكيد الحذف", width="stretch"):
                    cursor.execute("DELETE FROM categories WHERE name = %s", (cat_to_delete,))
                    conn.commit()
                    st.success(f"✅ تم حذف القسم '{cat_to_delete}' نهائياً!")
                    st.rerun()
        else:
            st.info("📭 لا توجد أقسام مسجلة في قاعدة البيانات حتى الآن.")

    except Exception as e:
        st.error(f"❌ حدث خطأ أثناء إدارة الأقسام: {e}")
