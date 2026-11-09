"""SmartCheck core — flag confident-but-wrong AI output.

Without sources, `check()` flags the patterns that most often hide errors:
numeric claims with no source, "always ... never" contradictions and hedged
claims stated as fact.

With sources, it also checks the answer against them:

* every number in the answer must appear in the sources (CHECK-NUMBER-NOT-IN-SOURCE);
* every sentence must share enough content words with some source sentence
  (CHECK-UNSUPPORTED); `citation_coverage` is the share of sentences supported.

Word overlap is a cheap first pass: it catches invented figures and sentences
that have nothing to do with the sources, but it cannot tell a paraphrase that
reverses a meaning from one that keeps it. Pass `judge=` for a model-based
check of each sentence; a judge that fails or returns something unreadable
counts as "not supported", never as a pass.
"""
from __future__ import annotations

import json
import re
from typing import Callable

from .models import Issue, Verdict

# A quantitative claim: a 3+ digit run, a percentage (e.g. 20%, 7.2 %), or a
# number paired with a magnitude word (e.g. 1.6 million).
_NUM = re.compile(
    r"\b\d{3,}\b"
    r"|\b\d+(?:\.\d+)?\s?%"
    r"|\b\d+(?:\.\d+)?\s*(?:hundred|thousand|million|billion|trillion)\b",
    re.I)
# Every number, for matching against sources (1,200 and 1200 are the same).
_ANY_NUM = re.compile(r"\d[\d,]*(?:\.\d+)?")
_SENT = re.compile(r"(?<=[.!?。！？])\s+|\n+")
_WORD = re.compile(r"[A-Za-z][A-Za-z'-]+|\d[\d,]*(?:\.\d+)?|[一-鿿]")
_STOP = set("""a an the and or but if of to in on at by for with from as is are was were be been being
it its this that these those there here we you they he she i our your their his her them us
has have had do does did not no so than then too very can could should would will may might
must about into over under after before also just only such""".split())

#: A sentence is supported when at least this share of its content words
#: appears in one source sentence.
SUPPORT_THRESHOLD = 0.5

Judge = Callable[[str, str], object]


def _norm_num(s: str) -> str:
    s = s.replace(",", "")
    return s.rstrip("0").rstrip(".") if "." in s else s


def _content_words(text: str) -> set[str]:
    return {w.lower().replace(",", "") for w in _WORD.findall(text)} - _STOP


def _sentences(text: str) -> list[str]:
    return [s.strip() for s in _SENT.split(text) if s and s.strip()]


def _support(sentence: str, source_sents: list[set[str]]) -> float:
    words = _content_words(sentence)
    if not words:
        return 1.0
    return max((len(words & src) / len(words) for src in source_sents), default=0.0)


def _judge_says_supported(judge: Judge, sentence: str, sources: str) -> bool:
    """Ask the judge; anything other than a clear yes counts as unsupported."""
    try:
        raw = judge(sentence, sources)
    except Exception:
        return False
    if isinstance(raw, bool):
        return raw
    if isinstance(raw, dict):
        return raw.get("supported") is True
    if isinstance(raw, str):
        try:
            parsed = json.loads(raw)
        except ValueError:
            return raw.strip().lower() in ("yes", "supported", "true")
        return isinstance(parsed, dict) and parsed.get("supported") is True
    return False


def check(answer: str, sources: str = "", *, judge: Judge | None = None,
          threshold: float = SUPPORT_THRESHOLD) -> Verdict:
    """Check `answer`, against `sources` (the source text itself) when given.

    `judge(sentence, sources)` may return a bool, a dict or JSON with a
    boolean "supported" field, or "yes". It is consulted for sentences that
    word overlap does not already support.
    """
    issues: list[Issue] = []
    has_sources = bool(sources and sources.strip())

    if _NUM.search(answer) and not has_sources:
        issues.append(Issue("CHECK-UNSOURCED-NUMBER", 0.6, "numeric claim with no source"))
    if re.search(r"\balways\b.*\bnever\b|\bnever\b.*\balways\b", answer, re.I):
        issues.append(Issue("CHECK-CONTRADICTION", 0.7, "internal contradiction"))
    if re.search(r"\b(as of my knowledge|i think|maybe|probably)\b", answer, re.I):
        issues.append(Issue("CHECK-HEDGED", 0.5, "hedged/uncertain claim stated as fact"))

    if not has_sources:
        coverage = 0.0 if re.search(r"\d", answer) else 0.5
        return Verdict(passed=not issues, issues=issues, citation_coverage=coverage)

    source_numbers = {_norm_num(n) for n in _ANY_NUM.findall(sources)}
    for n in _ANY_NUM.findall(answer):
        if _norm_num(n) not in source_numbers:
            issues.append(Issue("CHECK-NUMBER-NOT-IN-SOURCE", 0.8, n))

    source_sents = [_content_words(s) for s in _sentences(sources)] or [_content_words(sources)]
    sentences = _sentences(answer)
    supported = 0
    for s in sentences:
        ok = _support(s, source_sents) >= threshold
        if not ok and judge is not None:
            ok = _judge_says_supported(judge, s, sources)
        if ok:
            supported += 1
        else:
            issues.append(Issue("CHECK-UNSUPPORTED", 0.7, s[:120]))
    coverage = round(supported / len(sentences), 2) if sentences else 1.0
    return Verdict(passed=not issues, issues=issues, citation_coverage=coverage)
