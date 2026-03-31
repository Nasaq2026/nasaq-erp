import streamlit as st
import pandas as pd
import urllib.parse
from datetime import datetime

def render_finance(conn):
    st.title("💰 الإدارة المالية والتحصيل الذكي")
    
    # 1. إحصائيات عامة (KPIs)
    cursor = conn.cursor()
    cursor.execute("SELECT SUM(total_with_vat), SUM(paid), SUM(profit) FROM orders")
    totals = cursor.fetchone()
    total_sales = float(totals[0]) if totals[0] else 0.0
    total_paid = float(totals[1]) if totals[1] else 0.0
    total_profit = float(totals[2]) if totals[2] else 0.0
    total_debt = total_sales - total_paid

    col_s1, col_s2, col_s3 = st.columns(3)
    col_s1.metric("إجمالي المبيعات", f"{total_sales:,.2f} ر.س")
    col_s2.metric("إجمالي المحصل", f"{total_paid:,.2f} ر.س", delta=f"{total_debt:,.2f} متبقي", delta_color="inverse")
    col_s3.metric("صافي الأرباح المتوقعة", f"{total_profit:,.2f} ر.س")

    st.divider()

    # 2. تبويبات النظام المالي
    tab_debt, tab_pricing, tab_quotes = st.tabs(["⚠️ مديونيات العملاء", "⚙️ إدارة أسعار الخدمات", "📄 عروض الأسعار"])

    # --- تبويب المديونيات ---
    with tab_debt:
        render_collection_center(conn)

    # --- تبويب إدارة الأسعار (نظام التسعير الاحترافي الذي طلبته) ---
    with tab_pricing:
        st.subheader("🛠️ ضبط أسعار الخدمات (موديول)")
        st.info("قم بتعديل أسعار المتر أو القطعة هنا، وسيتم تحديثها تلقائياً في عروض الأسعار.")
        
        # جلب الأسعار الحالية
        df_prices = pd.read_sql("SELECT category, unit_price, unit_type FROM services_pricing", conn)
        edited_prices = st.data_editor(df_prices, use_container_width=True, num_rows="dynamic", key="price_editor")
        
        if st.button("💾 حفظ تحديثات الأسعار"):
            for index, row in edited_prices.iterrows():
                cursor.execute("""
                    INSERT INTO services_pricing (category, unit_price, unit_type) 
                    VALUES (%s, %s, %s) 
                    ON CONFLICT (category) DO UPDATE SET unit_price = EXCLUDED.unit_price, unit_type = EXCLUDED.unit_type
                """, (row['category'], row['unit_price'], row['unit_type']))
            conn.commit()
            st.success("✅ تم تحديث قائمة الأسعار بنجاح!")

    # --- تبويب عروض الأسعار ---
    with tab_quotes:
        render_quotes_engine(conn)

def render_collection_center(conn):
    st.subheader("💳 مركز التحصيل والمتابعة")
    query = """
        SELECT work_order_sn, client_name, phone, total_with_vat, paid, 
        (total_with_vat - paid) as remaining 
        FROM orders WHERE (total_with_vat - paid) > 0
    """
    df_debts = pd.read_sql(query, conn)

    if df_debts.empty:
        st.success("🎉 لا توجد مديونيات معلقة حالياً!")
    else:
        for index, row in df_debts.iterrows():
            with st.container():
                c1, c2, c3 = st.columns([2, 1, 1])
                c1.write(f"👤 **{row['client_name']}**\nطلب: {row['work_order_sn']}")
                c2.error(f"المتبقي: {row['remaining']:,.2f} ر.س")
                
                # رسالة واتساب احترافية مع ترميز URL الصحيح
                msg = f"عزيزنا {row['client_name']}، نذكركم بالمبلغ المتبقي لطلبكم {row['work_order_sn']} وقدره {row['remaining']} ر.س لدى مؤسسة موديول ✨."
                link = f"https://wa.me/{row['phone']}?text={urllib.parse.quote(msg)}"
                c3.markdown(f"<a href='{link}' target='_blank' style='text-decoration:none;'><button style='width:100%; border-radius:10px; background-color:#25d366; color:white; border:none; padding:5px;'>📲 مطالبة واتساب</button></a>", unsafe_allow_html=True)

def render_quotes_engine(conn):
    st.subheader("📑 محرك عروض الأسعار والتسعير التلقائي")
    
    # جلب الأسعار لاستخدامها في الحساب التلقائي
    cursor = conn.cursor()
    cursor.execute("SELECT category, unit_price, unit_type FROM services_pricing")
    prices = {r[0]: (float(r[1]), r[2]) for r in cursor.fetchall()}

    with st.expander("✨ إنشاء عرض سعر ذكي"):
        c1, c2 = st.columns(2)
        q_client = c1.text_input("اسم العميل المستهدف")
        q_phone = c2.text_input("رقم الجوال")
        
        q_cat = st.selectbox("نوع الخدمة", list(prices.keys()))
        u_price, u_type = prices[q_cat]
        
        q_qty = st.number_input(f"الكمية بالـ ({u_type})", min_value=0.1, value=1.0)
        
        # الحساب التلقائي
        subtotal = q_qty * u_price
        vat = subtotal * 0.15
        total = subtotal + vat
        
        st.info(f"💰 التسعير التلقائي: {u_price} ريال لكل {u_type} | الإجمالي مع الضريبة: {total:,.2f} ريال")
        
        if st.button("حفظ وتحويل لعرض سعر رسمي"):
            q_sn = f"QT-{datetime.now().strftime('%m%d%H%M')}"
            cursor.execute("""
                INSERT INTO quotations (quote_sn, client_name, phone, details, total_amount, status)
                VALUES (%s, %s, %s, %s, %s, 'مسودة')
            """, (q_sn, q_client, q_phone, q_cat, total))
            conn.commit()
            st.success(f"✅ تم حفظ عرض السعر {q_sn}")
