"""Behaviour of core.check: which issue each kind of claim raises, and the citation coverage."""
from sf_smartcheck.core import check


def kinds(v):
    return [i.type for i in v.issues]


def test_large_number_without_a_source_is_flagged():
    v = check("Revenue grew 340 last quarter.")
    assert not v.passed and kinds(v) == ["CHECK-UNSOURCED-NUMBER"]
    assert v.citation_coverage == 0.0


def test_the_same_number_with_a_source_that_contains_it_passes():
    v = check("Revenue grew 340 last quarter.", sources="Q3 report, p. 4: revenue grew 340 last quarter.")
    assert v.passed and v.issues == [] and v.citation_coverage == 1.0


def test_a_source_that_does_not_contain_the_number_is_not_enough():
    """Version 3.0 passed any answer once any source text was given."""
    v = check("Revenue grew 340 last quarter.", sources="Q3 report, p. 4")
    assert not v.passed
    assert "CHECK-NUMBER-NOT-IN-SOURCE" in kinds(v) and "CHECK-UNSUPPORTED" in kinds(v)


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
    v = check("I think it always grows 500 and never shrinks.")
    conf = {i.type: i.confidence for i in v.issues}
    assert conf == {"CHECK-UNSOURCED-NUMBER": 0.6, "CHECK-CONTRADICTION": 0.7,
                    "CHECK-HEDGED": 0.5}


SOURCE = "Q3 report: revenue grew 3.4% to 1,200 million yuan. Churn was flat at 2%."


def test_numbers_are_matched_against_the_sources():
    assert check("Revenue grew 3.4% to 1,200 million yuan.", SOURCE).passed
    assert check("Revenue grew 3.4% to 1200 million yuan.", SOURCE).passed     # 1,200 == 1200
    v = check("Revenue grew 4.3% to 1,200 million yuan.", SOURCE)
    assert [i.span for i in v.issues if i.type == "CHECK-NUMBER-NOT-IN-SOURCE"] == ["4.3"]


def test_sentences_with_no_support_are_flagged_and_lower_coverage():
    v = check("Revenue grew 3.4% to 1,200 million yuan. The board approved a dividend.", SOURCE)
    assert kinds(v) == ["CHECK-UNSUPPORTED"]
    assert v.issues[0].span == "The board approved a dividend."
    assert v.citation_coverage == 0.5


def test_a_judge_can_support_a_paraphrase():
    answer = "Customer attrition did not change."
    assert "CHECK-UNSUPPORTED" in kinds(check(answer, SOURCE))
    v = check(answer, SOURCE, judge=lambda sentence, sources: {"supported": True})
    assert v.passed and v.citation_coverage == 1.0


def test_a_failing_or_unreadable_judge_never_passes_a_sentence():
    answer = "Customer attrition did not change."
    def broken(sentence, sources):
        raise RuntimeError("model down")
    for judge in (broken, lambda s, src: "Sure, looks fine!", lambda s, src: '{"supported": "yes"}', lambda s, src: None):
        assert "CHECK-UNSUPPORTED" in kinds(check(answer, SOURCE, judge=judge))
    assert check(answer, SOURCE, judge=lambda s, src: '{"supported": true}').passed


def test_chinese_text_is_checked_character_by_character():
    src = "第三季度营收增长3.4%。"
    assert check("营收增长3.4%。", src).passed
    assert not check("利润下降。", src).passed


def test_cli_checks_files_and_sets_the_exit_code(tmp_path, capsys):
    from sf_smartcheck import cli
    ans, src = tmp_path / "answer.txt", tmp_path / "source.txt"
    src.write_text(SOURCE)
    ans.write_text("Revenue grew 3.4% to 1,200 million yuan.")
    assert cli.main([str(ans), "--sources", str(src)]) == 0
    ans.write_text("Revenue grew 9% to 5,000 million yuan.")
    assert cli.main([str(ans), "--sources", str(src), "--json"]) == 1
    assert '"CHECK-NUMBER-NOT-IN-SOURCE"' in capsys.readouterr().out
