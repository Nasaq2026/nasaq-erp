# utils/invoice.py
import streamlit as st
import qrcode
import io
import base64
from datetime import datetime
from utils.zatca import generate_zatca_qr

def generate_invoice_html(order_row, client_row):
    try:
        # بيانات الطلب
        order_id = order_row[0]
        sn = order_row[1]
        client_name = order_row[2]
        phone = order_row[3]
        price = float(order_row[6] or 0)
        vat = float(order_row[7] or 0)
        total = float(order_row[8] or 0)
        paid = float(order_row[9] or 0)
        category = order_row[12]
        
        # بيانات العميل (السجل، الضريبي، العنوان)
        comp_name = client_row[3] if client_row and client_row[3] else client_name
        c_vat = client_row[4] if client_row and client_row[4] else "---"
        c_cr = client_row[6] if client_row and len(client_row) > 6 else "---" # السجل التجاري
        c_addr = client_row[5] if client_row and client_row[5] else "المملكة العربية السعودية" # العنوان الوطني
    except Exception as e:
        return f"<html><body>خطأ في البيانات: {e}</body></html>"

    # توليد QR هيئة الزكاة
    timestamp = datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")
    zatca_str = generate_zatca_qr("مؤسسة نسق للدعاية والإعلان", "312345678900003", timestamp, f"{total:.2f}", f"{vat:.2f}")
    qr_img = qrcode.make(zatca_str)
    buf = io.BytesIO()
    qr_img.save(buf, format="PNG")
    qr_img_b64 = base64.b64encode(buf.getvalue()).decode("utf-8")

    html = f"""
    <html dir="rtl">
    <head><meta charset="UTF-8">
    <style>
        body {{ font-family: 'Arial', sans-serif; padding: 20px; }}
        .inv-card {{ border: 2px solid #2980b9; padding: 20px; max-width: 850px; margin: auto; border-radius: 10px; }}
        .header {{ display: flex; justify-content: space-between; border-bottom: 2px solid #2980b9; padding-bottom: 15px; }}
        .details-table {{ width: 100%; border-collapse: collapse; margin-top: 20px; }}
        .details-table th, .details-table td {{ border: 1px solid #ddd; padding: 12px; text-align: center; }}
        .details-table th {{ background: #2980b9; color: white; }}
        .qr-code {{ width: 130px; height: 130px; }}
    </style>
    </head>
    <body>
        <div class="inv-card">
            <div class="header">
                <div style="text-align: right;">
                    <h2 style="color:#2980b9; margin:0;">مؤسسة نسق للدعاية والإعلان</h2>
                    <p style="margin:5px 0;">الرقم الضريبي للمنشأة: 312345678900003</p>
                    <p style="margin:5px 0;">السجل التجاري: 1010123456</p>
                    <p style="margin:5px 0;">العنوان الوطني: تبوك - المملكة العربية السعودية</p>
                    <h3 style="margin-top:15px; background:#f4f4f4; display:inline-block; padding:5px 15px;">فاتورة ضريبية مبسطة</h3>
                </div>
                <img class="qr-code" src="data:image/png;base64,{qr_img_b64}">
            </div>
            
            <div style="margin-top: 20px; display: grid; grid-template-columns: 1fr 1fr; gap: 20px; font-size: 14px;">
                <div style="border: 1px solid #eee; padding: 10px;">
                    <p><b>الفاتورة لـ:</b> {comp_name}</p>
                    <p><b>الرقم الضريبي للعميل:</b> {c_vat}</p>
                    <p><b>السجل التجاري للعميل:</b> {c_cr}</p>
                    <p><b>العنوان الوطني:</b> {c_addr}</p>
                </div>
                <div style="text-align: left; border: 1px solid #eee; padding: 10px;">
                    <p><b>رقم الفاتورة:</b> INV-{sn}</p>
                    <p><b>التاريخ:</b> {datetime.now().strftime('%Y-%m-%d')}</p>
                    <p><b>رقم الجوال:</b> {phone}</p>
                </div>
            </div>

            <table class="details-table">
                <tr><th>البيان (الخدمة)</th><th>المبلغ قبل الضريبة</th><th>الضريبة (15%)</th><th>الإجمالي</th></tr>
                <tr><td>{category}</td><td>{price:,.2f}</td><td>{vat:,.2f}</td><td><b>{total:,.2f}</b></td></tr>
            </table>

            <div style="margin-top: 20px; width: 40%; margin-right: auto;">
                <table style="width:100%; border-collapse: collapse;">
                    <tr style="background:#f9f9f9;"><td>المدفوع:</td><td align="center">{paid:,.2f}</td></tr>
                    <tr style="color:red; font-weight:bold;"><td>المتبقي:</td><td align="center">{total-paid:,.2f}</td></tr>
                </table>
            </div>
            <p style="text-align: center; margin-top: 30px; font-size: 12px; color: #777;">شكراً لتعاملكم معنا</p>
        </div>
    </body>
    </html>
    """
    return html
