# evals/retrieval_eval.py
# Goal: measure top-k search on a labeled test set (labels written BEFORE running).

import csv

from experiments.topk_demo import load_cv_skills, build_index, search

PAIRS_PATH = "evals/skill_pairs.csv"


def load_pairs(path=PAIRS_PATH):
    """Read the test set: list of (query, expected). expected = a CV skill or 'none'."""
    with open(path, encoding="utf-8") as f:
        return [(row["query"], row["expected"]) for row in csv.DictReader(f)]


def full_ranking(query, index):
    """All CV skills sorted by score, best first: list of (score, skill)."""
    return search(query, index, k=len(index))


if __name__ == "__main__":
    pairs = load_pairs()
    index = build_index(load_cv_skills())

    match_pairs = [(q, e) for q, e in pairs if e != "none"]
    none_pairs = [(q, e) for q, e in pairs if e == "none"]

    # 1) Queries that SHOULD find a CV skill
    print("SHOULD MATCH")
    print(f"  {'query':<32}{'expected':<14}{'rank':>5}{'score':>8}   top-1")
    hit1 = hit3 = 0
    correct_scores = []  # (score, query, expected)
    for query, expected in match_pairs:
        ranking = full_ranking(query, index)
        skills_in_order = [skill for _, skill in ranking]
        rank = skills_in_order.index(expected) + 1
        score = ranking[rank - 1][0]
        correct_scores.append((score, query, expected))
        if rank == 1:
            hit1 += 1
        if rank <= 3:
            hit3 += 1
        top_skill = ranking[0][1]
        print(f"  {query:<32}{expected:<14}{rank:>5}{score:>8.3f}   {top_skill}")
    print(f"  Hit@1: {hit1}/{len(match_pairs)}   Hit@3: {hit3}/{len(match_pairs)}\n")

    # 2) Queries that should find NOTHING
    print("SHOULD FIND NOTHING")
    print(f"  {'query':<32}{'top-1':<14}{'score':>8}")
    none_scores = []  # (score, query, top skill)
    for query, _ in none_pairs:
        top_score, top_skill = full_ranking(query, index)[0]
        none_scores.append((top_score, query, top_skill))
        print(f"  {query:<32}{top_skill:<14}{top_score:>8.3f}")
    print()

    # 3) Can one threshold separate them?
    low = min(correct_scores)
    high = max(none_scores)
    print("THRESHOLD CHECK")
    print(f"  Lowest correct score:  {low[0]:.3f}  ({low[1]} -> {low[2]})")
    print(f"  Highest 'none' score:  {high[0]:.3f}  ({high[1]} -> {high[2]})")
    if high[0] < low[0]:
        print(f"  OK: a threshold exists between {high[0]:.3f} and {low[0]:.3f}")
    else:
        print("  OVERLAP: no single threshold separates them")