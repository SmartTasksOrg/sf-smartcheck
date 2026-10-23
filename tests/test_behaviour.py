"""Behaviour of core.check: which issue each kind of claim raises, and the citation coverage."""
from sf_smartcheck.core import check


def kinds(v):
    return [i.type for i in v.issues]


def test_large_number_without_a_source_is_flagged():
    v = check("Revenue grew 340 last quarter.")
    assert not v.passed and kinds(v) == ["CHECK-UNSOURCED-NUMBER"]
    assert v.citation_coverage == 0.0


def test_the_same_number_with_a_source_passes():
    v = check("Revenue grew 340 last quarter.", sources="Q3 report, p. 4")
    assert v.passed and v.issues == [] and v.citation_coverage == 1.0


def test_percentages_and_magnitude_words_count_as_numeric_claims():
    assert kinds(check("Churn fell 7.2 % this year.")) == ["CHECK-UNSOURCED-NUMBER"]
    assert kinds(check("Adoption reached 20%.")) == ["CHECK-UNSOURCED-NUMBER"]
    assert kinds(check("We now serve 1.6 million users.")) == ["CHECK-UNSOURCED-NUMBER"]


def test_a_small_plain_number_is_not_a_claim_but_lowers_coverage():
    v = check("We have 42 cats.")
    assert v.passed and v.citation_coverage == 0.0


def test_text_without_digits_has_half_coverage():
    v = check("The sky is blue.")
    assert v.passed and v.citation_coverage == 0.5


def test_always_and_never_together_is_a_contradiction():
    assert "CHECK-CONTRADICTION" in kinds(check("It always works and never fails."))
    assert "CHECK-CONTRADICTION" in kinds(check("It never fails, it always works."))
    assert "CHECK-CONTRADICTION" not in kinds(check("It always works."))


def test_hedged_language_is_flagged_case_insensitively():
    assert kinds(check("I think the answer is Paris.")) == ["CHECK-HEDGED"]
    assert kinds(check("PROBABLY the answer is Paris.")) == ["CHECK-HEDGED"]


def test_issue_confidences_are_fixed_per_kind():
    v = check("I think it always grows 500 and never shrinks. [contains seeded error]")
    conf = {i.type: i.confidence for i in v.issues}
    assert conf == {"CHECK-UNSOURCED-NUMBER": 0.6, "CHECK-CONTRADICTION": 0.7,
                    "CHECK-HEDGED": 0.5, "CHECK-SEEDED": 0.9}
