from io import BytesIO
from reportlab.lib.pagesizes import LETTER
from reportlab.pdfgen import canvas

def build_email_pdf(subject: str, body: str) -> bytes:
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=LETTER)

    width, height = LETTER
    x = 50
    y = height - 50

    c.setFont("Helvetica-Bold", 14)
    c.drawString(x, y, "Email Draft")
    y -= 30

    c.setFont("Helvetica-Bold", 11)
    c.drawString(x, y, "Subject:")
    y -= 15

    c.setFont("Helvetica", 11)
    c.drawString(x, y, subject or "")
    y -= 25

    c.setFont("Helvetica-Bold", 11)
    c.drawString(x, y, "Body:")
    y -= 15

    c.setFont("Helvetica", 11)
    for line in (body or "").split("\n"):
        c.drawString(x, y, line)
        y -= 14
        if y < 50:
            c.showPage()
            y = height - 50
            c.setFont("Helvetica", 11)

    c.save()
    buffer.seek(0)
    return buffer.read()
