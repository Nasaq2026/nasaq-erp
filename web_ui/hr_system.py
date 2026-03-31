import streamlit as st  # <-- السطر الأهم، هذا هو سبب المشكلة في الصورة
import pandas as pd     # نحتاجه غالباً

def render_hr(conn):
    # تنسيق الواجهة بأيقونات وحركة
    st.markdown("""
        <div style="text-align: right; margin-bottom: 20px;">
            <h1 style="color: #1e293b;">🪪 الموارد البشرية وشؤون الموظفين (HR)</h1>
            <p style="color: #64748b;">إدارة الرواتب، المكافآت، ورسائل الشكر الداخلية.</p>
        </div>
    """, unsafe_allow_html=True)

    # محرك الأتمتة (الأعمدة التفاعلية بدلاً من القوائم)
    col_msg, col_sal = st.columns([1, 1])

    with col_msg:
        st.subheader("✉️ إرسال شكر وتقدير")
        emp = st.selectbox("اختر الموظف (لإرسال الرسالة):", ["أحمد (مصمم)", "محمد (فني)"])
        template = st.selectbox("نموذج الرسالة:", ["إنجاز سريع", "إبداع في التصميم", "تفاني في التركيب"])
        
        if st.button("إرسال للموظف", use_container_width=True):
            # دالة إرسال شكر ذكية (يمكن دمجها بالواتساب لاحقاً)
            st.success(f"✅ تم إرسال رسالة التقدير إلى {emp} بنجاح! 🎉")

    with col_sal:
        st.subheader("💵 مسير الرواتب المطور")
        
        # إنشاء دالة حساب الرواتب التلقائية
        data = {
            "الموظف": ["أحمد (مصمم)", "محمد (فني)"],
            "الراتب الأساسي": [5000, 4500],
            "الإضافي/البونص": [200, 0],
            "السلف/الخصومات": [0, 100]
        }
        df_base = pd.DataFrame(data)
        
        # دالة حساب حقيقية: صافي المستحق = (الأساسي + الإضافي - الخصومات)
        df_base['صافي المستحق'] = df_base['الراتب الأساسي'] + df_base['الإضافي/البونص'] - df_base['السلف/الخصومات']
        
        # عرض الجدول بشكل احترافي
        st.dataframe(df_base, use_container_width=True)

    st.divider()

    # محرك التطوير المهني (Growth Plan)
    st.subheader("💡 خطة التطوير المهني لفريق موديول")
    st.markdown("- **أحمد (مصمم):** تطوير مهارات Blender ثلاثية الأبعاد.")
    st.markdown("- **محمد (فني):** التدرب على ماكينة ليزر جديدة.")
