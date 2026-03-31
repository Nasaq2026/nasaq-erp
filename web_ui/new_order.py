import streamlit as st
import pandas as pd
from datetime import datetime
# استيراد الديالوج من الملف المنفصل
try:
    from utils.add_client_modal import add_client_modal_dialog
except ImportError:
    def add_client_modal_dialog(conn): st.error("ملف add_client_modal غير موجود في مجلد utils")

# ==========================================
# 📦 أولاً: قاعدة بيانات الخامات (قائمة مسبقة)
# ==========================================
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
# 🛠️ ثانياً: واجهة تسجيل الطلب (نظام نَسق)
# ==========================================
def render_new_order(conn):
    st.markdown("""
        <style>
        .step-container { background-color: #f8fafc; padding: 15px; border-radius: 10px; border-right: 5px solid #fb923c; margin-bottom: 20px; }
        .price-box { background-color: #1e293b; color: #fb923c; padding: 20px; border-radius: 12px; text-align: center; }
        </style>
    """, unsafe_allow_html=True)

    # إدارة حالة الصفحات والبيانات
    if 'order_step' not in st.session_state: st.session_state.order_step = 1
    if 'current_order' not in st.session_state: st.session_state.current_order = {}

    # --- واجهة 1: اختيار/إضافة العميل ---
    if st.session_state.order_step == 1:
        st.markdown("<div class='step-container'><h3>👤 المرحلة الأولى: تحديد العميل</h3></div>", unsafe_allow_html=True)
        
        # جلب العملاء المسجلين مسبقاً
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT client_name, phone FROM clients")
            clients_data = cursor.fetchall()
            client_options = {row[0]: row[1] for row in clients_data}
        except:
            client_options = {}

        col_a, col_b = st.columns([3, 1])
        with col_b:
            if st.button("➕ عميل جديد", type="primary", use_container_width=True):
                add_client_modal_dialog(conn)
        
        selected_name = col_a.selectbox("اختر العميل من القاعدة:", ["-- اختر من القائمة --"] + list(client_options.keys()))
        
        c1, c2 = st.columns(2)
        # تعبئة الجوال تلقائياً عند اختيار الاسم
        phone_val = client_options.get(selected_name, "") if selected_name != "-- اختر من القائمة --" else ""
        confirm_phone = c1.text_input("رقم الجوال للتأكيد:", value=phone_val)
        project_ref = c2.text_input("اسم المشروع / الإشارة (مثلاً: لوحة المحل):")

        if st.button("التالي: اختيار القسم ➡️", width='stretch'):
            if selected_name != "-- اختر من القائمة --":
                st.session_state.current_order.update({
                    "name": selected_name, 
                    "phone": confirm_phone,
                    "project_name": project_ref
                })
                st.session_state.order_step = 2
                st.rerun()
            else: st.warning("⚠️ يرجى اختيار عميل أو إضافة عميل جديد للمتابعة.")

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
        
        if st.button("⬅️ رجوع لتعديل بيانات العميل"): st.session_state.order_step = 1; st.rerun()

    # --- واجهة 3: تفاصيل الخامة والحساب الفني ---
    elif st.session_state.order_step == 3:
        cat = st.session_state.current_order["category"]
        st.markdown(f"<div class='step-container'><h3>🛠️ المرحلة الثالثة: تفاصيل ({cat})</h3></div>", unsafe_allow_html=True)
        
        materials = MATERIALS_DB[cat]
        selected_mat = st.selectbox("اختار الخامة المسجلة مسبقاً:", list(materials.keys()))
        
        base_price = materials[selected_mat]["price"]
        unit = materials[selected_mat]["unit"]
        
        st.info(f"📍 السعر المعتمد في نَسق: {base_price} ر.س لكل {unit}")
        
        c1, c2 = st.columns(2)
        qty = c1.number_input(f"الكمية ({unit}):", min_value=0.1, value=1.0)
        final_unit_price = c2.number_input("سعر الوحدة (تعديل يدوي):", value=float(base_price))

        # الحسابات الضريبية (15%)
        subtotal = qty * final_unit_price
        vat = subtotal * 0.15
        total = subtotal + vat

        st.markdown(f"""
            <div class="price-box">
                <small style="color: white;">المجموع قبل الضريبة: {subtotal:,.2f} ر.س</small>
                <h2 style="margin: 10px 0;">الإجمالي: {total:,.2f} ر.س</h2>
                <small style="color: white;">شامل ضريبة القيمة المضافة (15%): {vat:,.2f} ر.س</small>
            </div>
        """, unsafe_allow_html=True)

        notes = st.text_area("وصف العمل / مقاسات / ملاحظات فنية:")

        if st.button("✅ تعميد الطلب وإرساله للتنفيذ", width='stretch'):
            try:
                cursor = conn.cursor()
                # تجهيز البيانات
                order_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                project_name = st.session_state.current_order.get("project_name") or selected_mat
                
                # إدخال الطلب في قاعدة البيانات (SQL)
                query = """
                    INSERT INTO orders 
                    (client_name, service_type, total_price, status, created_at, project_name) 
                    VALUES (%s, %s, %s, %s, %s, %s)
                """
                # الحالة تبدأ بـ "التصميم" كأول مرحلة في ورشة نَسق
                values = (st.session_state.current_order["name"], cat, total, "التصميم", order_date, project_name)
                
                cursor.execute(query, values)
                conn.commit()
                
                st.balloons()
                st.success(f"تم تعميد طلب العميل {st.session_state.current_order['name']} بنجاح! تم تحويله لقسم التصميم.")
                
                # تصفير الجلسة للطلب القادم
                st.session_state.order_step = 1
                st.session_state.current_order = {}
                st.rerun()
                
            except Exception as e:
                st.error(f"❌ خطأ فني أثناء الحفظ: {e}")

        if st.button("⬅️ رجوع لاختيار قسم آخر"): st.session_state.order_step = 2; st.rerun()
