from typing import Literal
from pydantic import BaseModel

# ---------- 1. Forms (Offer now stores a level per skill) ----------
class Skill(BaseModel):
    name: str
    level: Literal["notions", "intermediate", "advanced", "unknown"]

class Offer(BaseModel):
    title: str
    required_skills: list[Skill]
    bonus: list[str]

class CV(BaseModel):
    skills: list[Skill]

# Levels as numbers so Python can compare them
LEVELS = {"notions": 1, "intermediate": 2, "advanced": 3}


# ---------- 2. Rule for ONE skill ----------
def check_skill(req: Skill, cv_skills: dict) -> tuple[str, str]:
    if req.name not in cv_skills:
        return "missing", f"❌ {req.name}: not on your CV"

    cv_level = cv_skills[req.name]

    if cv_level == "unknown":
        if req.level == "unknown":
            return "match", f"✅ {req.name} (⚠️ level not stated on your CV)"
        return "match", f"✅ {req.name} (⚠️ {req.level} required, your level isn't stated)"

    if req.level == "unknown" or LEVELS[cv_level] >= LEVELS[req.level]:
        return "match", f"✅ {req.name}"

    return "partial", f"🟡 {req.name}: {req.level} required, you have {cv_level}"


# ---------- 3. Rule for the whole offer (your thresholds) ----------
def categorize(statuses: list[str]) -> str:
    missing = statuses.count("missing")
    partial = statuses.count("partial")
    if missing == 0 and partial == 0:
        return "🟢 très compatible"
    elif missing <= 1 and partial <= 2:
        return "🟠 compatible avec écarts"
    else:
        return "🔴 peu compatible"


# ---------- 4. Match one offer against the CV ----------
def match(offer: Offer, cv: CV) -> None:
    cv_skills = {s.name: s.level for s in cv.skills}   # {"python": "unknown", ...}

    statuses = []
    print(f"\n=== {offer.title} ===")
    for req in offer.required_skills:
        status, message = check_skill(req, cv_skills)
        statuses.append(status)
        print("  ", message)

    for b in offer.bonus:
        if b in cv_skills:
            print(f"   ➕ bonus: {b}")

    print("  →", categorize(statuses))


# ---------- 5. Hand-written test data ----------
offer = Offer(
    title="Data Engineer",
    required_skills=[
        Skill(name="python", level="unknown"),
        Skill(name="sql", level="unknown"),
        Skill(name="docker", level="intermediate"),
        Skill(name="kubernetes", level="unknown"),
    ],
    bonus=["airflow", "git"],
)

cv = CV(skills=[
    Skill(name="python", level="unknown"),
    Skill(name="sql", level="unknown"),
    Skill(name="docker", level="notions"),
    Skill(name="git", level="unknown"),
])

match(offer, cv)