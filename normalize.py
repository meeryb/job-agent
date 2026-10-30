import json

# ---------- Load the synonym map from the data file ----------
with open("synonyms.json", encoding="utf-8") as f:
    _data = json.load(f)

NO_SPLIT = {n.lower() for n in _data["no_split"]}

# Turn {"official": ["variant1", "variant2"]} into {"variant1": "official", "variant2": "official", "official": "official"}
SYNONYMS = {}
for official, variants in _data["skills"].items():
    SYNONYMS[official] = official
    for v in variants:
        SYNONYMS[v.lower()] = official

def normalize(name: str) -> str:
    """Clean one name, then replace it by its official name if it has one."""
    name = name.strip().lower().replace("_", " ")
    return SYNONYMS.get(name, name)


def to_options(names: list[str]) -> list[str]:
    """Split names on '/', normalize each part, and remove duplicates.
    Names that are known as a whole (like 'ci/cd') are NOT split."""
    options = []
    for raw in names:
        whole = raw.strip().lower()
        if whole in SYNONYMS or whole in NO_SPLIT:
            parts = [whole]
        else:
            parts = raw.split("/")
        for part in parts:
            clean = normalize(part)
            if clean and clean not in options:
                options.append(clean)
    return options


if __name__ == "__main__":
    tests = ["LLMs", "api d'ia / llm", "CI/CD", "Traitement automatique du langage", "K8s", "Python 3.10"]
    for t in tests:
        print(f"{t!r:40} → {to_options([t])}")