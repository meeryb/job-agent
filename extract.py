from google import genai
from google.genai import types
from dotenv import load_dotenv
from schemas import Offer, CV

load_dotenv()  # keep your own key lines if different

MODEL = "gemini-3.8-flash"
client = genai.Client()


OFFER_RULES = """You extract job offer data into JSON.
Rules:
- Only use information written in the offer. Never invent.
- Skills the offer requires go in required_skills.
- Skills described as "a plus", "ideally", "un plus", "souhaité" go in bonus.
- Write every skill name in lowercase, short name only (e.g. "docker", "sql").
- For each required skill, set level only if the offer states it for that skill; otherwise "unknown".
- required_language = the language the job requires, not the language the offer is written in.
- If level, contract or required_language is not stated, use "unknown".
- When the offer lists tools as examples of ONE requirement (in parentheses, "e.g.", "comme", "ou", "such as"), create ONE required skill: name = the first tool, alternatives = the other tools. Otherwise alternatives = [].
"""

CV_RULES = """You extract CV data into JSON.
Rules:
- Only use information written in the CV. Never add a skill that is not written.
- Write every skill name in lowercase, short name only (e.g. "docker", "sql").
- level: use "notions", "intermediate" or "advanced" only if the CV states it. Otherwise "unknown".
- languages: short codes ("fr", "en", "es", "ar").
"""


def call_llm(text: str, rules: str, schema):
    """The ONE place that talks to the model. Switching to Ollama = change only this."""
    response = client.models.generate_content(
        model=MODEL,
        contents=text,
        config=types.GenerateContentConfig(
            system_instruction=rules,
            response_mime_type="application/json",
            response_schema=schema,
            automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True),
        ),
    )
    return schema.model_validate_json(response.text)


def extract_offer(text: str) -> Offer:
    return call_llm(text, OFFER_RULES, Offer)


def extract_cv(text: str) -> CV:
    return call_llm(text, CV_RULES, CV)


if __name__ == "__main__":
    test = "Stage Data Engineer – Rabat. Requis : Python, Docker avancé. Kubernetes est un plus."
    print(extract_offer(test))