from pathlib import Path

input_file = Path("training_data.csv")
output_file = Path("training_data_clean.csv")

if not input_file.exists():
    raise FileNotFoundError("❌ training_data.csv not found!")

new_lines = []
with open(input_file, "r", encoding="utf-8") as f:
    for line in f:
        parts = [p.strip() for p in line.strip().split(",")]
        if len(parts) == 8:
            # OLD row (8 columns)
            font_size, bold, indent, length, numbered, pdf_name, text, label = parts

            is_all_caps = int(text.isupper())
            upper_ratio = sum(c.isupper() for c in text) / max(1, len(text))
            ends_with_colon = int(text.strip().endswith(":"))
            word_count = len(text.split())
            is_page1 = 0

            new_parts = [
                font_size, bold, indent, length, numbered,
                str(is_all_caps), str(upper_ratio), str(ends_with_colon),
                str(word_count), str(is_page1),
                pdf_name, text, label
            ]
            new_lines.append(",".join(new_parts))
        elif len(parts) == 13:
            # Already new format → keep as is
            new_lines.append(",".join(parts))
        else:
            print(f"⚠️ Skipped invalid row ({len(parts)} columns): {line}")

# Write clean file
with open(output_file, "w", encoding="utf-8") as f:
    # Write header
    f.write("font_size,bold,indent,length,numbered,is_all_caps,upper_ratio,ends_with_colon,word_count,is_page1,pdf_name,text,label\n")
    for row in new_lines:
        f.write(row + "\n")

print(f"✅ Cleaned dataset saved as {output_file}")
print(f"➡️ Total rows: {len(new_lines)}")
