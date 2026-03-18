# utils/invoice.py
import os
import webbrowser
import qrcode
import io
import base64
from datetime import datetime
from utils.zatca import generate_zatca_qr

def generate_invoice_html(order_row, client_row):
    # order_row: يحتوي على بيانات الطلب
    # client_row: يحتوي على بيانات العميل (الرقم الضريبي، المؤسسة، الخ)
    
    # التأكد من تحويل القيم المالية لأرقام لتجنب أي أخطاء
    try:
        order_id = order_row[0]
        client_name = order_row[2]
        phone = order_row[3]
        price = float(order_row[6] or 0)
        vat = float(order_row[7] or 0)
        total = float(order_row[8] or 0)
        paid = float(order_row[9] or 0)
        category = order_row[12]
    except Exception as e:
        print("خطأ في قراءة بيانات الطلب:", e)
        return
    
    # استخراج بيانات العميل الضريبية (إن وجدت)
    comp_name = client_row[3] if client_row and len(client_row) > 3 and client_row[3] else client_name
    client_vat = client_row[4] if client_row and len(client_row) > 4 and client_row[4] else "---"
    client_addr = client_row[5] if client_row and len(client_row) > 5 and client_row[5] else "---"

    date_str = datetime.now().strftime("%Y/%m/%d")
    timestamp = datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")

    # توليد نص هيئة الزكاة والدخل
    zatca_str = generate_zatca_qr("مؤسسة نسق للدعاية والإعلان", "312345678900003", timestamp, f"{total:.2f}", f"{vat:.2f}")
    
    # تحويل النص إلى صورة QR Code حقيقية ودمجها في كود HTML (بدون الحاجة لحفظ صورة خارجية)
    qr_img = qrcode.make(zatca_str)
    buffer = io.BytesIO()
    qr_img.save(buffer, format="PNG")
    qr_img_b64 = base64.b64encode(buffer.getvalue()).decode("utf-8")

    # 🔴 التصميم الجديد المتوافق مع المتصفح 100% (نسخة قياسية بيضاء/رمادية)
    html = f"""
    <html dir="rtl">
    <head><meta charset="UTF-8"></head>
    <body style="font-family: Arial, sans-serif; font-size: 14px; color: #000; padding: 40px; max-width: 900px; margin: auto;">

        <table width="100%" cellpadding="5" style="margin-bottom: 20px;">
            <tr>
                <td width="50%" valign="top" align="right">
                    <h2 style="margin: 0; font-size: 22px; font-weight: bold; color: #333;">مؤسسة نسق للدعاية والإعلان</h2>
                    <p style="margin: 5px 0;">الرقم الضريبي : 312345678900003</p>
                    <p style="margin: 5px 0;">السجل التجاري : 1010123456</p>
                    <p style="margin: 5px 0;">العنوان : المملكة العربية السعودية</p>
                </td>
                <td width="50%" valign="top" align="left">
                    <table width="100%">
                        <tr>
                            <td align="left">
                                <h2 style="margin: 0 0 10px 0; font-size: 20px; font-weight: bold;">فاتورة ضريبية</h2>
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

        <div style="margin-top: 20px; margin-bottom: 20px; font-size: 14px;">
            <p style="margin: 4px 0;">العميل : {comp_name}</p>
            <p style="margin: 4px 0;">الرقم الضريبي : {client_vat}</p>
            <p style="margin: 4px 0;">العنوان : {client_addr}</p>
        </div>

        <table width="100%" border="0" cellpadding="10" style="border-collapse: collapse; text-align: center; border-bottom: 1px solid #ccc; border-top: 1px solid #ccc;">
            <tr style="background-color: #f4f6f8; font-weight: bold; font-size: 13px; color: #333;">
                <td style="border-bottom: 1px solid #ccc;">البند</td>
                <td style="border-bottom: 1px solid #ccc;">الوصف</td>
                <td style="border-bottom: 1px solid #ccc;">الكمية</td>
                <td style="border-bottom: 1px solid #ccc;">السعر</td>
                <td style="border-bottom: 1px solid #ccc;">المجموع بدون الضريبة</td>
                <td style="border-bottom: 1px solid #ccc;">نسبة الضريبة</td>
                <td style="border-bottom: 1px solid #ccc;">قيمة الضريبة</td>
                <td style="border-bottom: 1px solid #ccc;">المجموع</td>
            </tr>
            <tr style="font-size: 13px;">
                <td>1</td>
                <td>{category}</td>
                <td>1</td>
                <td>{price:.2f}</td>
                <td>{price:.2f}</td>
                <td>15%</td>
                <td>{vat:.2f}</td>
                <td>{total:.2f}</td>
            </tr>
        </table>

        <table width="100%" style="margin-top: 30px;">
            <tr>
                <td width="60%" valign="top">
                    <p style="font-weight: bold; font-size: 14px; margin-bottom: 5px;">بيانات الدفع</p>
                    <p style="margin: 3px 0; font-size: 13px;">بنك الراجحي</p>
                    <p style="margin: 3px 0; font-size: 13px;">رقم الحساب : 123456789012345</p>
                    <p style="margin: 3px 0; font-size: 13px;">رقم الايبان : SA1234567890123456789012</p>
                </td>
                <td width="40%" valign="top">
                    <table width="100%" style="border-collapse: collapse; text-align: left;" cellpadding="10">
                        <tr>
                            <th style="border-bottom: 1px solid #ddd; text-align: right; font-size: 13px; color: #555;">الإجمالي قبل الضريبة</th>
                            <td style="border-bottom: 1px solid #ddd; font-size: 13px;">{price:.2f}</td>
                        </tr>
                        <tr>
                            <th style="border-bottom: 1px solid #ddd; text-align: right; font-size: 13px; color: #555;">القيمة المضافة (15%)</th>
                            <td style="border-bottom: 1px solid #ddd; font-size: 13px;">{vat:.2f}</td>
                        </tr>
                        <tr>
                            <th style="border-bottom: 2px solid #333; text-align: right; font-size: 15px; color: #000;">الإجمالي (ر.س)</th>
                            <td style="border-bottom: 2px solid #333; font-size: 15px; font-weight: bold;">{total:.2f}</td>
                        </tr>
                        <tr>
                            <th style="border-bottom: 1px solid #eee; text-align: right; font-size: 12px; color: #10B981; padding-top: 15px;">المدفوع</th>
                            <td style="border-bottom: 1px solid #eee; font-size: 12px; color: #10B981; padding-top: 15px;">{paid:.2f}</td>
                        </tr>
                        <tr>
                            <th style="text-align: right; font-size: 13px; color: #EF4444;">المتبقي</th>
                            <td style="font-size: 13px; color: #EF4444; font-weight: bold;">{total - paid:.2f}</td>
                        </tr>
                    </table>
                </td>
            </tr>
        </table>
        
        <p style="text-align: center; color: #888; font-size: 12px; margin-top: 50px;">شكراً لتعاملكم مع مؤسسة نسق للدعاية والإعلان</p>

    </body>
    </html>
    """
    
    with open("temp_inv.html", "w", encoding="utf-8") as f: 
        f.write(html)
    webbrowser.open("file://" + os.path.abspath("temp_inv.html"))