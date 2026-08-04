from core import DevMindState, call_llm
from tools.github_tool import get_failed_runs, get_latest_run_status
from tools.slack_tool import send_incident_notification
from tools.jira_tool import create_incident_ticket

SYSTEM_PROMPT = """You are DevMind — an incident response expert.

You detect, analyze, and coordinate responses to DevOps incidents.

Your incident report must include:
1. **Incident Summary** — What happened in 1-2 sentences
2. **Root Cause Analysis** — Why did this happen?
3. **Impact Assessment** — What is affected and how severely?
4. **Immediate Actions** — What to do RIGHT NOW (numbered list)
5. **Prevention** — How to prevent this in future
6. **Severity** — CRITICAL / HIGH / MEDIUM / LOW with justification

Be decisive and actionable. Time matters in incidents."""


def node_incident_agent(state: DevMindState) -> DevMindState:
    repo    = state["repo"]
    message = state["message"]
    history = state["history"]

    print(f" Incident Agent → analyzing incidents for {repo}")

    # gather signals from all sources
    latest_run  = get_latest_run_status(repo)
    failed_runs = get_failed_runs(repo)

    # determine if there's an active incident
    has_pipeline_failure = latest_run.get("conclusion") == "failure"
    failure_count        = len(failed_runs)

    # determine severity based on signals
    if failure_count >= 3:
        severity = "CRITICAL"
    elif failure_count >= 1 and has_pipeline_failure:
        severity = "HIGH"
    elif has_pipeline_failure:
        severity = "MEDIUM"
    else:
        severity = "LOW"

    context = f"""
INCIDENT SIGNALS:

PIPELINE STATUS:
Latest run conclusion: {latest_run.get('conclusion', 'unknown')}
Latest run status:     {latest_run.get('status', 'unknown')}
Branch:                {latest_run.get('branch', 'unknown')}
Commit:                {latest_run.get('commit', 'unknown')}

FAILURE HISTORY:
Total recent failures: {failure_count}
Active incident:       {has_pipeline_failure}

COMPUTED SEVERITY: {severity}

USER QUERY: {message}
"""

    # get AI incident analysis
    analysis = call_llm(
        system_prompt = SYSTEM_PROMPT,
        user_message  = f"Analyze incidents and provide response plan: {message}",
        context       = context,
        history       = history,
    )

    # create Jira ticket if incident is real
    jira_ticket = {}
    if severity in ["HIGH", "CRITICAL"]:
        jira_ticket = create_incident_ticket(
            title       = f"[{severity}] Pipeline failure in {repo}",
            description = analysis[:500],
            severity    = severity,
        )

    # notify Slack
    send_incident_notification(
        repo        = repo,
        severity    = severity,
        description = analysis[:400],
        jira_ticket = jira_ticket.get("id", ""),
    )

    action = (
        f"Incident analyzed — severity: {severity}"
        + (f", Jira: {jira_ticket.get('id')}" if jira_ticket else "")
    )
    print(f" Incident Agent → {action}")

    return {
        **state,
        "github_data":  {
            "latest_run":    latest_run,
            "failure_count": failure_count,
            "jira_ticket":   jira_ticket,
        },
        "analysis":     analysis,
        "action_taken": action,
        "severity":     severity,
        "incident":     has_pipeline_failure,
        "notification": f"Incident report sent to Slack — {severity}",
        "response":     f"**Incident Report**\n\n{analysis}",
        "agent":        "incident_agent",
    }
