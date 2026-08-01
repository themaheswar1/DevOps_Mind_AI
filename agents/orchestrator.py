from core import DevMindState, detect_intent
import re


def node_orchestrate(state: DevMindState) -> DevMindState:
    """
    Entry point for all requests.
    Detects intent and extracts PR number if mentioned.
    """
    message = state["message"]
    intent  = detect_intent(message)

    # extract PR number if mentioned
    pr_number = None
    match = re.search(r"pr\s*#?\s*(\d+)|pull\s*request\s*#?\s*(\d+)", message.lower())
    if match:
        pr_number = int(match.group(1) or match.group(2))

    print(f" Orchestrator → Intent: {intent} | PR: {pr_number}")

    return {
        **state,
        "intent":    intent,
        "pr_number": pr_number,
    }


def router(state: DevMindState) -> str:
    """Route to the correct agent based on intent."""
    intent = state["intent"]

    routing = {
        "pr_review":      "pr_agent",
        "cicd_status":    "cicd_agent",
        "infra_health":   "infra_agent",
        "incident_check": "incident_agent",
        "general":        "pr_agent",
    }

    return routing.get(intent, "pr_agent")
