# evals/synonym_eval.py
# Goal: BASELINE. Run the 20 labeled queries through the current synonym map.

from job_agent.normalize import SYNONYMS, normalize
from experiments.topk_demo import load_cv_skills
from evals.retrieval_eval import load_pairs


def find_in_cv(query, cv_skills):
    """Return the CV skill with the same official name as the query, or 'none'."""
    target = normalize(query)
    for skill in cv_skills:
        if normalize(skill) == target:
            return skill
    return "none"


if __name__ == "__main__":
    print(f"Synonym map: {len(SYNONYMS)} entries\n")

    cv_skills = load_cv_skills()
    pairs = load_pairs()

    print(f"  {'query':<32}{'expected':<14}{'found':<14}result")
    ok_match = ok_none = n_match = n_none = 0

    for query, expected in pairs:
        found = find_in_cv(query, cv_skills)

        if found == expected:
            result = "OK"
        elif found == "none":
            result = "MISSED"   # should have found a skill, found nothing
        else:
            result = "WRONG"    # found a skill it should not

        if expected == "none":
            n_none += 1
            if result == "OK":
                ok_none += 1
        else:
            n_match += 1
            if result == "OK":
                ok_match += 1

        print(f"  {query:<32}{expected:<14}{found:<14}{result}")

    print(f"\n  Should match:        {ok_match}/{n_match}")
    print(f"  Should find nothing: {ok_none}/{n_none}")