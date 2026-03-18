# web_ui/calculator.py
import streamlit as st

def render_calculator(conn):
    st.markdown("""
        <div style="text-align: right;">
            <h1 style="color: #1e293b;">🧮 حاسبات الإنتاج والتسعير</h1>
            <p style="color: #64748b;">أدوات ذكية لحساب تسعير المطبوعات وتقليل هدر الخامات في الورشة.</p>
        </div>
    """, unsafe_allow_html=True)

    # 🌑 استخدام التبويبات بشكل عصري
    tab1, tab2 = st.tabs(["💰 تسعير اللوحات (بالمتر)", "📏 حاسبة الهدر (الاستيكرات)"])
    
    # ==========================================
    # التبويب الأول: حاسبة التسعير
    # ==========================================
    with tab1:
        st.markdown("### 💰 حاسبة تسعير الطباعة (بالمساحة)")
        with st.container():
            col1, col2, col3 = st.columns(3)
            width = col1.number_input("العرض (بالمتر)", min_value=0.0, value=1.0, step=0.1, key="calc_w")
            height = col2.number_input("الطول (بالمتر)", min_value=0.0, value=1.0, step=0.1, key="calc_h")
            qty = col3.number_input("الكمية", min_value=1, value=1, step=1, key="calc_qty")
            
            price_per_meter = st.number_input("سعر المتر المربع (ر.س)", min_value=0.0, value=50.0, step=5.0)
            
            # العمليات الحسابية
            area = width * height
            total_area = area * qty
            total_price = total_area * price_per_meter
            vat = total_price * 0.15
            final_total = total_price + vat
            
            st.divider()
            
            # عرض النتائج بشكل كروت Metric واضحة
            res_c1, res_c2, res_c3 = st.columns(3)
            res_c1.metric("📏 المساحة الإجمالية", f"{total_area:.2f} م²")
            res_c2.metric("💰 قبل الضريبة", f"{total_price:.2f} ر.س")
            res_c3.metric("🧾 الضريبة (15%)", f"{vat:.2f} ر.س")
            
            st.success(f"🔥 الإجمالي المطلوب من العميل: **{final_total:,.2f} ر.س**")

    # ==========================================
    # التبويب الثاني: حاسبة الهدر (الإنتاج الفني)
    # ==========================================
    with tab2:
        st.markdown("### 📏 حاسبة هدر الاستيكرات (للمتر المربع 100x100 سم)")
        st.info("💡 احسب عدد الحبات الممكن استخراجها من المتر الواحد لتقليل فواقد الخامة.")
        
        with st.form("waste_calculator_form"):
            col_w, col_h = st.columns(2)
            with col_w:
                w_cm = st.number_input("عرض الحبة (سم)", min_value=0.1, value=5.0, step=1.0)
            with col_h:
                h_cm = st.number_input("طول الحبة (سم)", min_value=0.1, value=5.0, step=1.0)
                
            # ✅ تحديث الزر للكود الجديد width="stretch"
            calc_btn = st.form_submit_button("⚙️ احسب الإنتاج والهدر", width="stretch")
            
            if calc_btn:
                if w_cm > 100 or h_cm > 100:
                    st.error("❌ خطأ: أبعاد الحبة أكبر من مساحة المتر المربع (100x100 سم)!")
                else:
                    # خوارزمية الحساب
                    res_w = int(100 / w_cm)
                    res_h = int(100 / h_cm)
                    total_pieces = res_w * res_h
                    
                    used_area = total_pieces * (w_cm * h_cm)
                    waste_pct = 100 - (used_area / 10000) * 100
                    
                    st.divider()
                    
                    col_res1, col_res2 = st.columns(2)
                    col_res1.metric("📦 الإنتاج الصافي للمتر", f"{total_pieces} حبة")
                    
                    # تلوين ذكي لنسبة الهدر
                    if waste_pct < 15:
                        col_res2.metric("🗑️ نسبة الهدر", f"{waste_pct:.1f}%", delta="ممتاز", delta_color="normal")
                    elif waste_pct < 30:
                        col_res2.metric("⚠️ نسبة الهدر", f"{waste_pct:.1f}%", delta="مقبول", delta_color="off")
                    else:
                        col_res2.metric("🚨 نسبة الهدر", f"{waste_pct:.1f}%", delta="مرتفع جداً!", delta_color="inverse")
                    
                    if waste_pct > 30:
                        st.warning("💡 **نصيحة للإدارة:** نسبة الهدر عالية! حاول تغيير ترتيب الحبات أو الطباعة على رولات بمقاسات مختلفة لتوفير التكاليف.")
