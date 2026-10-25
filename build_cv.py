from extract import extract_cv

with open("cv.txt", encoding="utf-8") as f:
    cv = extract_cv(f.read())

with open("cv.json", "w", encoding="utf-8") as f:
    f.write(cv.model_dump_json(indent=2))

print(f"Saved cv.json with {len(cv.skills)} skills. Now check it by hand!")