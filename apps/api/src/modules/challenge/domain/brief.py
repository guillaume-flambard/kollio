from collections.abc import Sequence
from dataclasses import dataclass
from uuid import UUID


class BriefError(ValueError):
    """Raised when there is nothing to challenge."""


@dataclass(frozen=True)
class BriefOption:
    title: str
    proposal: str
    mechanism: str | None = None
    upside: str | None = None
    cost: str | None = None
    risks: str | None = None
    critical_assumptions: str | None = None
    success_metrics: str | None = None


@dataclass(frozen=True)
class BriefEvidence:
    contribution_id: UUID
    side: str
    title: str
    body: str | None = None


@dataclass(frozen=True)
class Brief:
    payload: dict[str, object]
    contribution_ids: frozenset[UUID]


_OPTION_FIELDS: tuple[tuple[str, str], ...] = (
    ("mechanism", "mechanism"),
    ("upside", "upside"),
    ("cost", "cost"),
    ("risks", "risks"),
    ("critical_assumptions", "critical_assumptions"),
    ("success_metrics", "success_metrics"),
)


def build_brief(*, question: str, option: BriefOption, evidence: Sequence[BriefEvidence]) -> Brief:
    """Assemble what the Critic is allowed to see.

    Only structured material the space already treats as canonical: the space
    question, the option's own fields, and the contributions linked as evidence.
    A narrative field the option does not carry is omitted rather than sent empty,
    so the Critic cannot read an absence as an answer.
    """
    clean_question = question.strip()
    if not clean_question:
        raise BriefError("A challenge needs the question it is challenging")

    option_payload: dict[str, object] = {
        "title": option.title,
        "proposal": option.proposal,
    }
    for attribute, key in _OPTION_FIELDS:
        value = getattr(option, attribute)
        if value is not None and value.strip():
            option_payload[key] = value.strip()

    payload: dict[str, object] = {
        "question": clean_question,
        "option": option_payload,
        "evidence": [
            {
                "contribution_id": str(item.contribution_id),
                "side": item.side,
                "title": item.title,
                "body": item.body,
            }
            for item in evidence
        ],
    }
    return Brief(
        payload=payload,
        contribution_ids=frozenset(item.contribution_id for item in evidence),
    )
