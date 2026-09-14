from typing import Literal, TypedDict


class ConstraintAnalysisState(TypedDict):
    workflow_id: str
    locale: Literal["fr", "en"]
    title: str
    pitch: str
    evidence: list[dict[str, str]]
    context: dict[str, object]
    result: dict[str, object]
    approved: bool | None
