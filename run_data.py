from pathlib import Path
from src.extractor_data import extract_outline

input_dir = Path("input")

for pdf in input_dir.glob("*.pdf"):
    extract_outline(str(pdf))

print("✅ training_data.csv updated! Label the 'label' column manually.")
