import streamlit as st
import streamlit.components.v1 as components

def show_invoice_printer(conn, selected_sn):
    """دالة لجلب البيانات وطباعة الفاتورة بشكل احترافي"""
    cursor = conn.cursor()
    
    # 1. جلب البيانات المالية (تأكد من مطابقة أسماء الأعمدة لجدولك)
    cursor.execute("""
        SELECT work_order_sn, client_name, phone, details, 
               total_with_vat, paid, (total_with_vat - paid) as debt,
               category, material_type, dimensions
        FROM orders WHERE work_order_sn = %s
    """, (selected_sn,))
    
    res = cursor.fetchone()
    
    if not res:
        st.error("❌ لم يتم العثور على بيانات لهذا الطلب في قاعدة البيانات.")
        return

    # ترتيب البيانات في قاموس
    d = {
        'sn': res[0], 'name': res[1], 'phone': res[2], 'details': res[3],
        'total': float(res[4]), 'paid': float(res[5]), 'debt': float(res[6]),
        'cat': res[7], 'mat': res[8], 'dims': res[9]
    }

    # 2. قالب HTML الفاتورة (تصميم موديول الرسمي)
    html_template = f"""
    <div id="invoice" style="direction: rtl; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; padding: 40px; color: #333; line-height: 1.6;">
        <div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 2px solid #1e293b; padding-bottom: 20px;">
            <div>
                <h1 style="margin: 0; color: #1e293b;">مؤسسة موديول للدعاية والإعلان ✨</h1>
                <p style="margin: 5px 0;">جازان - المملكة العربية السعودية</p>
            </div>
            <div style="text-align: left;">
                <h2 style="margin: 0; color: #64748b;">فاتورة ضريبية</h2>
                <p style="margin: 5px 0;">رقم الطلب: <b>{d['sn']}</b></p>
            </div>
        </div>

        <div style="margin-top: 30px; display: flex; justify-content: space-between;">
            <div>
                <p><b>السادة/</b> {d['name']}</p>
                <p><b>رقم الجوال:</b> {d['phone']}</p>
            </div>
            <div style="text-align: left;">
                <p><b>التاريخ:</b> {st.session_state.get('current_date', '2026-03-31')}</p>
            </div>
        </div>

        <table style="width: 100%; border-collapse: collapse; margin-top: 30px;">
            <thead>
                <tr style="background-color: #1e293b; color: white;">
                    <th style="padding: 12px; border: 1px solid #ddd; text-align: right;">الوصف والخدمة</th>
                    <th style="padding: 12px; border: 1px solid #ddd; text-align: center;">المواصفات / المقاسات</th>
                    <th style="padding: 12px; border: 1px solid #ddd; text-align: center;">الإجمالي (شامل الضريبة)</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td style="padding: 12px; border: 1px solid #ddd;">{d['cat']} ({d['mat']})</td>
                    <td style="padding: 12px; border: 1px solid #ddd; text-align: center;">{d['details']} <br> {d['dims']}</td>
                    <td style="padding: 12px; border: 1px solid #ddd; text-align: center;">{d['total']:,.2f} ر.س</td>
                </tr>
            </tbody>
        </table>

        <div style="margin-top: 40px; margin-right: auto; width: 300px; background: #f8fafc; padding: 20px; border-radius: 8px;">
            <div style="display: flex; justify-content: space-between; margin-bottom: 10px;">
                <span>الإجمالي:</span> <b>{d['total']:,.2f} ر.س</b>
            </div>
            <div style="display: flex; justify-content: space-between; margin-bottom: 10px; color: green;">
                <span>المدفوع:</span> <b>{d['paid']:,.2f} ر.س</b>
            </div>
            <div style="display: flex; justify-content: space-between; padding-top: 10px; border-top: 2px solid #ddd; color: red; font-size: 18px;">
                <span>المتبقي:</span> <b>{d['debt']:,.2f} ر.س</b>
            </div>
        </div>

        <div style="margin-top: 50px; text-align: center;">
            <button onclick="window.print()" style="padding: 12px 30px; background-color: #1e293b; color: white; border: none; border-radius: 5px; cursor: pointer; font-size: 16px;">
                🖨️ حفظ كـ PDF أو طباعة الفاتورة
            </button>
            <p style="font-size: 12px; color: #94a3b8; margin-top: 20px;">نظام نَسق لإدارة المطابع - موديول 2026</p>
        </div>
    </div>
    """
    
    # عرض الفاتورة في Streamlit
    components.html(html_template, height=900, scrolling=True)

# الاستدعاء في واجهة المستخدم (تضعه في المكان الذي تريد ظهور الزر فيه)
if st.button("🧾 إصدار فاتورة ضريبية"):
    # استبدل 'WO-03311649' بالمتغير الذي يحمل رقم الطلب المختار
    show_invoice_printer(conn, 'WO-03311649')
