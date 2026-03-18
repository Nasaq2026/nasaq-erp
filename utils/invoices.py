# utils/invoice.py
import streamlit as st
import qrcode
import io
import base64
from datetime import datetime
from utils.zatca import generate_zatca_qr

def generate_invoice_html(order_row, client_row):
    try:
        # استخراج البيانات والتأكد من تحويلها لأرقام
        order_id = order_row[0]
        client_name = order_row[2]
        phone = order_row[3]
        price = float(order_row[6] or 0)
        vat = float(order_row[7] or 0)
        total = float(order_row[8] or 0)
        paid = float(order_row[9] or 0)
        category = order_row[12]
    except Exception as e:
        st.error(f"خطأ في قراءة بيانات الطلب: {e}")
        return ""

    # استخراج بيانات العميل الضريبية
    comp_name = client_row[3] if client_row and len(client_row) > 3 and client_row[3] else client_name
    client_vat = client_row[4] if client_row and len(client_row) > 4 and client_row[4] else "---"
    client_addr = client_row[5] if client_row and len(client_row) > 5 and client_row[5] else "---"

    date_str = datetime.now().strftime("%Y/%m/%d")
    timestamp = datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")

    # 1. توليد نص هيئة الزكاة (ZATCA)
    zatca_str = generate_zatca_qr("مؤسسة نسق للدعاية والإعلان", "312345678900003", timestamp, f"{total:.2f}", f"{vat:.2f}")
    
    # 2. تحويل النص إلى صورة QR Code حقيقية مدمجة
    qr_img = qrcode.make(zatca_str)
    buffer = io.BytesIO()
    qr_img.save(buffer, format="PNG")
    qr_img_b64 = base64.b64encode(buffer.getvalue()).decode("utf-8")

    # 3. بناء هيكل الـ HTML (بدون أوامر فتح ملفات)
    html = f"""
    <html dir="rtl">
    <head><meta charset="UTF-8"></head>
    <body style="font-family: Arial, sans-serif; font-size: 14px; color: #000; padding: 20px; max-width: 850px; margin: auto; background-color: #fff;">

        <table width="100%" cellpadding="5" style="margin-bottom: 20px; border-bottom: 2px solid #333; padding-bottom: 10px;">
            <tr>
                <td width="50%" valign="top" align="right">
                    <h2 style="margin: 0; font-size: 22px; font-weight: bold; color: #1e293b;">مؤسسة نسق للدعاية والإعلان</h2>
                    <p style="margin: 5px 0;">الرقم الضريبي : 312345678900003</p>
                    <p style="margin: 5px 0;">السجل التجاري : 1010123456</p>
                    <p style="margin: 5px 0;">العنوان : المملكة العربية السعودية</p>
                </td>
                <td width="50%" valign="top" align="left">
                    <table width="100%">
                        <tr>
                            <td align="left">
                                <h2 style="margin: 0 0 10px 0; font-size: 20px; font-weight: bold;">فاتورة ضريبية مبسطة</h2>
                                <img src="data:image/png;base64,{qr_img_b64}" width="130" height="130" style="border: 1px solid #eee; padding: 5px; border-radius: 8px;">
                            </td>
                        </tr>
                        <tr>
                            <td align="left" style="font-weight: bold; font-size: 13px;">
                                <p style="margin: 2px 0;">الرقم &nbsp;&nbsp;&nbsp; INV-{order_id}</p>
                                <p style="margin: 2px 0;">التاريخ &nbsp;&nbsp; {date_str}</p>
                            </td>
                        </tr>
                    </table>
                </td>
            </tr>
        </table>

        <div style="margin-top: 20px; margin-bottom: 20px; font-size: 14px; border: 1px solid #eee; padding: 10px; border-radius: 5px;">
            <p style="margin: 4px 0;"><b>معلومات العميل:</b></p>
            <p style="margin: 4px 0;">العميل : {comp_name}</p>
            <p style="margin: 4px 0;">الرقم الضريبي : {client_vat}</p>
            <p style="margin: 4px 0;">العنوان : {client_addr}</p>
        </div>

        <table width="100%" border="0" cellpadding="10" style="border-collapse: collapse; text-align: center;">
            <tr style="background-color: #f8fafc; font-weight: bold; font-size: 13px; color: #1e293b; border-bottom: 1px solid #ddd;">
                <td>#</td>
                <td>الوصف</td>
                <td>الكمية</td>
                <td>السعر</td>
                <td>الضريبة (15%)</td>
                <td>المجموع</td>
            </tr>
            <tr style="font-size: 13px; border-bottom: 1px solid #eee;">
                <td>1</td>
                <td>{category}</td>
                <td>1</td>
                <td>{price:,.2f}</td>
                <td>{vat:,.2f}</td>
                <td><b>{total:,.2f}</b></td>
            </tr>
        </table>

        <table width="100%" style="margin-top: 30px;">
            <tr>
                <td width="60%" valign="top" style="font-size: 12px; color: #64748b;">
                    <p style="font-weight: bold; font-size: 14px; color: #333; margin-bottom: 5px;">بيانات الدفع البنكي:</p>
                    <p style="margin: 2px 0;">بنك الراجحي</p>
                    <p style="margin: 2px 0;">رقم الحساب : 123456789012345</p>
                    <p style="margin: 2px 0;">الايبان : SA1234567890123456789012</p>
                </td>
                <td width="40%" valign="top">
                    <table width="100%" style="border-collapse: collapse; text-align: left;" cellpadding="8">
                        <tr>
                            <th style="border-bottom: 1px solid #eee; text-align: right; font-size: 13px;">الإجمالي قبل الضريبة</th>
                            <td style="border-bottom: 1px solid #eee; font-size: 13px;">{price:,.2f}</td>
                        </tr>
                        <tr>
                            <th style="border-bottom: 1px solid #eee; text-align: right; font-size: 13px;">ضريبة القيمة المضافة</th>
                            <td style="border-bottom: 1px solid #eee; font-size: 13px;">{vat:,.2f}</td>
                        </tr>
                        <tr style="background-color: #f8fafc;">
                            <th style="border-bottom: 2px solid #1e293b; text-align: right; font-size: 15px;">الإجمالي شامل الضريبة</th>
                            <td style="border-bottom: 2px solid #1e293b; font-size: 15px; font-weight: bold;">{total:,.2f} ر.س</td>
                        </tr>
                        <tr>
                            <th style="text-align: right; font-size: 12px; color: #10B981;">المدفوع</th>
                            <td style="font-size: 12px; color: #10B981;">{paid:,.2f}</td>
                        </tr>
                        <tr>
                            <th style="text-align: right; font-size: 13px; color: #EF4444; font-weight: bold;">المتبقي</th>
                            <td style="font-size: 13px; color: #EF4444; font-weight: bold;">{total - paid:,.2f}</td>
                        </tr>
                    </table>
                </td>
            </tr>
        </table>
        
        <p style="text-align: center; color: #94a3b8; font-size: 12px; margin-top: 40px; border-top: 1px dashed #ddd; padding-top: 10px;">شكراً لتعاملكم مع مؤسسة نسق للدعاية والإعلان</p>
    </body>
    </html>
    """
    return html # ✅ نرجع الكود عشان الـ App يستلمه
