# web_ui/calculator.py
import streamlit as st

def render_calculator(conn):
    st.title("🧮 حاسبات الإنتاج والتسعير")
    st.info("أدوات سريعة لمساعدة الإدارة في تسعير المطبوعات وحساب الهدر في الخامات.")
    
    # 🔴 استخدام التبويبات (Tabs) لفصل الحاسبتين بشكل منظم وشيك
    tab1, tab2 = st.tabs(["💰 حاسبة تسعير اللوحات (بالمتر)", "📏 حاسبة هدر الاستيكرات (الإنتاج الفني)"])
    
    # ==========================================
    # التبويب الأول: حاسبة التسعير (اللي عملناها المرة اللي فاتت)
    # ==========================================
    with tab1:
        st.markdown("### 💰 حاسبة تسعير الطباعة (بالمساحة)")
        with st.container():
            col1, col2, col3 = st.columns(3)
            width = col1.number_input("العرض (بالمتر)", min_value=0.0, value=1.0, step=0.1, key="calc_w")
            height = col2.number_input("الطول (بالمتر)", min_value=0.0, value=1.0, step=0.1, key="calc_h")
            qty = col3.number_input("الكمية", min_value=1, value=1, step=1, key="calc_qty")
            
            price_per_meter = st.number_input("سعر المتر المربع (ر.س)", min_value=0.0, value=50.0, step=5.0)
            
            area = width * height
            total_area = area * qty
            total_price = total_area * price_per_meter
            vat = total_price * 0.15
            final_total = total_price + vat
            
            st.divider()
            st.markdown(f"#### 📏 المساحة الإجمالية: **{total_area:.2f} متر مربع**")
            st.markdown(f"#### 💰 الإجمالي قبل الضريبة: **{total_price:.2f} ر.س**")
            st.markdown(f"#### 🧾 الضريبة (15%): **{vat:.2f} ر.س**")
            st.success(f"🔥 الإجمالي المطلوب من العميل: {final_total:.2f} ر.س")

    # ==========================================
    # التبويب الثاني: حاسبة الهدر (الكود اللي إنت بعته)
    # ==========================================
    with tab2:
        st.markdown("### 📏 حاسبة هدر الاستيكرات (للمتر المربع 100x100 سم)")
        st.write("تقوم هذه الأداة بحساب عدد الحبات التي يمكن استخراجها من متر مربع واحد ونسبة الهدر (الفراغات) المتبقية.")
        
        with st.form("waste_calculator_form"):
            col_w, col_h = st.columns(2)
            with col_w:
                w_cm = st.number_input("عرض الحبة (سم)", min_value=0.1, value=5.0, step=1.0)
            with col_h:
                h_cm = st.number_input("طول الحبة (سم)", min_value=0.1, value=5.0, step=1.0)
                
            calc_btn = st.form_submit_button("⚙️ احسب الإنتاج والهدر", use_container_width=True)
            
            if calc_btn:
                if w_cm > 100 or h_cm > 100:
                    st.error("❌ خطأ: أبعاد الحبة أكبر من مساحة المتر المربع (100x100 سم)!")
                else:
                    # نفس خوارزمية الحساب اللي إنت كاتبها بالظبط
                    res_w = int(100 / w_cm)
                    res_h = int(100 / h_cm)
                    total_pieces = res_w * res_h
                    
                    used_area = total_pieces * (w_cm * h_cm)
                    waste_pct = 100 - (used_area / 10000) * 100
                    
                    st.divider()
                    
                    # عرض النتائج بشكل بصري جذاب
                    col_res1, col_res2 = st.columns(2)
                    col_res1.metric("📦 الإنتاج الصافي للمتر", f"{total_pieces} حبة")
                    
                    # تغيير لون نسبة الهدر حسب الخطورة (أخضر لو قليل، برتقالي أو أحمر لو عالي)
                    waste_color = "normal" if waste_pct < 15 else ("inverse" if waste_pct < 30 else "off")
                    if waste_color == "normal":
                        col_res2.metric("🗑️ نسبة الهدر (الفراغات)", f"{waste_pct:.1f}%")
                    else:
                        col_res2.metric("⚠️ نسبة الهدر (الفراغات)", f"{waste_pct:.1f}%", delta="مرتفع!", delta_color="inverse")
                    
                    if waste_pct > 30:
                        st.warning("💡 نصيحة للإدارة: نسبة الهدر عالية جداً، يُفضل تغيير مقاس الحبة أو طباعتها على رولات بمقاسات مختلفة لتوفير الخامة.")