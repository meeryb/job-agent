# experiments/similarity_demo.py
# Goal: compute cosine similarity by hand and test our predictions.

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


# 1) Test the code on the small example (we know the answer: 1)
print("Small example [1, 2] vs [2, 4]:", round(cosine([1, 2], [2, 4]), 3))
print()

# 2) Real pairs with bge-m3
pairs = [
    ("Docker", "containers"),
    ("Docker", "cooking pasta"),
    ("Java", "JavaScript"),
]

results = []
for text_a, text_b in pairs:
    score = cosine(embed(text_a), embed(text_b))
    results.append((score, text_a, text_b))

results.sort(reverse=True)  # highest score first

for score, text_a, text_b in results:
    print(f"{score:.3f}  {text_a} vs {text_b}")