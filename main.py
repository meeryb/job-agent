from extract import extract_offer, extract_cv
from match import match


def read_file(path: str) -> str:
    with open(path, encoding="utf-8") as f:
        return f.read()


cv = extract_cv(read_file("cv.txt"))
offer = extract_offer(read_file("offer.txt"))
match(offer, cv)