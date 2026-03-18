from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
from datetime import datetime

def create_professional_invoice(data, qr_path):

    width, height = A4

    pdf_path = f"invoices/invoice_{data['invoice_no']}.pdf"

    c = canvas.Canvas(pdf_path, pagesize=A4)

    # =============================
    # HEADER
    # =============================

    if os.path.exists("assets/logo.png"):
        c.drawImage("assets/logo.png", 20*mm, height-40*mm, 35*mm, 25*mm)

    c.setFont("Helvetica-Bold", 20)
    c.drawRightString(width-20*mm, height-25*mm, "فاتورة ضريبية")

    c.setFont("Helvetica", 11)
    c.drawRightString(width-20*mm, height-32*mm, f"رقم الفاتورة: {data['invoice_no']}")
    c.drawRightString(width-20*mm, height-38*mm, f"التاريخ: {datetime.now().strftime('%Y-%m-%d')}")

    # =============================
    # COMPANY INFO
    # =============================

    c.setFont("Helvetica-Bold", 12)
    c.drawString(20*mm, height-60*mm, "بيانات البائع")

    c.setFont("Helvetica", 11)
    c.drawString(20*mm, height-68*mm, f"المؤسسة: {data['seller']}")
    c.drawString(20*mm, height-75*mm, f"الرقم الضريبي: {data['vat']}")

    # =============================
    # CLIENT INFO
    # =============================

    c.setFont("Helvetica-Bold", 12)
    c.drawString(120*mm, height-60*mm, "بيانات العميل")

    c.setFont("Helvetica", 11)
    c.drawString(120*mm, height-68*mm, f"الاسم: {data['client']}")
    c.drawString(120*mm, height-75*mm, f"الجوال: {data['phone']}")

    # =============================
    # TABLE HEADER
    # =============================

    table_y = height-100*mm

    c.setFont("Helvetica-Bold", 11)

    c.drawString(20*mm, table_y, "المنتج")
    c.drawString(100*mm, table_y, "الكمية")
    c.drawString(120*mm, table_y, "السعر")
    c.drawString(150*mm, table_y, "الإجمالي")

    c.line(20*mm, table_y-3, 190*mm, table_y-3)

    # =============================
    # ITEMS
    # =============================

    c.setFont("Helvetica", 11)

    y = table_y-15

    for item in data["items"]:

        c.drawString(20*mm, y, item["name"])
        c.drawString(100*mm, y, str(item["qty"]))
        c.drawString(120*mm, y, str(item["price"]))
        c.drawString(150*mm, y, str(item["total"]))

        y -= 10

    # =============================
    # TOTAL BOX
    # =============================

    y -= 10

    c.setFont("Helvetica-Bold", 12)

    c.drawRightString(190*mm, y, f"الإجمالي: {data['total']} ر.س")

    y -= 10

    c.drawRightString(190*mm, y, f"ضريبة القيمة المضافة: {data['vat_total']} ر.س")

    y -= 10

    total_final = float(data["total"]) + float(data["vat_total"])

    c.drawRightString(190*mm, y, f"الإجمالي شامل الضريبة: {total_final} ر.س")

    # =============================
    # QR CODE
    # =============================

    c.drawImage(qr_path, 20*mm, 20*mm, 35*mm, 35*mm)

    # =============================
    # FOOTER
    # =============================

    c.setFont("Helvetica", 9)

    c.drawCentredString(width/2, 15*mm, "شكراً لتعاملكم مع مؤسسة نسق للدعاية والإعلان")

    c.save()

    return pdf_path