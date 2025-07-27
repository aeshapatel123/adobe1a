import fitz
import re
import json
import platform
from pathlib import Path
from pdf2image import convert_from_path
import pytesseract
from src.classifier import HeadingClassifier

POPLER_PATH = r"C:\poppler\Library\bin"
classifier = HeadingClassifier("models/heading_classifier.pkl")

def extract_outline(pdf_path, out_path):
    if _is_scanned_pdf(pdf_path):
        lines_data = _extract_with_ocr(pdf_path)
    else:
        lines_data = _extract_with_pymupdf(pdf_path)

    if not lines_data:
        print(f"❌ No text detected in {pdf_path}")
        return

    title = None
    outline = []

    for line in lines_data:
        features = [
            line["font_size"], line["bold"], line["indent"], line["length"], line["numbered"],
            line["is_all_caps"], line["upper_ratio"], line["ends_with_colon"],
            line["word_count"], line["is_page1"]
        ]
        label = classifier.predict(features)

        if label == "BODY":
            continue
        if label == "TITLE" and line["page"] == 1 and not title:
            title = line["text"]
            continue

        outline.append({"level": label, "text": line["text"], "page": line["page"]})

    if not title:
        for i, item in enumerate(outline):
            if item["level"] in ["H1", "H2"]:
                title = item["text"]
                outline.pop(i)
                break

    if not title:
        title = Path(pdf_path).stem

    data = {"title": title, "outline": outline}
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"✅ Output saved: {out_path}")

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
        pages = convert_from_path(pdf_path)

    lines_data = []
    for page_num, image in enumerate(pages, 1):
        text = pytesseract.image_to_string(image, lang="eng+hin+guj+jpn")
        for line in text.split("\n"):
            line = line.strip()
            if not line:
                continue
            lines_data.append({
                "text": line, "page": page_num, "font_size": 12, "bold": 0,
                "italic": 0, "indent": 50,
                "numbered": 1 if re.match(r"^\d+(\.\d+)*\s", line) else 0,
                "length": len(line),
                "is_all_caps": int(line.isupper()),
                "upper_ratio": sum(c.isupper() for c in line) / max(1, len(line)),
                "ends_with_colon": int(line.strip().endswith(":")),
                "word_count": len(line.split()), "is_page1": int(page_num == 1)
            })
    return lines_data
