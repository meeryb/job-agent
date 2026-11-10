# experiments/topk_demo.py
# Goal: top-k search by hand. Query = an offer skill, index = my CV skills.

import json
import math
import ollama

# ---- Experiment settings (change ONE at a time) ----
MODEL = "qwen3-embedding:0.6b"   # before: "bge-m3"
USE_INSTRUCTION = False          # Run A: False   |   Run B: True
INSTRUCTION = ("Given a skill required in a job offer, retrieve the CV skill "
               "that is the same skill or an accepted equivalent")

CV_PATH = "data/cv.json"
K = 3              # how many results we keep
MIN_SCORE = 0.45   # below this, a result is junk


def load_cv_skills(path=CV_PATH):
    """Read cv.json and return the list of skill names."""
    with open(path, encoding="utf-8") as f:
        cv = json.load(f)
    return [skill["name"] for skill in cv["skills"]]


def embed_many(texts):
    """Turn a list of texts into a list of vectors (one call = a batch)."""
    result = ollama.embed(model=MODEL, input=texts)
    return result["embeddings"]


def cosine(a, b):
    """Cosine similarity between two vectors."""
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = math.sqrt(sum(x * x for x in a))
    norm_b = math.sqrt(sum(x * x for x in b))
    return dot / (norm_a * norm_b)


def build_index(skills):
    """Embed all CV skills ONCE. No instruction here: they are documents."""
    print(f"Model: {MODEL} | Instruction: {'yes' if USE_INSTRUCTION else 'no'}")
    vectors = embed_many(skills)
    return list(zip(skills, vectors))


def search(query, index, k=K):
    """Compare the query with every item, sort, keep the top k."""
    if USE_INSTRUCTION:
        query = f"Instruct: {INSTRUCTION}\nQuery: {query}"
    query_vector = embed_many([query])[0]
    scored = [(cosine(query_vector, vector), skill) for skill, vector in index]
    scored.sort(reverse=True)
    return scored[:k]


if __name__ == "__main__":
    skills = load_cv_skills()
    print(f"Building index: {len(skills)} CV skills...")
    index = build_index(skills)
    print("Done.\n")

    queries = ["containers", "Java", "apprentissage automatique", "cooking pasta"]

    for query in queries:
        print(f"Query: {query}")
        for score, skill in search(query, index):
            flag = "" if score >= MIN_SCORE else "   (below minimum → dropped)"
            print(f"  {score:.3f}  {skill}{flag}")
        print()