from core import DevMindState, call_llm
from tools.github_tool import (
    get_latest_run_status, get_failed_runs,
    get_failed_steps, get_workflow_runs
)
from tools.slack_tool import send_cicd_notification

SYSTEM_PROMPT = """You are DevMind — a CI/CD pipeline expert.

You analyze GitHub Actions pipeline results and provide clear, actionable reports.

Your report must include:
1. **Pipeline Status** — Pass/Fail with details
2. **What Ran** — Which steps executed
3. **Failure Analysis** — If failed, exactly WHY and WHERE
4. **Fix Suggestion** — Specific steps to resolve the failure
5. **Risk Assessment** — Should this be merged or blocked?

Be specific, technical, and actionable."""


def node_cicd_agent(state: DevMindState) -> DevMindState:
    repo    = state["repo"]
    message = state["message"]
    history = state["history"]

    print(f" CI/CD Agent → checking pipeline for {repo}")

    # get pipeline status
    latest_run    = get_latest_run_status(repo)
    failed_runs   = get_failed_runs(repo)
    recent_runs   = get_workflow_runs(repo, limit=5)

    # build context
    context = f"""
LATEST PIPELINE RUN:
Status:     {latest_run.get('status')}
Conclusion: {latest_run.get('conclusion')}
Branch:     {latest_run.get('branch')}
Commit:     {latest_run.get('commit')}
Triggered:  {latest_run.get('triggered_by')}
URL:        {latest_run.get('url')}

RECENT RUNS SUMMARY:
Total recent runs: {len(recent_runs)}
Failed runs:       {len(failed_runs)}
"""

    # get failed steps if there are failures
    failed_steps = []
    if failed_runs:
        run_id       = failed_runs[0].get("id")
        failed_steps = get_failed_steps(repo, run_id)
        if failed_steps:
            context += "\nFAILED STEPS:\n"
            for step in failed_steps:
                context += f"- Job: {step['job']} | Step: {step['step']}\n"

    # get AI analysis
    analysis = call_llm(
        system_prompt = SYSTEM_PROMPT,
        user_message  = f"Analyze the CI/CD pipeline: {message}",
        context       = context,
        history       = history,
    )

    # determine severity
    conclusion = latest_run.get("conclusion", "")
    severity   = "HIGH" if conclusion == "failure" else "LOW"

    # notify Slack
    send_cicd_notification(
        repo           = repo,
        status         = latest_run.get("status", "unknown"),
        conclusion     = conclusion,
        url            = latest_run.get("url", ""),
        failure_reason = analysis[:300] if conclusion == "failure" else "",
    )

    action = f"Pipeline status checked — {conclusion or 'in_progress'}"
    print(f" CI/CD Agent → {action}")

    return {
        **state,
        "github_data":  {
            "latest_run":   latest_run,
            "failed_runs":  len(failed_runs),
            "failed_steps": failed_steps,
        },
        "analysis":     analysis,
        "action_taken": action,
        "severity":     severity,
        "incident":     conclusion == "failure",
        "notification": f"Pipeline status sent to Slack",
        "response":     f"**CI/CD Pipeline Report**\n\n{analysis}",
        "agent":        "cicd_agent",
    }
