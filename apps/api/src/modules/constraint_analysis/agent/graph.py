from typing import Any, Literal

from langgraph.checkpoint.base import BaseCheckpointSaver
from langgraph.graph import END, START, StateGraph
from langgraph.types import interrupt

from src.modules.constraint_analysis.agent.state import ConstraintAnalysisState
from src.modules.constraint_analysis.domain.models import (
    AnalysisEvidence,
    ConstraintAnalysisResult,
)
from src.modules.constraint_analysis.service.ports import ConstraintAnalysisGateway


def build_constraint_analysis_graph(
    gateway: ConstraintAnalysisGateway,
    checkpointer: BaseCheckpointSaver[Any],
) -> Any:
    async def analyze(state: ConstraintAnalysisState) -> dict[str, object]:
        result = await gateway.analyze(
            title=state["title"],
            pitch=state["pitch"],
            locale=state["locale"],
            evidence=[AnalysisEvidence.model_validate(item) for item in state["evidence"]],
        )
        return {"result": result.model_dump(mode="json")}

    async def review(state: ConstraintAnalysisState) -> dict[str, object]:
        approved = interrupt({"locale": state["locale"], "result": state["result"]})
        if not isinstance(approved, bool):
            raise ValueError("Review must provide a boolean decision")
        return {"approved": approved}

    def after_review(state: ConstraintAnalysisState) -> Literal["complete", "reject"]:
        return "complete" if state["approved"] else "reject"

    async def complete(state: ConstraintAnalysisState) -> dict[str, object]:
        return {
            "result": ConstraintAnalysisResult.model_validate(state["result"]).model_dump(
                mode="json"
            )
        }

    graph = StateGraph(ConstraintAnalysisState)
    graph.add_node("analyze", analyze)
    graph.add_node("review", review)
    graph.add_node("complete", complete)
    graph.add_edge(START, "analyze")
    graph.add_edge("analyze", "review")
    graph.add_conditional_edges("review", after_review, {"complete": "complete", "reject": END})
    graph.add_edge("complete", END)
    return graph.compile(checkpointer=checkpointer)
