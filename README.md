ADOBE HACKATHON 1A

This project extracts document headings and outlines from PDFs.  
It works for both digital PDFs and scanned PDFs, and it supports multiple languages.  
The output is a structured JSON file with the document title and headings.

Features

- Works on **digital PDFs** (text-based) and **scanned PDFs** using OCR
- Uses an **XGBoost model** to classify each line as TITLE / H1 / H2 / H3 / BODY
- Supports **multiple languages (English, Hindi, Gujarati, Japanese)**
- Generates clean JSON output that can be easily used in other systems

---

Input and Output

- **Input:** Place all PDFs in the `input` folder
- **Output:** The script creates one `.json` output file for each PDF in the `output` folder

Example output:

```json
{
  "title": "Sample Document",
  "outline": [
    { "level": "H1", "text": "Introduction", "page": 1 },
    { "level": "H2", "text": "Methodology", "page": 2 }
  ]
}
```
