from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()
client = genai.Client()
MODEL = "gemini-3.8-flash"
MAX_STEPS = 5

# ---------- Fake data ----------
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

# ---------- Tools (Python functions) ----------
def get_offer(offer_id):
    return OFFERS.get(int(offer_id), "Offer not found.")

def read_cv():
    return CV

def search_courses(skill):
    return COURSES.get(skill.lower(), [])

TOOLS = {
    "get_offer": get_offer,
    "read_cv": read_cv,
    "search_courses": search_courses,
}

# ---------- Tool cards (what Gemini sees) ----------
get_offer_decl = types.FunctionDeclaration(
    name="get_offer",
    description="Returns the full text of a job offer, given its ID.",
    parameters=types.Schema(
        type="OBJECT",
        properties={"offer_id": types.Schema(type="INTEGER", description="The offer's ID number")},
        required=["offer_id"],
    ),
)

read_cv_decl = types.FunctionDeclaration(
    name="read_cv",
    description="Returns the candidate's CV text.",
)

search_courses_decl = types.FunctionDeclaration(
    name="search_courses",
    description="Finds courses in our catalog that teach one given skill.",
    parameters=types.Schema(
        type="OBJECT",
        properties={"skill": types.Schema(type="STRING", description="One skill, e.g. 'Docker'")},
        required=["skill"],
    ),
)

config = types.GenerateContentConfig(
    tools=[types.Tool(function_declarations=[get_offer_decl, read_cv_decl, search_courses_decl])],
    temperature=0.1,
)

# ---------- Agent loop (one question) ----------
def run_agent(contents):
    for step in range(MAX_STEPS):
        response = client.models.generate_content(model=MODEL, contents=contents, config=config)

        contents.append(response.candidates[0].content)

        if not response.function_calls:
            return response.text

        result_parts = []
        for call in response.function_calls:
            print(f"  Step {step + 1} → {call.name} {call.args}")
            func = TOOLS.get(call.name)
            result = func(**call.args) if func else f"Unknown tool: {call.name}"
            result_parts.append(types.Part.from_function_response(name=call.name, response={"result": result}))

        contents.append(types.Content(role="user", parts=result_parts))

    return "Stopped: max steps reached."

# ---------- Chat (many questions, shared memory) ----------
contents = []
print("Job agent ready. Type 'quit' to exit.")

while True:
    question = input("\nYou: ")
    if question.lower() == "quit":
        break
    contents.append(types.Content(role="user", parts=[types.Part(text=question)]))
    answer = run_agent(contents)
    print("Agent:", answer)