from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()
client = genai.Client()
MODEL = "gemini-3.8-flash"

OFFERS = {
    42: "Junior Data Engineer. Required: Python, SQL, Docker.",
    43: "AI Intern. Required: Python, LLM APIs, Git.",
}
CV = "Candidate: Sara. Skills: Python, Git, SQL. Education: engineering student."
COURSES = {
    "docker": ["Docker for Beginners (4h)", "Containers in Practice (6h)"],
    "llm apis": ["Build with LLM APIs (5h)"],
    "python": ["Python Advanced (8h)"],
}

def get_offer(offer_id: int) -> str:
    """Returns the full text of a job offer, given its ID."""
    return OFFERS.get(int(offer_id), "Offer not found.")

def read_cv() -> str:
    """Returns the candidate's CV text."""
    return CV

def search_courses(skill: str) -> list[str]:
    """Finds courses in our catalog that teach one given skill."""
    return COURSES.get(skill.lower(), [])

config = types.GenerateContentConfig(
    tools=[get_offer, read_cv, search_courses],
    temperature=0.1,
)

response = client.models.generate_content(
    model=MODEL,
    contents="Does my CV match offer 42? If skills are missing, find courses for them.",
    config=config,
)

print(response.text)
print("\nHidden history length:", len(response.automatic_function_calling_history))