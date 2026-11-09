# experiments/embed_demo.py
# Goal: turn texts into vectors with bge-m3 and look at them.

import ollama

MODEL = "bge-m3"

texts = [
    "Docker",
    "I use containers to package and deploy my applications in production",
]

for text in texts:
    result = ollama.embed(model=MODEL, input=text)
    vector = result["embeddings"][0]

    print(f"Text: {text!r}")
    print(f"  Words: {len(text.split())}")
    print(f"  Numbers in vector: {len(vector)}")
    print(f"  First 5 numbers: {[round(x, 3) for x in vector[:5]]}")
    print()