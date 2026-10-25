import time
import ollama
from google import genai
from google.genai import types, errors
from dotenv import load_dotenv
from schemas import Offer, CV

load_dotenv()  # keep your own key lines if different

# ---------- Model choice: change ONLY this ----------
PROVIDER = "ollama"                 # "ollama" or "gemini"
OLLAMA_MODEL = "llama3.2:3b"        # or "mistral:7b"
GEMINI_MODEL = "gemini-3.8-flash"

client = genai.Client()


OFFER_RULES = """You extract job offer data into JSON.
Rules:
- Only use information written in the offer. Never invent.
- Skills the offer requires go in required_skills.
- Skills described as "a plus", "ideally", "un plus", "souhaité" go in bonus.
- Write every skill name in lowercase, short name only (e.g. "docker", "sql").
- For each required skill, set level only if the offer states it for that skill; otherwise "unknown".
- When the offer lists tools as examples of ONE requirement (in parentheses, "e.g.", "comme", "ou", "such as"),
  create ONE required skill: name = the first tool, alternatives = the other tools. Otherwise alternatives = [].
- required_language = the language the job requires, not the language the offer is written in.
- If level, contract or required_language is not stated, use "unknown".
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
        format=schema.model_json_schema(),   # structured output: the form as JSON Schema
        options={"temperature": 0},          # same input → (almost) same output
    )
    return schema.model_validate_json(response.message.content)


# ---------- The ONE entry point the rest of the project uses ----------
def call_llm(text: str, rules: str, schema):
    if PROVIDER == "gemini":
        return call_gemini(text, rules, schema)
    elif PROVIDER == "ollama":
        return call_ollama(text, rules, schema)
    else:
        raise ValueError(f"Unknown provider: {PROVIDER}")


def extract_offer(text: str) -> Offer:
    return call_llm(text, OFFER_RULES, Offer)


def extract_cv(text: str) -> CV:
    return call_llm(text, CV_RULES, CV)


if __name__ == "__main__":
    test = "Stage Data Engineer – Rabat. Requis : Python, Docker avancé. Kubernetes est un plus."
    print(f"Provider: {PROVIDER}")
    print(extract_offer(test))