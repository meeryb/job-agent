import json
from pathlib import Path
import ollama
from job_agent.extract import extract_offer, OLLAMA_MODEL
from job_agent.match import match
from job_agent.schemas import CV

MAX_STEPS = 6

with open("data/cv.json", encoding="utf-8") as f:
    CV_DATA = CV.model_validate_json(f.read())

_results = {}   # cache for this session: offer file -> match result

ORDER = {"🟢 très compatible": 0, "🟠 compatible avec écarts": 1, "🔴 peu compatible": 2}


# ---------- Helpers (not tools) ----------
def _all_results() -> dict:
    """Extract and match every offer once, then reuse the results."""
    for path in sorted(Path("data/offers").glob("*.txt")):
        if path.name not in _results:
            print(f"   (extracting {path.name}...)")
            offer = extract_offer(path.read_text(encoding="utf-8"))
            _results[path.name] = match(offer, CV_DATA)
    return _results


def _ranked() -> list:
    """All (file, result) pairs, best first: category, then fewest missing, then fewest partial."""
    return sorted(
        _all_results().items(),
        key=lambda kv: (ORDER[kv[1]["label"]], len(kv[1]["missing"]), len(kv[1]["partial"])),
    )


def _to_int(value, default: int) -> int:
    """Turn the LLM's argument into an int. Use the default if it's None or invalid."""
    try:
        return int(value) if value is not None else default
    except (TypeError, ValueError):
        return default


# ---------- Tools (the LLM reads their names and docstrings) ----------
def rank_offers(top_n: int = 10) -> str:
    """Rank ALL job offers by compatibility with the user's CV, best first.
    Use when the user asks for the best offers, the top offers, or which offers fit them.

    Args:
      top_n: how many offers to return
    """
    top_n = _to_int(top_n, 10)
    lines = [
        f"{i}. {r['label']} – {r['title']} ({f})\n   missing: {', '.join(r['missing']) or 'nothing'}"
        for i, (f, r) in enumerate(_ranked()[:top_n], start=1)
    ]
    return "Best offers for you:\n" + "\n".join(lines)


def offer_details(file: str) -> str:
    """Skill-by-skill comparison between the CV and ONE specific offer.
    Use ONLY when the user names one offer (for example "offer7.txt").

    Args:
      file: the offer file name, for example "offer7.txt"
    """
    results = _all_results()
    if not file or file not in results:
        return f"Unknown offer: {file}. Available: {', '.join(sorted(results))}"
    r = results[file]
    return f"{r['label']} – {r['title']}\n" + "\n".join("   " + m for m in r["messages"])


def gap_report(top_n: int = 5, consider_top: int = 30, max_missing: int = 5) -> str:
    """The skills the user should learn first, from the offers closest to the user's profile.
    Already sorted, most important first.
    Use when the user asks what to learn, what to improve, what is missing, or which course to take.

    Args:
      top_n: how many skills to return
      consider_top: how many of the best-ranked offers to analyse
      max_missing: ignore offers with more missing skills than this (too far from the profile)
    """
    top_n = _to_int(top_n, 5)
    consider_top = _to_int(consider_top, 30)
    max_missing = _to_int(max_missing, 5)   # 3 + 2 noise margin measured on llama3.2:3b

    relevant = [r for _, r in _ranked()[:consider_top] if len(r["missing"]) <= max_missing]

    missing, partial = {}, {}
    for r in relevant:
        for s in r["missing"]:
            missing[s] = missing.get(s, 0) + 1
        for s in r["partial"]:
            partial[s] = partial.get(s, 0) + 1

    skills = set(missing) | set(partial)
    best = sorted(skills, key=lambda s: missing.get(s, 0) + partial.get(s, 0), reverse=True)[:top_n]

    if not best:
        return "No gaps found in the offers close to your profile. 🎉"

    lines = [
        f"{i}. {s}: needed in {missing.get(s, 0) + partial.get(s, 0)} of {len(relevant)} close offers "
        f"({missing.get(s, 0)} missing, {partial.get(s, 0)} partial)"
        for i, s in enumerate(best, start=1)
    ]
    return "Learn in this order:\n" + "\n".join(lines)


TOOLS = {"rank_offers": rank_offers, "offer_details": offer_details, "gap_report": gap_report}

SYSTEM = """You are a job-search assistant for one candidate.
Rules:
- Answer ONLY from tool results. Never invent offers, skills or categories.
- Never change the category a tool returned.
- Never say you did something (searched online, applied, sent) unless a tool did it.
- If the request is unclear or missing information, ask the user a short question first.
- When a tool gives a ranked list, keep its order and its numbers.
- Answer briefly, in the user's language."""


# ---------- The agent loop: the LLM routes, Python answers ----------
def run_agent(messages: list) -> str:
    for step in range(MAX_STEPS):
        response = ollama.chat(
            model=OLLAMA_MODEL,
            messages=messages,
            tools=list(TOOLS.values()),          # Ollama builds the tool cards from the functions
            options={"temperature": 0},
        )
        msg = response.message
        messages.append(msg)

        if not msg.tool_calls:                   # no tool: the LLM answers or asks a question
            return msg.content

        answers = []
        for call in msg.tool_calls:
            name = call.function.name
            args = call.function.arguments or {}
            print(f"   🔧 {name}({args})")
            func = TOOLS.get(name)
            try:
                result = func(**args) if func else f"Unknown tool: {name}"
            except Exception as e:               # a bad argument must not crash the agent
                result = f"Tool error in {name}: {e}"
            messages.append({"role": "tool", "content": result, "tool_name": name})
            answers.append(result)

        final = "\n\n".join(answers)
        messages.append({"role": "assistant", "content": final})   # keep what the user saw
        return final                                                # return direct: Python answers

    return "Stopped: too many steps."


if __name__ == "__main__":
    messages = [{"role": "system", "content": SYSTEM}]
    print("Ask your agent (type 'quit' to stop).")
    while True:
        question = input("\nYou: ")
        if question.strip().lower() == "quit":
            break
        messages.append({"role": "user", "content": question})
        print("\nAgent:", run_agent(messages))