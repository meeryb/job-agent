from extract import call_llm, GROUP_RULES, PROVIDER, OLLAMA_MODEL, GEMINI_MODEL
from schemas import SentenceSkills

# Each sentence + the groups YOU expect (ground truth)
CASES = [
    ("Développement Python (FastAPI ou équivalent)",
     [["python"], ["fastapi"]]),
    ("IA générative : LLMs, RAG, agents (ex : LangChain, LlamaIndex, SDK des fournisseurs de modèles)",
     [["llms"], ["rag"], ["agents", "langchain", "llamaindex", "sdk des fournisseurs de modèles"]]),
    ("Bonnes pratiques logicielles : Git, tests, revue de code, architecture logicielle",
     [["git"], ["tests"], ["revue de code"], ["architecture logicielle"]]),
    ("Notions de cloud et DevOps (Docker, CI/CD, Azure, AWS ou GCP)",
     [["docker"], ["ci/cd"], ["azure", "aws", "gcp"]]),
]

model = OLLAMA_MODEL if PROVIDER == "ollama" else GEMINI_MODEL
print(f"Model: {model}\n")

for sentence, expected in CASES:
    try:
        result = call_llm(sentence, GROUP_RULES, SentenceSkills)
        got = [g.tools for g in result.groups]
    except Exception as e:
        got = f"ERROR: {e.__class__.__name__}"
    print(sentence)
    print("   expected:", expected)
    print("   got:     ", got, "\n")