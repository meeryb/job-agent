from job_agent.schemas import Skill, RequiredSkill, Offer, CV
from job_agent.normalize import normalize, to_options

LEVELS = {"notions": 1, "intermediate": 2, "advanced": 3}


def check_skill(req: RequiredSkill, cv_skills: dict) -> tuple[str, str]:
    options = to_options([req.name] + req.alternatives)
    found = [o for o in options if o in cv_skills]

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
    cv_skills = {normalize(s.name): s.level for s in cv.skills}

    messages = []
    missing = []
    partial = []
    seen = set()                                   # requirements already checked
    for req in offer.required_skills:
        key = to_options([req.name] + req.alternatives)[0]
        if key in seen:
            continue                               # duplicate (e.g. python twice): skip
        seen.add(key)

        status, message = check_skill(req, cv_skills)
        messages.append(message)
        if status == "missing":
            missing.append(key)
        elif status == "partial":
            partial.append(key)

    bonus = [b for b in offer.bonus if normalize(b) in cv_skills]

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
        title="Test normalization",
        required_skills=[
            RequiredSkill(name="api d'ia / llm", level="unknown", alternatives=["conversational ai"]),
            RequiredSkill(name="LLMs", level="unknown", alternatives=[]),
            RequiredSkill(name="python", level="unknown", alternatives=[]),
            RequiredSkill(name="python", level="unknown", alternatives=[]),
        ],
        bonus=[],
        level="unknown", contract="stage", location="Rabat", required_language="unknown",
    )
    cv = CV(
        full_name="Test", languages=["fr"], location="Rabat",
        skills=[Skill(name="llm", level="unknown"), Skill(name="python", level="unknown")],
    )
    print(match(offer, cv))