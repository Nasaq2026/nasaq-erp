# utils/invoice_generator.py

import os
import base64
import qrcode

from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas


# =========================================
# TLV ENCODING (ZATCA QR)
# =========================================

def _tlv(tag, value):

    value_bytes = value.encode("utf-8")

    return bytes([tag]) + bytes([len(value_bytes)]) + value_bytes


def generate_zatca_qr(seller, vat, timestamp, total, vat_total):

    tlv_data = b''.join([
        _tlv(1, seller),
        _tlv(2, vat),
        _tlv(3, timestamp),
        _tlv(4, total),
        _tlv(5, vat_total)
    ])

    base64_qr = base64.b64encode(tlv_data).decode()

    qr = qrcode.make(base64_qr)

    if not os.path.exists("temp"):
        os.makedirs("temp")

    path = "temp/invoice_qr.png"
    qr.save(path)

    return path, base64_qr


# =========================================
# CREATE PDF INVOICE
# =========================================

def create_invoice_pdf(invoice):

    """
    invoice = {
        "seller": "",
        "vat": "",
        "client": "",
        "invoice_number": "",
        "date": "",
        "total": "",
        "vat_total": ""
    }
    """

    if not os.path.exists("invoices"):
        os.makedirs("invoices")

    timestamp = datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")

    qr_path, qr_data = generate_zatca_qr(
        invoice["seller"],
        invoice["vat"],
        timestamp,
        str(invoice["total"]),
        str(invoice["vat_total"])
    )

    file_path = f"invoices/invoice_{invoice['invoice_number']}.pdf"

    c = canvas.Canvas(file_path, pagesize=A4)

    width, height = A4


    # ========================
    # عنوان الفاتورة
    # ========================

    c.setFont("Helvetica-Bold", 20)
    c.drawString(80, height - 80, "Invoice")


    # ========================
    # بيانات المؤسسة
    # ========================

    c.setFont("Helvetica", 12)

    c.drawString(80, height - 120, f"Seller : {invoice['seller']}")
    c.drawString(80, height - 140, f"VAT No : {invoice['vat']}")


    # ========================
    # بيانات العميل
    # ========================

    c.drawString(80, height - 180, f"Client : {invoice['client']}")


    # ========================
    # تفاصيل الفاتورة
    # ========================

    c.drawString(80, height - 220, f"Invoice No : {invoice['invoice_number']}")
    c.drawString(80, height - 240, f"Date : {invoice['date']}")



    # ========================
    # المبالغ
    # ========================

    c.drawString(80, height - 300, f"Total : {invoice['total']} SAR")
    c.drawString(80, height - 320, f"VAT : {invoice['vat_total']} SAR")



    # ========================
    # QR CODE
    # ========================

    c.drawImage(qr_path, width - 200, height - 260, 120, 120)



    # ========================
    # نص أسفل الفاتورة
    # ========================

    c.setFont("Helvetica", 9)

    c.drawString(
        80,
        100,
        "Scan QR using ZATCA E-Invoice QR Reader"
    )


    c.save()

    return file_path, qr_data