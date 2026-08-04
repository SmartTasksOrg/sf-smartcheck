"""UML data objects for SmartCheck — the diagram in the README is these classes."""
from __future__ import annotations
from dataclasses import dataclass, field

@dataclass
class Issue:
    type: str
    confidence: float
    span: str

@dataclass
class Verdict:
    passed: bool
    issues: list[Issue]
    citation_coverage: float
