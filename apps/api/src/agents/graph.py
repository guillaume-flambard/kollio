from langgraph.graph import END, START, StateGraph
from langgraph.types import interrupt

from src.agents.schemas import ConstraintAnalysis, GateFinding
from src.agents.state import AgentState
from src.modules.iterations.store import store_raw_analysis
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


def build_analysis_graph(gateway, checkpointer, sessions, analyses):
    async def assess_constraints(state: AgentState):
        analysis = await gateway.assess_constraints(
            state["title"], state["pitch"], state["locale"], state["evidence"]
        )
        return {"finding": ConstraintAnalysis.model_validate(analysis).model_dump()}

    async def persist_analysis(state: AgentState):
        analysis = ConstraintAnalysis.model_validate(state["finding"])
        result = await save_result(
            sessions,
            state["workflow_id"],
            "constraints",
            {k: state[k] for k in ("title", "pitch", "locale", "evidence", "iteration_id")},
            analysis.model_dump(),
        )
        stored = await store_raw_analysis(
            analyses,
            state["idea_id"],
            state["iteration_id"],
            result,
            model=gateway.settings.llm_model,
        )
        return {"finding": result, "analysis_id": str(stored.id)}

    graph = StateGraph(AgentState)
    graph.add_node("assess_constraints", assess_constraints)
    graph.add_node("persist_analysis", persist_analysis)
    graph.add_edge(START, "assess_constraints")
    graph.add_edge("assess_constraints", "persist_analysis")
    graph.add_edge("persist_analysis", END)
    return graph.compile(checkpointer=checkpointer)
