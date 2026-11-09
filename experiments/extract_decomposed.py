import time
import ollama
from google import genai
from google.genai import types, errors
from dotenv import load_dotenv
from job_agent.schemas import Offer, CV, RequiredSkill, OfferSplit, SentenceSkills

load_dotenv()

# ---------- Model choice: change ONLY this ----------
PROVIDER = "ollama"                 # "ollama" or "gemini"
OLLAMA_MODEL = "llama3.2:3b"
GEMINI_MODEL = "gemini-3.8-flash"

client = genai.Client()


# ---------- Step 1: split the offer into requirement sentences ----------
SPLIT_RULES = """You split a job offer into its requirement sentences.
Rules:
- Copy each requirement sentence or bullet EXACTLY as written. Do not rewrite or translate.
- Only keep sentences about skills, tools, knowledge or experience the candidate needs.
  Skip sentences about the company, the missions, the benefits.
- If one line mixes a requirement and a "plus" (e.g. "Python ; TypeScript est un plus"),
  split it into two sentences.
- kind = "bonus" if the sentence says "un plus", "a plus", "souhaité", "idéalement", "nice to have".
  Otherwise kind = "required".
- required_language = the language the job requires, not the language the offer is written in.
- If level, contract or required_language is not stated, use "unknown".
"""

# ---------- Step 2: group the skills of ONE sentence ----------
GROUP_RULES = """You receive ONE requirement sentence from a job offer. List the skills it asks for.
Rules:
- Only use skills written in the sentence. Never add skills.
- By default, each skill is its own group.
- "ou" / "or" makes alternatives ONLY between items of the SAME KIND (e.g. several cloud providers).
  Items of a different kind in the same list stay in separate groups.
- "SKILL (ex : A, B)" or "SKILL (e.g. A, B)": the skill and its examples form ONE group.
- "X ou équivalent": X is alone. "équivalent" is not a skill.
- A skill written outside the parentheses is its own group.
- Do not put connector words ("ou", "or", "ex", "e.g.", "comme", "équivalent", "etc.") in a group.
- Write names in lowercase, short, in the language of the sentence. Do not translate.
- level: "notions", "intermediate" or "advanced" only if the sentence states it. Otherwise "unknown".
"""

CV_RULES = """You extract CV data into JSON.
Rules:
- Only use information written in the CV. Never add a skill that is not written.
- Write every skill name in lowercase, short name only (e.g. "docker", "sql").
- level: use "notions", "intermediate" or "advanced" only if the CV states it. Otherwise "unknown".
- languages: short codes ("fr", "en", "es", "ar").
"""


# ---------- Provider 1: Gemini (cloud) ----------
def call_gemini(text: str, rules: str, schema, max_retries: int = 5):
    for attempt in range(max_retries):
        try:
            response = client.models.generate_content(
                model=GEMINI_MODEL,
                contents=text,
                config=types.GenerateContentConfig(
                    system_instruction=rules,
                    response_mime_type="application/json",
                    response_schema=schema,
                    automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True),
                ),
            )
            return schema.model_validate_json(response.text)
        except errors.APIError as e:
            if e.code in (429, 503) and attempt < max_retries - 1:
                wait = 5 * 2 ** attempt
                print(f"   ⚠️ error {e.code}, retrying in {wait}s...")
                time.sleep(wait)
            else:
                raise


# ---------- Provider 2: Ollama (local) ----------
def call_ollama(text: str, rules: str, schema):
    response = ollama.chat(
        model=OLLAMA_MODEL,
        messages=[
            {"role": "system", "content": rules},
            {"role": "user", "content": text},
        ],
        format=schema.model_json_schema(),
        options={"temperature": 0},
    )
    return schema.model_validate_json(response.message.content)


def call_llm(text: str, rules: str, schema):
    if PROVIDER == "gemini":
        return call_gemini(text, rules, schema)
    elif PROVIDER == "ollama":
        return call_ollama(text, rules, schema)
    else:
        raise ValueError(f"Unknown provider: {PROVIDER}")


# ---------- The chain: step 1 → step 2 (per sentence) → one Offer ----------
def extract_offer(text: str, verbose: bool = False) -> Offer:
    split = call_llm(text, SPLIT_RULES, OfferSplit)              # step 1: 1 call

    required = []
    bonus = []
    for req in split.requirements:
        result = call_llm(req.text, GROUP_RULES, SentenceSkills)  # step 2: 1 call per sentence
        if verbose:
            print(f"   [{req.kind}] {req.text}")
            print(f"      → {[g.tools for g in result.groups]}")

        for g in result.groups:
            if not g.tools:
                continue
            if req.kind == "required":
                required.append(RequiredSkill(name=g.tools[0], level=g.level,
                                              alternatives=g.tools[1:]))
            else:
                bonus.extend(g.tools)

    return Offer(
        title=split.title,
        required_skills=required,
        bonus=bonus,
        level=split.level,
        contract=split.contract,
        location=split.location,
        required_language=split.required_language,
    )


def extract_cv(text: str) -> CV:
    return call_llm(text, CV_RULES, CV)


if __name__ == "__main__":
    print(f"Provider: {PROVIDER}  |  Model: {OLLAMA_MODEL if PROVIDER == 'ollama' else GEMINI_MODEL}\n")
    with open("offers/offer14.txt", encoding="utf-8") as f:
        offer = extract_offer(f.read(), verbose=True)
    print("\nRequired:")
    for r in offer.required_skills:
        print(f"   {r.name}  (alternatives: {r.alternatives})")
    print("Bonus:", offer.bonus)