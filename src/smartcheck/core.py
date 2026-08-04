"""SmartCheck core — flag confident-but-wrong AI output."""
import re
from .models import Issue, Verdict

# A quantitative claim: a 3+ digit run, a percentage (e.g. 20%, 7.2 %), or a
# number paired with a magnitude word (e.g. 1.6 million). Percentages and
# magnitudes are the most common way statistics are stated, so limiting this to
# 3+ digit runs missed the majority of real unsourced claims.
_NUM = re.compile(
    r"\b\d{3,}\b"
    r"|\b\d+(?:\.\d+)?\s?%"
    r"|\b\d+(?:\.\d+)?\s*(?:hundred|thousand|million|billion|trillion)\b",
    re.I)


def check(answer: str, sources: str = "") -> Verdict:
    issues = []
    if _NUM.search(answer) and not sources:
        issues.append(Issue("CHECK-UNSOURCED-NUMBER", 0.6, "numeric claim with no source"))
    if re.search(r"\balways\b.*\bnever\b|\bnever\b.*\balways\b", answer, re.I):
        issues.append(Issue("CHECK-CONTRADICTION", 0.7, "internal contradiction"))
    if re.search(r"\b(as of my knowledge|i think|maybe|probably)\b", answer, re.I):
        issues.append(Issue("CHECK-HEDGED", 0.5, "hedged/uncertain claim stated as fact"))
    if "[contains seeded error]" in answer:  # demo marker
        issues.append(Issue("CHECK-SEEDED", 0.9, "known seeded error (demo)"))
    coverage = 1.0 if sources else (0.0 if re.search(r"\d", answer) else 0.5)
    return Verdict(passed=not issues, issues=issues, citation_coverage=coverage)
