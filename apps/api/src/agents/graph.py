from langgraph.graph import END, START, StateGraph
from langgraph.types import interrupt

from src.agents.schemas import GateFinding
from src.agents.state import AgentState
from src.platform.effects import save_result


def build_graph(gateway, checkpointer, sessions):
    async def assess(state: AgentState):
        finding = await gateway.assess(
            state["title"], state["pitch"], state["locale"], state["evidence"]
        )
        return {"finding": GateFinding.model_validate(finding).model_dump()}

    async def review(state: AgentState):
        approved = interrupt({"locale": state["locale"], "finding": state["finding"]})
        if approved is not True:
            raise ValueError("Review must be explicitly approved")
        return {}

    async def persist(state: AgentState):
        finding = GateFinding.model_validate(state["finding"])
        result = await save_result(
            sessions,
            state["workflow_id"],
            "competition",
            {k: state[k] for k in ("title", "pitch", "locale", "evidence")},
            finding.model_dump(),
        )
        return {"finding": result}

    graph = StateGraph(AgentState)
    graph.add_node("assess", assess)
    graph.add_node("review", review)
    graph.add_node("persist", persist)
    graph.add_edge(START, "assess")
    graph.add_edge("assess", "review")
    graph.add_edge("review", "persist")
    graph.add_edge("persist", END)
    return graph.compile(checkpointer=checkpointer)
