# experiments/similarity_demo.py
# Goal: compute cosine similarity by hand and test our predictions.
# Experiment 2: does adding context change the scores?

import math
import ollama

MODEL = "bge-m3"


def embed(text):
    """Turn one text into a vector (list of 1024 numbers)."""
    result = ollama.embed(model=MODEL, input=text)
    return result["embeddings"][0]


def dot(a, b):
    """Multiply number by number, then add everything."""
    return sum(x * y for x, y in zip(a, b))


def norm(a):
    """Length of the arrow: square root of the sum of squares."""
    return math.sqrt(sum(x * x for x in a))


def cosine(a, b):
    """Cosine similarity: dot product divided by the two lengths."""
    return dot(a, b) / (norm(a) * norm(b))


def score(text_a, text_b):
    """Cosine similarity between two texts."""
    return cosine(embed(text_a), embed(text_b))


# Each test: (word A, word B, A in a sentence, B in a sentence)
tests = [
    ("Java", "JavaScript",
     "Backend development in Java with Spring Boot",
     "Frontend development in JavaScript with React"),
    ("Docker", "containers",
     "Deploy the application with Docker",
     "Experience with containers for deployment"),
    ("Docker", "cooking pasta",
     "Deploy the application with Docker",
     "Cooking pasta for a family dinner"),
]

print(f"{'Pair':<28}{'Alone':>8}{'Context':>10}")
for a, b, ctx_a, ctx_b in tests:
    alone = score(a, b)
    with_context = score(ctx_a, ctx_b)
    print(f"{a + ' vs ' + b:<28}{alone:>8.3f}{with_context:>10.3f}")