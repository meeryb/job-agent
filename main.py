from pathlib import Path
from job_agent.extract import extract_offer, extract_cv
from job_agent.match import match
from job_agent.schemas import CV


def read_file(path) -> str:
    with open(path, encoding="utf-8") as f:
        return f.read()


def sort_key(result: dict) -> tuple:
    return (len(result["missing"]), len(result["partial"]))


# 1. CV: extracted once
cv = CV.model_validate_json(read_file("data/cv.json"))

# 2. Every offer in the offers/ folder
results = []
for path in sorted(Path("data/offers").glob("*.txt")):
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

# 4. Gap report: missing and partial counted separately
missing_counts = {}
partial_counts = {}
for r in results:
    for skill in r["missing"]:
        missing_counts[skill] = missing_counts.get(skill, 0) + 1
    for skill in r["partial"]:
        partial_counts[skill] = partial_counts.get(skill, 0) + 1


def total(skill: str) -> int:
    return missing_counts.get(skill, 0) + partial_counts.get(skill, 0)


all_skills = set(missing_counts) | set(partial_counts)

print("\n========== GAPS ==========")
for skill in sorted(all_skills, key=total, reverse=True):
    m = missing_counts.get(skill, 0)
    p = partial_counts.get(skill, 0)
    print(f"   {skill}: {m + p} of {len(results)} offers  ({m} missing, {p} partial)")