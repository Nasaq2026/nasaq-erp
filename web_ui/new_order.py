import streamlit as st
import pandas as pd
from datetime import datetime

# ==========================================
# 📦 أولاً: قاعدة بيانات الخامات (مسجلة مسبقاً)
# ==========================================
# ملاحظة: في المستقبل سننقل هذه للـ Database لتعدلها من صفحة الإعدادات
MATERIALS_DB = {
    "حروف مضيئة": {
        "ستيل رينبو (إضاءة خلفية)": {"price": 650, "unit": "متر طولي"},
        "أكريليك كوري (3 ملم)": {"price": 450, "unit": "متر طولي"},
        "زنكور بخ فرن": {"price": 380, "unit": "متر طولي"},
        "حروف ليد نيون": {"price": 500, "unit": "متر طولي"}
    },
    "استكرات وبنرات": {
        "استكر ألماني (Mactac)": {"price": 45, "unit": "متر مربع"},
        "بنر 13 أونص (High Quality)": {"price": 28, "unit": "متر مربع"},
        "رول اب (85x200 سم)": {"price": 140, "unit": "حبة"},
        "استكر شفاف مع قص": {"price": 60, "unit": "متر مربع"}
    },
    "أكريليك وفوركس": {
        "لوح أكريليك (3 ملم)": {"price": 190, "unit": "لوح 122x244"},
        "فوركس (5 ملم)": {"price": 110, "unit": "لوح 122x244"},
        "قص ليزر أكريليك (ساعة)": {"price": 150, "unit": "ساعة تشغيل"}
    },
    "مطبوعات ورقية": {
        "كروت شخصية (1000 كرت)": {"price": 120, "unit": "بوكس"},
        "بروشور A4 (وجهين)": {"price": 0.85, "unit": "نسخة"},
        "فولدرات جاكيت": {"price": 4.5, "unit": "نسخة"}
    }
}

# ==========================================
# 🛠️ ثانياً: واجهة تسجيل الطلب (الويزارد الذكي)
# ==========================================
def render_new_order(conn):
    st.markdown("""
        <style>
        .step-container { background-color: #f8fafc; padding: 15px; border-radius: 10px; border-right: 5px solid #fb923c; margin-bottom: 20px; }
        .price-box { background-color: #1e293b; color: #fb923c; padding: 20px; border-radius: 12px; text-align: center; }
        </style>
    """, unsafe_allow_html=True)

    # إدارة حالة الصفحات
    if 'order_step' not in st.session_state: st.session_state.order_step = 1
    if 'current_order' not in st.session_state: st.session_state.current_order = {}

    # --- واجهة 1: بيانات العميل ---
    if st.session_state.order_step == 1:
        st.markdown("<div class='step-container'><h3>👤 المرحلة الأولى: بيانات العميل</h3></div>", unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        c_name = c1.text_input("اسم العميل / المؤسسة:")
        c_phone = c2.text_input("رقم الجوال (التعميد والواتساب):", placeholder="05xxxxxxxx")
        
        if st.button("التالي: اختيار القسم ➡️", width='stretch'):
            if c_name and c_phone:
                st.session_state.current_order.update({"name": c_name, "phone": c_phone})
                st.session_state.order_step = 2
                st.rerun()
            else: st.warning("⚠️ يرجى تعبئة بيانات العميل أولاً.")

    # --- واجهة 2: اختيار التخصص الإعلاني ---
    elif st.session_state.order_step == 2:
        st.markdown("<div class='step-container'><h3>📦 المرحلة الثانية: اختر نوع المنتج</h3></div>", unsafe_allow_html=True)
        categories = list(MATERIALS_DB.keys())
        cols = st.columns(2)
        for i, cat in enumerate(categories):
            if cols[i%2].button(cat, width='stretch'):
                st.session_state.current_order["category"] = cat
                st.session_state.order_step = 3
                st.rerun()
        
        if st.button("⬅️ رجوع"): st.session_state.order_step = 1; st.rerun()

    # --- واجهة 3: تفاصيل الخامة والحساب ---
    elif st.session_state.order_step == 3:
        cat = st.session_state.current_order["category"]
        st.markdown(f"<div class='step-container'><h3>🛠️ المرحلة الثالثة: تفاصيل ({cat})</h3></div>", unsafe_allow_html=True)
        
        # القائمة المسبقة للخامات
        materials = MATERIALS_DB[cat]
        selected_mat = st.selectbox("اختار الخامة المسجلة مسبقاً:", list(materials.keys()))
        
        base_price = materials[selected_mat]["price"]
        unit = materials[selected_mat]["unit"]
        
        st.info(f"📍 السعر المعتمد: {base_price} ر.س لكل {unit}")
        
        c1, c2 = st.columns(2)
        qty = c1.number_input(f"الكمية المطلوبة ({unit}):", min_value=0.1, value=1.0)
        final_unit_price = c2.number_input("سعر الوحدة (يمكنك التعديل):", value=float(base_price))

        # الحسابات الضريبية السعودية
        subtotal = qty * final_unit_price
        vat = subtotal * 0.15
        total = subtotal + vat

        st.markdown(f"""
            <div class="price-box">
                <small style="color: white;">المجموع (قبل الضريبة): {subtotal:,.2f} ر.س</small>
                <h2 style="margin: 10px 0;">الإجمالي: {total:,.2f} ر.س</h2>
                <small style="color: white;">شامل ضريبة القيمة المضافة (15%): {vat:,.2f} ر.س</small>
            </div>
        """, unsafe_allow_html=True)

        st.text_area("وصف العمل / ملاحظات فنية:")

        if st.button("✅ تعميد الطلب وإصدار أمر التشغيل", width='stretch'):
            st.balloons()
            st.success("تم تسجيل الطلب بنجاح! سيصل إشعار للمصمم والفني فوراً.")
            # هنا نضيف كود الـ SQL للحفظ
            st.session_state.order_step = 1
            st.rerun()

        if st.button("⬅️ رجوع"): st.session_state.order_step = 2; st.rerun()
