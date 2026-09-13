from typing import Literal, NotRequired, TypedDict
from uuid import UUID


class AgentState(TypedDict):
    workflow_id: str
    locale: Literal["fr", "en"]
    title: str
    pitch: str
    evidence: list[dict]
    finding: dict
    idea_id: NotRequired[UUID]
    iteration_id: NotRequired[UUID]
    analysis_id: NotRequired[str]
