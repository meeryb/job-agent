from typing import Literal
from pydantic import BaseModel, ValidationError
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()
MODEL = "gemini-3.8-flash"
client = genai.Client() 


class Offer(BaseModel):
    title: str
    required_skills: list[str]
    bonus: list[str]
    level: Literal["junior", "mid", "senior", "unknown"]
    contract: Literal["stage", "cdi", "cdd", "freelance", "unknown"]
    location: str
    language: Literal["fr", "en", "unknown"]



OFFER_TEXT = """
Stage PFE – Data Engineer (6 mois) – Rabat
Nous recherchons un(e) étudiant(e) en dernière année d'école d'ingénieur.
Compétences requises : Python, SQL, Docker.
La connaissance de Kubernetes ou d'Airflow est un plus.
Démarrage : février 2027.
"""



RULES = """You extract job offer data into JSON.
Rules:
- Only use information written in the offer. Never invent.
- Skills the offer requires go in required_skills.
- Skills described as "a plus", "ideally", "un plus", "souhaité" go in bonus.
- Write every skill in lowercase, short name only (e.g. "docker", "sql").
- If level, contract or language is not stated, use "unknown".
"""



def extract_offer(text: str) -> Offer:
    response = client.models.generate_content(
        model=MODEL,
        contents=text,
        config=types.GenerateContentConfig(
            system_instruction=RULES,
            response_mime_type="application/json",
            response_schema=Offer,
            automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True),
        ),
    )
    print("RAW REPLY:\n", response.text, "\n")
    return Offer.model_validate_json(response.text)


offer = extract_offer(OFFER_TEXT)
print("Title:        ", offer.title)
print("Required:     ", offer.required_skills)
print("Bonus: ", offer.bonus)
print("Level:        ", offer.level)
print("Contract:     ", offer.contract)



print("\n--- Testing bad data ---")
bad = '{"title": "X", "required_skills": [], "bonus": [], "level": "Junior", "contract": "stage", "location": "Rabat", "language": "fr"}'
try:
    Offer.model_validate_json(bad)
except ValidationError as e:
    print("Rejected!\n", e)