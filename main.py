from pathlib import Path
from extract import extract_offer, extract_cv
from match import match
from schemas import CV


def read_file(path) -> str:
    with open(path, encoding="utf-8") as f:
        return f.read()


def sort_key(result: dict) -> tuple:
    return (len(result["missing"]), len(result["partial"]))


# 1. CV: extracted once
cv = CV.model_validate_json(read_file("cv.json"))

# 2. Every offer in the offers/ folder
results = []
for path in sorted(Path("offers").glob("*.txt")):
    print(f"Extracting {path.name}...")
    offer = extract_offer(read_file(path))
    results.append(match(offer, cv))

# 3. Ranking: fewest gaps first
print("\n========== RANKING ==========")
for r in sorted(results, key=sort_key):
    print(f"\n{r['label']}  –  {r['title']}")
    for m in r["messages"]:
        print("   ", m)
    for b in r["bonus"]:
        print(f"    ➕ bonus: {b}")

# 4. Gap report: which skills are missing most often
gap_counts = {}
for r in results:
    for skill in r["missing"] + r["partial"]:
        gap_counts[skill] = gap_counts.get(skill, 0) + 1

print("\n========== GAPS ==========")
for skill, count in sorted(gap_counts.items(), key=lambda x: x[1], reverse=True):
    print(f"   {skill}: {count} of {len(results)} offers")