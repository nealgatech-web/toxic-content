import json
import csv
from collections import Counter

def to_label_id(x):
    """Normalize raw label to {0,1,2} or return None if unknown."""
    if isinstance(x, int):
        if x in (0, 1, 2): return x
        return None
    s = str(x).strip().lower()
    # direct digits
    if s.isdigit():
        v = int(s)
        return v if v in (0, 1, 2) else None
    # common strings
    if s in {"hatespeech", "hate_speech", "hate"}: return 0
    if s in {"normal", "non-toxic", "nontoxic", "neutral"}: return 1
    if s in {"offensive", "abusive"}: return 2
    return None

# Load dataset
with open("dataset.json", "r", encoding="utf-8") as f:
    data = json.load(f)

raw_label_counter = Counter()
norm_label_counter = Counter()
rows = []

for _, content in data.items():
    post_tokens = content.get("post_tokens", [])
    annotators = content.get("annotators", [])

    # Extract raw labels (handles list-of-dicts and dict-of-lists)
    if isinstance(annotators, list):
        raw_labels = [a.get("label") for a in annotators if isinstance(a, dict) and "label" in a]
    elif isinstance(annotators, dict):
        raw_labels = annotators.get("label", [])
    else:
        raw_labels = []

    if not post_tokens or not raw_labels:
        continue

    raw_label_counter.update(raw_labels)

    # Normalize labels to 0/1/2
    labels = [to_label_id(x) for x in raw_labels]
    labels = [x for x in labels if x is not None]
    if not labels:
        continue

    norm_label_counter.update(labels)
    majority_label = Counter(labels).most_common(1)[0][0]

    text_type = "toxic" if majority_label in (0, 2) else "normal"
    text = " ".join(post_tokens)
    rows.append((text_type, text))

# Summaries
print("=== Raw Label Summary (as found in JSON) ===")
for k, v in sorted(raw_label_counter.items(), key=lambda x: str(x[0])):
    print(f"{k!r}: {v:,}")

print("\n=== Normalized Label Summary (0=hate,1=normal,2=offensive) ===")
for k, v in sorted(norm_label_counter.items()):
    meaning = {0: "hatespeech (toxic)", 1: "normal", 2: "offensive (toxic)"}[k]
    print(f"{k}: {v:,} → {meaning}")

print(f"\nTotal examples written: {len(rows):,}")

# Write CSV
with open("hatexplain_binary.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["text_type", "text"])
    writer.writerows(rows)

print("\n✅ CSV file 'hatexplain_binary.csv' created successfully (text_type ∈ {toxic, normal}).")
