import json
import csv
from collections import Counter

# Load dataset
with open("dataset.json", "r", encoding="utf-8") as f:
    data = json.load(f)

rows = []

def normalize_label(label):
    """Normalize label to 'hatespeech', 'offensive', or 'normal'."""
    s = str(label).strip().lower()
    if s in {"0", "hate", "hatespeech", "hate_speech"}:
        return "hatespeech"
    if s in {"2", "offensive", "abusive"}:
        return "offensive"
    return "normal"

# Stats
majority_toxic = 0
majority_normal = 0
pure_toxic = 0
pure_normal = 0

for example_id, content in data.items():
    post_tokens = content.get("post_tokens", [])
    if not post_tokens:
        continue

    text1 = " ".join([f'"{t}"' for t in post_tokens])
    text2 = " ".join(post_tokens)
    annotators = content.get("annotators", [])
    if not annotators:
        continue

    # Normalize labels
    labels = [normalize_label(a.get("label")) for a in annotators if "label" in a]
    if not labels:
        continue

    # Determine majority toxicity
    toxic_count = sum(l in ("hatespeech", "offensive") for l in labels)
    normal_count = sum(l == "normal" for l in labels)
    is_toxic = "toxic" if toxic_count > normal_count else "normal"

    # Track stats
    if is_toxic == "toxic":
        majority_toxic += 1
    else:
        majority_normal += 1

    # Check pure label cases
    if all(l in ("hatespeech", "offensive") for l in labels):
        pure_toxic += 1
    elif all(l == "normal" for l in labels):
        pure_normal += 1

    # Flatten row
    flat = [text1, text2, is_toxic]
    for ann in annotators:
        label = normalize_label(ann.get("label"))
        annotator_id = ann.get("annotator_id", "")
        target = ", ".join(ann.get("target", [])) if isinstance(ann.get("target"), list) else ann.get("target", "")
        flat.extend([label, annotator_id, target])

    rows.append(flat)

# Determine header dynamically
max_annotators = max((len(r) - 3) // 3 for r in rows)
header = ["Text1", "Text2", "IsToxic"]
for i in range(1, max_annotators + 1):
    header.extend([f"Label{i}", f"Annotator_id{i}", f"Target{i}"])

# Write CSV
with open("hatexplain_detailed.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(header)
    writer.writerows(rows)

# Print stats
print("\n=== Summary Statistics ===")
print(f"Majority-win Toxic:  {majority_toxic:,}")
print(f"Majority-win Normal: {majority_normal:,}")
print(f"Pure Toxic:          {pure_toxic:,}")
print(f"Pure Normal:         {pure_normal:,}")
print(f"\n✅ Done! Wrote {len(rows):,} rows to hatexplain_detailed.csv")
