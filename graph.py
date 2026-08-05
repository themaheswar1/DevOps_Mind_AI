from typing import List
from langgraph.graph import StateGraph, END
from core import DevMindState, build_initial_state
from agents.orchestrator import node_orchestrate, router
from agents.pr_agent import node_pr_agent
from agents.cicd_agent import node_cicd_agent
from agents.infra_agent import node_infra_agent
from agents.incident_agent import node_incident_agent
from agents.notification_agent import node_notification_agent


def build_graph():
    graph = StateGraph(DevMindState)

    # add all nodes
    graph.add_node("orchestrator",    node_orchestrate)
    graph.add_node("pr_agent",        node_pr_agent)
    graph.add_node("cicd_agent",      node_cicd_agent)
    graph.add_node("infra_agent",     node_infra_agent)
    graph.add_node("incident_agent",  node_incident_agent)
    graph.add_node("notification",    node_notification_agent)

    # entry point
    graph.set_entry_point("orchestrator")

    # orchestrator routes to specialist agent
    graph.add_conditional_edges(
        "orchestrator",
        router,
        {
            "pr_agent":       "pr_agent",
            "cicd_agent":     "cicd_agent",
            "infra_agent":    "infra_agent",
            "incident_agent": "incident_agent",
        }
    )

    # all agents → notification → END
    graph.add_edge("pr_agent",       "notification")
    graph.add_edge("cicd_agent",     "notification")
    graph.add_edge("infra_agent",    "notification")
    graph.add_edge("incident_agent", "notification")
    graph.add_edge("notification",   END)

    return graph.compile()


def run_turn(message: str, history: List[dict], graph) -> dict:
    initial_state = build_initial_state(message, history)
    result = graph.invoke(initial_state)
    return result


print(" **==DevMind Graph loaded===**")
