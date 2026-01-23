from fpdf import FPDF
from pathlib import Path
from bs4 import BeautifulSoup
import re, markdown

dest = Path("PDFs")
target = Path(r"C:\Users\Eem\Dropbox\Jamies Vault\01 - Daily\Daily Notes\2026\2026-01-11 Sun.md")

class MarkdownPDF(FPDF):
    def header(self):
        self.set_font("Helvetica", "B", 24)
        self.cell(0, 10, "Diary Entry 260111", ln=True, align="C")
        self.ln(5)

pdf = MarkdownPDF()
pdf.set_auto_page_break(True, 15)
pdf.add_page()

with open(target, encoding="utf-8") as f:
    html = markdown.markdown(f.read())

soup = BeautifulSoup(html, "html.parser")

for tag in soup:
    if tag.name == "h2":
        pdf.set_font("Helvetica", "B", 24)
        pdf.ln(5)
        pdf.multi_cell(0, 12, tag.text)
    elif tag.name == "h3":
        pdf.set_font("Helvetica", "B", 18)
        pdf.ln(4)
        pdf.multi_cell(0, 10, tag.text)
    elif tag.name == "h4":
        pdf.set_font("Helvetica", "B", 14)
        pdf.ln(4)
        pdf.multi_cell(0, 8, tag.text)
    elif tag.name == "p":
        pdf.set_font("Helvetica", size=12)
        pdf.set_x(pdf.l_margin)
        pdf.multi_cell(0, 8, tag.text)
        pdf.ln(2)

pdf.output(dest / "test4.pdf")