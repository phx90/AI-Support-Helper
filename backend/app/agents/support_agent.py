from typing import TypedDict

from langgraph.graph import END, START, StateGraph


class AgentState(TypedDict, total=False):
    question: str
    action: str
    answer: str


def analyze(state: AgentState) -> AgentState:
    q = state["question"].lower()
    ticket = any(
        x in q for x in ["abra um chamado", "crie um chamado", "open a ticket", "create a ticket"]
    )
    status = any(x in q for x in ["status do sistema", "system status"])
    return {**state, "action": "create_ticket" if ticket else "status" if status else "retrieve"}


def route(state: AgentState) -> str:
    return state["action"]


def build_agent():
    g = StateGraph(AgentState)
    g.add_node("analyze_question", analyze)
    g.add_edge(START, "analyze_question")
    g.add_conditional_edges(
        "analyze_question", route, {"create_ticket": END, "status": END, "retrieve": END}
    )
    return g.compile()


support_agent = build_agent()
