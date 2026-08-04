from core import DevMindState
from tools.slack_tool import send_slack_message


def node_notification_agent(state: DevMindState) -> DevMindState:
    """
    Final node — always runs after any agent.
    Ensures all responses are properly logged.
    """
    agent    = state.get("agent", "unknown")
    severity = state.get("severity", "LOW")
    incident = state.get("incident", False)

    # if HIGH/CRITICAL and not already notified — send summary
    if incident and severity in ["HIGH", "CRITICAL"]:
        summary = (
            f"*DevMind Summary*\n"
            f"*Agent:* {agent}\n"
            f"*Severity:* {severity}\n"
            f"*Action:* {state.get('action_taken', 'N/A')}\n"
            f"*Repo:* `{state.get('repo', 'N/A')}`"
        )
        send_slack_message(summary, severity=severity)
        print(f" Notification Agent → summary sent for {severity} incident")

    return state
