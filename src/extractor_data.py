import fitz
import re
import csv
import platform
from pathlib import Path
from pdf2image import convert_from_path
import pytesseract

POPLER_PATH = r"C:\poppler\Library\bin"  # Windows Poppler path

def extract_outline(pdf_path):
    if _is_scanned_pdf(pdf_path):
        lines_data = _extract_with_ocr(pdf_path)
    else:
        lines_data = _extract_with_pymupdf(pdf_path)

    if not lines_data:
        print(f"❌ No text detected in {pdf_path}")
        return

    save_training_data(lines_data, Path(pdf_path).name)

def _is_scanned_pdf(pdf_path):
    doc = fitz.open(pdf_path)
    return all(page.get_text().strip() == "" for page in doc)

def _extract_with_pymupdf(pdf_path):
    doc = fitz.open(pdf_path)
    lines_data = []
    for page_num, page in enumerate(doc, 1):
        for block in page.get_text("dict")["blocks"]:
            for line in block.get("lines", []):
                text = " ".join([s["text"] for s in line["spans"]]).strip()
                if not text:
                    continue
                span = line["spans"][0]
                font_size = span["size"]
                font_name = span["font"]
                indent = line["bbox"][0]
                bold = 1 if "Bold" in font_name else 0
                numbered = 1 if re.match(r"^\d+(\.\d+)*\s", text) else 0

                lines_data.append({
                    "text": text, "page": page_num, "font_size": font_size,
                    "bold": bold, "italic": 1 if "Italic" in font_name else 0,
                    "indent": indent, "numbered": numbered, "length": len(text),
                    "is_all_caps": int(text.isupper()),
                    "upper_ratio": sum(c.isupper() for c in text) / max(1, len(text)),
                    "ends_with_colon": int(text.strip().endswith(":")),
                    "word_count": len(text.split()), "is_page1": int(page_num == 1)
                })
    return lines_data

def _extract_with_ocr(pdf_path):
    if platform.system() == "Windows":
        pages = convert_from_path(pdf_path, poppler_path=POPLER_PATH)
    else:
        pages = convert_from_path(pdf_path)  # Docker/Linux

    lines_data = []
    for page_num, image in enumerate(pages, 1):
        text = pytesseract.image_to_string(image, lang="eng+hin+guj+jpn")
        for line in text.split("\n"):
            line = line.strip()
            if not line:
                continue
            lines_data.append({
                "text": line, "page": page_num, "font_size": 12,
                "bold": 0, "italic": 0, "indent": 50,
                "numbered": 1 if re.match(r"^\d+(\.\d+)*\s", line) else 0,
                "length": len(line),
                "is_all_caps": int(line.isupper()),
                "upper_ratio": sum(c.isupper() for c in line) / max(1, len(line)),
                "ends_with_colon": int(line.strip().endswith(":")),
                "word_count": len(line.split()), "is_page1": int(page_num == 1)
            })
    return lines_data

def save_training_data(lines_data, pdf_name):
    file_path = Path("training_data.csv")
    existing_rows = set()

    if file_path.exists():
        with open(file_path, "r", encoding="utf-8") as f:
            next(f, None)
            for line in f:
                existing_rows.add(line.strip().lower())

    write_header = not file_path.exists() or file_path.stat().st_size == 0
    with open(file_path, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if write_header:
            writer.writerow([
                "font_size", "bold", "indent", "length", "numbered",
                "is_all_caps", "upper_ratio", "ends_with_colon",
                "word_count", "is_page1", "pdf_name", "text", "label"
            ])
        for line in lines_data:
            row = [
                line["font_size"], line["bold"], line["indent"], line["length"], line["numbered"],
                line["is_all_caps"], line["upper_ratio"], line["ends_with_colon"],
                line["word_count"], line["is_page1"], pdf_name, line["text"], ""
            ]
            row_str = ",".join([str(x).strip().lower() for x in row])
            if row_str not in existing_rows:
                writer.writerow(row)
                existing_rows.add(row_str)
