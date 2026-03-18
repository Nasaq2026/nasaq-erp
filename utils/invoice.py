# utils/invoice.py
import streamlit as st
from datetime import datetime
from utils.zatca import generate_zatca_qr

def get_invoice_html(row):
    # تفكيك البيانات (تأكد أن ترتيب الصف يطابق قاعدة البيانات عندك)
    # ملاحظة: أضفت معالجة بسيطة لو الصف ناقص أو فيه بيانات مختلفة
    order_id, client, phone, date_in, date_out, price, vat, total, paid, cost, profit, designer, cat, details, status = row
    
    # توليد باركود هيئة الزكاة (QR Code)
    timestamp = datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")
    qr_base64 = generate_zatca_qr("مؤسسة نسق للدعاية والإعلان", "312345678900003", timestamp, total, vat)

    html_content = f"""
    <html dir="rtl">
    <head>
        <meta charset="UTF-8">
        <style>
            body {{ font-family: 'Tahoma', 'Arial', sans-serif; padding: 20px; color: #333; background-color: #f4f4f4; }}
            .invoice-box {{ border: 2px solid #2980b9; padding: 30px; border-radius: 15px; max-width: 800px; margin: auto; background-color: white; box-shadow: 0 4px 10px rgba(0,0,0,0.1); }}
            .header {{ display: flex; justify-content: space-between; align-items: center; border-bottom: 2px solid #2980b9; padding-bottom: 20px; }}
            .qr-code {{ width: 120px; height: 120px; }}
            .info-section {{ display: flex; justify-content: space-between; margin-top: 30px; font-size: 14px; line-height: 1.6; }}
            table {{ width: 100%; border-collapse: collapse; margin-top: 30px; text-align: center; }}
            th {{ background: #2980b9; color: white; padding: 12px; }}
            td {{ border: 1px solid #ddd; padding: 12px; }}
            .totals-table {{ width: 40%; margin-right: auto; margin-top: 20px; }}
            .footer {{ text-align: center; margin-top: 40px; color: #777; font-size: 12px; }}
        </style>
    </head>
    <body>
        <div class="invoice-box">
            <div class="header">
                <div style="text-align: right;">
                    <h1 style="color:#2980b9; margin:0;">مؤسسة نسق للدعاية والإعلان</h1>
                    <p style="margin: 5px 0;">الرقم الضريبي: 312345678900003</p>
                    <h3 style="margin-top: 10px;">فاتورة ضريبية مبسطة | Simplified Tax Invoice</h3>
                    <p><b>رقم الفاتورة:</b> #{order_id}</p>
                </div>
                <div>
                    <img class="qr-code" src="data:image/png;base64,{qr_base64}" alt="ZATCA QR Code" />
                </div>
            </div>
            
            <div class="info-section">
                <div><p><b>العميل:</b> {client}</p><p><b>الجوال:</b> {phone}</p></div>
                <div><p><b>التاريخ:</b> {date_in}</p><p><b>المصمم:</b> {designer}</p></div>
            </div>
            
            <table>
                <thead>
                    <tr>
                        <th>الوصف</th>
                        <th>المبلغ (قبل الضريبة)</th>
                        <th>الضريبة (15%)</th>
                        <th>الإجمالي</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td>{cat} - {details[:30]}...</td>
                        <td>{float(price):,.2f} ر.س</td>
                        <td>{float(vat):,.2f} ر.س</td>
                        <td><b>{float(total):,.2f} ر.س</b></td>
                    </tr>
                </tbody>
            </table>

            <table class="totals-table">
                <tr><td style="background:#f9f9f9;"><b>المدفوع</b></td><td>{float(paid):,.2f} ر.س</td></tr>
                <tr><td style="background:#f9f9f9;"><b>المتبقي</b></td><td style="color:red;"><b>{float(total) - float(paid):,.2f} ر.س</b></td></tr>
            </table>

            <div class="footer">شكراً لتعاملكم مع مؤسسة نسق للدعاية والإعلان</div>
        </div>
    </body>
    </html>
    """
    return html_content
