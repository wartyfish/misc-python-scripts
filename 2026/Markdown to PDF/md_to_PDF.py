from fpdf import FPDF
from pathlib import Path
import re

dest = Path("PDFs")
target = Path(r"C:\Users\Eem\Dropbox\Jamies Vault\01 - Daily\Daily Notes\2026-01-11 Sun.md")

hashtag_pattern = re.compile(r"\n#(\w)")



with open(target, "r", encoding="utf-8") as f:
    text = f.read()

#text = hashtag_pattern.sub(r"\n\\#\1", text)
#print(text)

 
pdf = FPDF()

pdf.add_page()
pdf.write_html(text)
pdf.output(dest / "test3.pdf")