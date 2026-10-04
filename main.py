import os
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

system_prompt = """You are a recruiting assistant.
Compare the CV with the job offer.
List matching skills and missing skills. Be objective and brief."""

cv = "Skills: Python, SQL, Power BI, Git."
offer = "Required: Python, SQL, Docker, cloud basics."

response = client.models.generate_content(
    model="gemini-3.8-flash",
    contents=f"CV: {cv}\n\nJob offer: {offer}",
    config=types.GenerateContentConfig(
        system_instruction=system_prompt,
        temperature=0.1,
    ),
)

print(response.text)
print("---")
print("Input tokens:", response.usage_metadata.prompt_token_count)
print("Output tokens:", response.usage_metadata.candidates_token_count)
print("Total tokens:", response.usage_metadata.total_token_count)