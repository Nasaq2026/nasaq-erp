import streamlit as st
import pandas as pd

def render_settings(conn):
    st.markdown("""
        <div style="text-align: right;">
            <h1 style="color: #1e293b;">⚙️ إعدادات النظام والخامات</h1>
            <p style="color: #64748b;">تحديث قوائم الأسعار، أنواع الخامات، ومعايير الضريبة السعودية.</p>
        </div>
    """, unsafe_allow_html=True)

    tabs = st.tabs(["🏗️ إدارة الخامات", "🏢 بيانات المؤسسة", "🔐 المستخدمين"])

    # --- التبويب الأول: إدارة الخامات ---
    with tabs[0]:
        st.subheader("إضافة خامة / منتج جديد")
        
        with st.form("add_material_form"):
            c1, c2, c3 = st.columns(3)
            cat = c1.selectbox("القسم:", ["حروف مضيئة", "استكرات وبنرات", "أكريليك وفوركس", "مطبوعات ورقية", "هدايا ودروع"])
            m_name = c2.text_input("اسم الخامة (مثلاً: أكريليك 3 ملم كوري):")
            m_unit = c3.selectbox("وحدة القياس:", ["متر طولي", "متر مربع", "حبة", "لوح", "ساعة قص"])
            
            c4, c5 = st.columns(2)
            m_price = c4.number_input("السعر الافتراضي (ريال سعودي):", min_value=0.0)
            submit = st.form_submit_button("إضافة الخامة للقائمة المسبقة ✅", width='stretch')

            if submit:
                if m_name:
                    try:
                        cursor = conn.cursor()
                        # تأكد من وجود جدول اسمه materials في قاعدة بياناتك
                        cursor.execute("""
                            INSERT INTO materials (category, material_name, unit, price) 
                            VALUES (%s, %s, %s, %s)
                        """, (cat, m_name, m_unit, m_price))
                        conn.commit()
                        st.success(f"تم إضافة {m_name} بنجاح!")
                    except Exception as e:
                        st.error(f"خطأ في الحفظ: {e}")
                else:
                    st.warning("يرجى إدخال اسم الخامة.")

        st.divider()
        st.subheader("📋 قائمة الخامات الحالية")
        try:
            df_materials = pd.read_sql("SELECT * FROM materials", conn)
            st.dataframe(df_materials, width='stretch', hide_index=True)
        except:
            st.info("لا توجد خامات مسجلة في قاعدة البيانات بعد.")

    # --- التبويب الثاني: بيانات المؤسسة ---
    with tabs[1]:
        st.info("هنا يمكنك تعديل رقم السجل التجاري، الرقم الضريبي، وشعار نَسق الذي يظهر في الفواتير.")
        st.text_input("الرقم الضريبي (VAT Number):", value="300XXXXXXXXXXXX")
        st.button("حفظ الإعدادات الضريبية")
