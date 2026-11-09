import csv
from job_agent.extract import extract_offer, extract_cv
from job_agent.match import match
from job_agent.schemas import CV

# The agent's labels → the same words as in labels.csv
COLOR = {
    "🟢 très compatible": "green",
    "🟠 compatible avec écarts": "orange",
    "🔴 peu compatible": "red",
}


def read_file(path: str) -> str:
    with open(path, encoding="utf-8") as f:
        return f.read()


# 1. Your labels (ground truth)
with open("evals/labels.csv", encoding="utf-8") as f:
    labels = list(csv.DictReader(f))

# 2. Run the agent on each labeled offer
cv = CV.model_validate_json(read_file("data/cv.json"))
rows = []
for row in labels:
    file = row["file"].strip()
    you = row["label"].strip().lower()
    print(f"Running {file}...")

    offer = extract_offer(read_file(f"data/offers/{file}"))
    result = match(offer, cv)
    agent = COLOR[result["label"]]

    rows.append({
        "file": file,
        "you": you,
        "agent": agent,
        "same": agent == you,
        "reason": row["reason"],
        "messages": result["messages"],
    })

# 3. Score
correct = sum(r["same"] for r in rows)
print(f"\n========== SCORE: {correct}/{len(rows)} ==========\n")
for r in rows:
    mark = "✅" if r["same"] else "❌"
    print(f"{mark} {r['file']:<12} you: {r['you']:<7} agent: {r['agent']}")

# 4. Disagreements (for error analysis)
print("\n========== DISAGREEMENTS ==========")
for r in rows:
    if not r["same"]:
        print(f"\n❌ {r['file']}  (you: {r['you']}, agent: {r['agent']})")
        print(f"   your reason: {r['reason']}")
        for m in r["messages"]:
            print("   ", m)