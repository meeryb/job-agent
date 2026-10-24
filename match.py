from schemas import Skill, RequiredSkill, Offer, CV

LEVELS = {"notions": 1, "intermediate": 2, "advanced": 3}


def check_skill(req: RequiredSkill, cv_skills: dict) -> tuple[str, str]:
    options = [req.name] + req.alternatives            # e.g. ["chromadb", "faiss"]
    found = [o for o in options if o in cv_skills]     # the ones you have

    if not found:
        return "missing", f"❌ {' / '.join(options)}: not on your CV"

    name = found[0]
    cv_level = cv_skills[name]

    if cv_level == "unknown":
        if req.level == "unknown":
            return "match", f"✅ {name} (⚠️ level not stated on your CV)"
        return "match", f"✅ {name} (⚠️ {req.level} required, your level isn't stated)"

    if req.level == "unknown" or LEVELS[cv_level] >= LEVELS[req.level]:
        return "match", f"✅ {name}"

    return "partial", f"🟡 {name}: {req.level} required, you have {cv_level}"


def categorize(statuses: list[str]) -> str:
    missing = statuses.count("missing")
    partial = statuses.count("partial")
    if missing == 0 and partial == 0:
        return "🟢 très compatible"
    elif missing <= 1 and partial <= 2:
        return "🟠 compatible avec écarts"
    else:
        return "🔴 peu compatible"


def match(offer: Offer, cv: CV) -> dict:
    cv_skills = {s.name: s.level for s in cv.skills}

    messages = []
    missing = []
    partial = []
    for req in offer.required_skills:
        status, message = check_skill(req, cv_skills)
        messages.append(message)
        if status == "missing":
            missing.append(req.name)
        elif status == "partial":
            partial.append(req.name)

    bonus = [b for b in offer.bonus if b in cv_skills]

    statuses = ["missing"] * len(missing) + ["partial"] * len(partial)
    return {
        "title": offer.title,
        "label": categorize(statuses),
        "missing": missing,
        "partial": partial,
        "bonus": bonus,
        "messages": messages,
    }


if __name__ == "__main__":
    offer = Offer(
        title="Data Engineer",
        required_skills=[
            RequiredSkill(name="python", level="unknown", alternatives=[]),
            RequiredSkill(name="sql", level="unknown", alternatives=[]),
            RequiredSkill(name="docker", level="intermediate", alternatives=[]),
            RequiredSkill(name="kubernetes", level="unknown", alternatives=[]),
        ],
        bonus=["airflow", "git"],
        level="unknown", contract="stage", location="Rabat", required_language="unknown",
    )
    cv = CV(
        full_name="Test", languages=["fr"], location="Rabat",
        skills=[
            Skill(name="python", level="unknown"),
            Skill(name="sql", level="unknown"),
            Skill(name="docker", level="notions"),
            Skill(name="git", level="unknown"),
        ],
    )
    print(match(offer, cv))