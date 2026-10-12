"""Generate a small synthetic PDF fixture; no real customer data is bundled."""

from pathlib import Path

from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

output = Path(__file__).with_name("sample.pdf")
pdf = canvas.Canvas(str(output), pagesize=letter)
pdf.drawString(48, 740, "Synthetic support policy - page 1")
pdf.drawString(48, 700, "Customers may return a product within 30 days after purchase.")
pdf.drawString(48, 670, "Support replies to email requests within two business days.")
pdf.showPage()
pdf.drawString(48, 740, "Synthetic support policy - page 2")
pdf.drawString(48, 700, "Enterprise customers must request a signed deletion receipt.")
pdf.save()
print(output)
