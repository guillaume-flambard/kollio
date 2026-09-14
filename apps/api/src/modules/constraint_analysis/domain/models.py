"""The model-facing analysis contract.

Ticket #58 fixed the separation: every factor carries a basis from
Known, Assumed or Unknown. An unknown factor carries no score and names
the evidence it is missing; a known factor must cite supplied evidence.
The engine may also state contradictions against the active company
context, referencing the objective or constraint id it contradicts.
"""

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

FactorName = Literal[
    "competition",
    "build_cost",
    "time_to_market",
    "defensibility",
    "acquisition",
]

Basis = Literal["known", "assumed", "unknown"]

ContradictionTarget = Literal["objective", "constraint"]

EXPECTED_FACTORS: frozenset[str] = frozenset(
    {"competition", "build_cost", "time_to_market", "defensibility", "acquisition"}
)


class AnalysisEvidence(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)

    id: str = Field(min_length=1)
    url: str = Field(min_length=1)
    text: str = Field(min_length=1)


class ConstraintFactor(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)

    name: FactorName
    basis: Basis
    score: int | None = Field(ge=0, le=100)
    gap: str | None
    summary: str = Field(min_length=1)
    source_ids: list[str]

    @model_validator(mode="after")
    def require_the_basis_shape(self) -> ConstraintFactor:
        if self.basis == "unknown":
            if self.score is not None:
                raise ValueError("An unknown factor carries no score")
            if not (self.gap or "").strip():
                raise ValueError("An unknown factor names the evidence it is missing")
            if self.source_ids:
                raise ValueError("An unknown factor cites no evidence")
        elif self.basis == "known":
            if self.score is None:
                raise ValueError("A known factor carries a score")
            if not self.source_ids:
                raise ValueError("A known factor cites at least one supplied evidence id")
        else:
            if self.score is None:
                raise ValueError("An assumed factor carries a score")
        return self


class Contradiction(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)

    target: ContradictionTarget
    ref_id: str = Field(min_length=1)
    detail: str = Field(min_length=1)


class ConstraintAnalysisResult(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)

    overall_score: int | None = Field(ge=0, le=100)
    verdict: Literal["viable", "conditional", "not_viable", "unknown"]
    summary: str = Field(min_length=1)
    factors: list[ConstraintFactor] = Field(min_length=5, max_length=5)
    contradictions: list[Contradiction]
    locale: Literal["fr", "en"]

    @model_validator(mode="after")
    def require_all_factors(self) -> ConstraintAnalysisResult:
        names = [factor.name for factor in self.factors]
        if len(set(names)) != len(names) or set(names) != EXPECTED_FACTORS:
            raise ValueError("Each required constraint factor must appear exactly once")
        if self.verdict == "unknown":
            if self.overall_score is not None:
                raise ValueError("An unknown verdict carries no overall score")
            if any(factor.basis != "unknown" for factor in self.factors):
                raise ValueError("An unknown verdict requires every factor to be unknown")
        elif self.overall_score is None:
            raise ValueError("A scored verdict carries an overall score")
        return self


def context_reference_ids(company_context: dict[str, object] | None) -> frozenset[str]:
    """The ids a contradiction may reference: the active objectives and constraints."""
    if not company_context:
        return frozenset()
    ids: set[str] = set()
    for key in ("objectives", "constraints"):
        items = company_context.get(key)
        if not isinstance(items, list):
            continue
        for item in items:
            if isinstance(item, dict) and isinstance(item.get("id"), str):
                ids.add(str(item["id"]))
    return frozenset(ids)


def validate_analysis_result(
    result: ConstraintAnalysisResult,
    *,
    requested_locale: str,
    evidence_ids: frozenset[str],
    context_ids: frozenset[str] = frozenset(),
) -> ConstraintAnalysisResult:
    if result.locale != requested_locale:
        raise ValueError("The model returned the wrong locale")
    cited_ids = {source_id for factor in result.factors for source_id in factor.source_ids}
    if not cited_ids.issubset(evidence_ids):
        raise ValueError("The model cited unknown evidence")
    if result.verdict != "unknown" and not cited_ids:
        raise ValueError("A non-unknown verdict requires evidence")
    referenced = {contradiction.ref_id for contradiction in result.contradictions}
    if referenced and not referenced.issubset(context_ids):
        raise ValueError("The model contradicted a context item that was not supplied")
    return result


class AnalystReport(BaseModel):
    """Step 1, the case in favour. Cheap work: it only has to be grounded."""

    model_config = ConfigDict(extra="forbid")

    arguments: list[str] = Field(min_length=1)


class ChallengerReport(BaseModel):
    """Step 2, why this fails specifically at this company. Visible work."""

    model_config = ConfigDict(extra="forbid")

    risks: list[str] = Field(min_length=1)
    missing_evidence: list[str] = Field(default_factory=list)


class EvidenceReport(BaseModel):
    """Step 3, separating stated fact from speculation. Visible work."""

    model_config = ConfigDict(extra="forbid")

    facts: list[str] = Field(default_factory=list)
    speculation: list[str] = Field(default_factory=list)


class CompanyFitReport(BaseModel):
    """Step 4, comparison against the active objectives and constraints."""

    model_config = ConfigDict(extra="forbid")

    supports: list[str] = Field(default_factory=list)
    conflicts: list[str] = Field(default_factory=list)
