from pathlib import Path
from src.extractor_predict import extract_outline

input_dir = Path("/app/input")
output_dir = Path("/app/output")
output_dir.mkdir(parents=True, exist_ok=True)

for pdf in input_dir.glob("*.pdf"):
    out_path = output_dir / f"{pdf.stem}.json"
    extract_outline(str(pdf), str(out_path))

print("✅ Processing complete. Outputs in /app/output/")
