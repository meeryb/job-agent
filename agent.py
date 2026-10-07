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

question = "What is the capital of France?"
contents = [types.Content(role="user", parts=[types.Part(text=question)])]

response = client.models.generate_content(model=MODEL, contents=contents, config=config)

if not response.function_calls:
    print("No tool needed:", response.text)
    exit()

call = response.function_calls[0]
print("Model asks for:", call.name, call.args)

result = get_offer(**call.args)
print("Tool result:", result)

contents.append(response.candidates[0].content)
contents.append(types.Content(
    role="user",
    parts=[types.Part.from_function_response(name=call.name, response={"result": result})],
))

final = client.models.generate_content(model=MODEL, contents=contents, config=config)
print("Final answer:", final.text)