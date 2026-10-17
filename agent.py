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

def get_offer(offer_id):
    return OFFERS.get(int(offer_id), "Offer not found.")


get_offer_decl = types.FunctionDeclaration(
    name="get_offer",
    description="Returns the full text of a job offer, given its ID.",
    parameters=types.Schema(
        type="OBJECT",
        properties={
            "offer_id": types.Schema(type="INTEGER", description="The offer's ID number"),
        },
        required=["offer_id"],
    ),
)
config = types.GenerateContentConfig(
    tools=[types.Tool(function_declarations=[get_offer_decl])],
    temperature=0.1,
)

MAX_STEPS = 5

question = "Compare offers 42 and 43. Which one fits a candidate with Python and Git better?"
contents = [types.Content(role="user", parts=[types.Part(text=question)])]

for step in range(MAX_STEPS):
    response = client.models.generate_content(model=MODEL, contents=contents, config=config)

    if not response.function_calls:
        print("Final answer:", response.text)
        break

    contents.append(response.candidates[0].content)

    result_parts = []
    for call in response.function_calls:
        print(f"Step {step + 1} → {call.name} {call.args}")
        result = get_offer(**call.args)
        result_parts.append(types.Part.from_function_response(name=call.name, response={"result": result}))

    contents.append(types.Content(role="user", parts=result_parts))
else:
    print("Stopped: max steps reached.")