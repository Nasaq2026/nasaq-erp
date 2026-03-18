# utils/invoice.py
import streamlit as st
import qrcode
import io
import base64
from datetime import datetime
from utils.zatca import generate_zatca_qr

def generate_invoice_html(order_row, client_row):
    """توليد كود HTML للفاتورة الضريبية متوافق مع معايير زاتكا 2026"""
    try:
        # استخراج البيانات الأساسية مع معالجة القيم الفارغة
        order_id = order_row[0] if order_row and order_row[0] else "000"
        client_name = order_row[2] if order_row and order_row[2] else "عميل"
        phone = order_row[3] if order_row and order_row[3] else "---"
        
        # تحويل القيم المالية لأرقام عشرية لضمان دقة الحسابات
        price = float(order_row[6]) if order_row[6] else 0.0
        vat = float(order_row[7]) if order_row[7] else 0.0
        total = float(order_row[8]) if order_row[8] else 0.0
        paid = float(order_row[9]) if order_row[9] else 0.0
        remaining = total - paid
        category = order_row[12] if order_row[12] else "خدمات دعاية وإعلان"

        # بيانات العميل الضريبية من جدول العملاء
        comp_name = client_row[3] if client_row and len(client_row) > 3 and client_row[3] else client_name
        client_vat = client_row[4] if client_row and len(client_row) > 4 and client_row[4] else "---"
        client_addr = client_row[5] if client_row and len(client_row) > 5 and client_row[5] else "المملكة العربية السعودية"

        date_str = datetime.now().strftime("%Y/%m/%d")
        timestamp = datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")

        # توليد نص الـ QR الخاص بهيئة الزكاة
        zatca_str = generate_zatca_qr("مؤسسة نسق للدعاية والإعلان", "312345678900003", timestamp, f"{total:.2f}", f"{vat:.2f}")
        
        # تحويل النص لصورة QR Code مدمجة Base64
        qr_img = qrcode.make(zatca_str)
        buf = io.BytesIO()
        qr_img.save(buf, format="PNG")
        qr_img_b64 = base64.b64encode(buf.getvalue()).decode("utf-8")

        # تصميم الـ HTML الاحترافي والأبيض للطباعة
        html = f"""
        <html dir="rtl">
        <head><meta charset="UTF-8"></head>
        <body style="font-family: Arial, sans-serif; padding: 20px; color: #000; background-color: #fff;">
            <div style="border: 1px solid #000; padding: 20px; max-width: 800px; margin: auto;">
                <table width="100%" style="border-bottom: 2px solid #000; padding-bottom: 10px;">
                    <tr>
                        <td align="right">
                            <h2 style="margin:0;">مؤسسة نسق للدعاية والإعلان</h2>
                            <p style="margin:5px 0;">الرقم الضريبي: 312345678900003</p>
                            <h3 style="margin-top:10px;">فاتورة ضريبية مبسطة | Tax Invoice</h3>
                        </td>
                        <td align="left">
                            <img src="data:image/png;base64,{qr_img_b64}" width="120">
                            <p style="margin:5px 0;"><b>رقم:</b> INV-{order_id}</p>
                            <p style="margin:5px 0;"><b>التاريخ:</b> {date_str}</p>
                        </td>
                    </tr>
                </table>

                <div style="margin: 20px 0; border: 1px solid #eee; padding: 10px;">
                    <p><b>معلومات العميل:</b> {comp_name}</p>
                    <p><b>الرقم الضريبي للعميل:</b> {client_vat}</p>
                </div>

                <table width="100%" border="1" style="border-collapse: collapse; text-align: center;">
                    <tr style="background:#f2f2f2;">
                        <th>الوصف</th><th>السعر</th><th>الضريبة</th><th>الإجمالي</th>
                    </tr>
                    <tr>
                        <td>{category}</td>
                        <td>{price:,.2f}</td>
                        <td>{vat:,.2f}</td>
                        <td><b>{total:,.2f}</b></td>
                    </tr>
                </table>

                <div style="margin-top: 20px; width: 40%; margin-right: auto;">
                    <table width="100%" border="1" style="border-collapse: collapse;">
                        <tr><td style="padding:5px;">المدفوع</td><td align="center">{paid:,.2f}</td></tr>
                        <tr style="color:red; font-weight:bold;"><td style="padding:5px;">المتبقي</td><td align="center">{remaining:,.2f}</td></tr>
                    </table>
                </div>
            </div>
        </body>
        </html>
        """
        return html
    except Exception as e:
        st.error(f"❌ فشل توليد HTML الفاتورة: {e}")
        return ""
