from typing import Literal, TypedDict


class AgentState(TypedDict):
    workflow_id: str
    locale: Literal["fr", "en"]
    title: str
    pitch: str
    evidence: list[dict]
    finding: dict
