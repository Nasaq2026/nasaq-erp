import streamlit as st  # السطر الذي يحل مشكلة name 'st' is not defined
import pandas as pd

def render_supply_chain(conn):
    st.markdown("""
        <div style="text-align: right; margin-bottom: 20px;">
            <h1 style="color: #3b82f6;">🚚 إدارة الموردين والورش الخارجية</h1>
            <p style="color: #64748b;">متابعة مخزون الاكريليك، الكلادينج، وتوريدات المصانع.</p>
        </div>
    """, unsafe_allow_html=True)

    # 1. إحصائيات الموردين (KPIs)
    col1, col2, col3 = st.columns(3)
    col1.metric("عدد الموردين", "12")
    col2.metric("طلبات شراء نشطة", "5")
    col3.metric("ديون الموردين", "4,200 ر.س", delta="-150", delta_color="normal")

    st.divider()

    # 2. إضافة مورد جديد أو ورشة
    with st.expander("➕ إضافة مورد أو مصنع خارجي جديد"):
        c1, c2 = st.columns(2)
        with c1:
            sup_name = st.text_input("اسم المورد/المصنع")
            sup_type = st.selectbox("التخصص", ["اكريليك وحروف", "كلادينج وهياكل", "مطابع ورقية", "إضاءة وكهرباء"])
        with c2:
            contact = st.text_input("رقم التواصل")
            location = st.text_input("موقع الورشة (رابط)")
        
        if st.button("حفظ المورد في نَسق", use_container_width=True):
            st.success(f"تم تسجيل المورد {sup_name} بنجاح! سيظهر في قائمة التوريد.")

    # 3. جدول الموردين الحاليين
    st.subheader("📋 قائمة الموردين والتعاملات")
    
    # بيانات تجريبية (يتم ربطها بجدول suppliers في قاعدة البيانات لاحقاً)
    suppliers_data = {
        "المورد": ["مصنع الخليج للاكريليك", "ورشة الوفاء للحديد", "مطبعة التميز"],
        "الحالة": ["نشط", "متوقف", "نشط"],
        "الرصيد (ر.س)": [1200, 0, 550],
        "آخر توريد": ["2026-03-25", "2026-02-10", "2026-03-30"]
    }
    df_sup = pd.DataFrame(suppliers_data)
    
    # عرض الجدول بتنسيق موديول
    st.dataframe(df_sup, use_container_width=True, hide_index=True)

    # 4. قسم "أمر توريد سريع"
    st.divider()
    st.subheader("📦 إصدار أمر توريد (LPO)")
    selected_sup = st.selectbox("اختر المورد لإرسال الطلب", df_sup["المورد"])
    order_details = st.text_area("تفاصيل المواد المطلوبة (مثلاً: 5 ألواح اكريليك 3 ملم أسود)")
    
    if st.button("إرسال طلب التوريد واتساب"):
        msg = f"تحية طيبة من مؤسسة موديول.. نود طلب الآتي: {order_details}"
        # هنا سنضع رابط واتساب المورد لاحقاً
        st.info(f"جاري تجهيز الرسالة لـ {selected_sup}...")
