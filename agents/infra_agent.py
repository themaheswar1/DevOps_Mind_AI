import random
from datetime import datetime
from core import DevMindState, call_llm
from tools.slack_tool import send_slack_message

SYSTEM_PROMPT = """You are DevMind — an infrastructure monitoring expert.

You analyze server metrics and provide clear health reports.

Your report must include:
1. **Overall Health** — GREEN / YELLOW / RED status
2. **Key Metrics** — CPU, Memory, Uptime, Response time
3. **Anomalies** — Anything above normal thresholds
4. **Recommendations** — What to watch or fix
5. **Risk Level** — LOW / MEDIUM / HIGH / CRITICAL

Thresholds:
- CPU > 80% = WARNING, > 95% = CRITICAL
- Memory > 85% = WARNING, > 95% = CRITICAL
- Response time > 500ms = WARNING, > 2000ms = CRITICAL"""


def get_simulated_metrics() -> dict:
    """
    Simulates infrastructure metrics.
    In production: replace with real GCP/AWS monitoring API calls.
    """
    cpu_usage    = round(random.uniform(15, 85), 1)
    memory_usage = round(random.uniform(40, 80), 1)
    disk_usage   = round(random.uniform(30, 70), 1)
    response_time = round(random.uniform(50, 400), 0)
    uptime_hours = round(random.uniform(100, 720), 1)

    return {
        "timestamp":     datetime.utcnow().isoformat(),
        "cpu_usage":     cpu_usage,
        "memory_usage":  memory_usage,
        "disk_usage":    disk_usage,
        "response_time": response_time,
        "uptime_hours":  uptime_hours,
        "requests_per_min": random.randint(50, 500),
        "error_rate":    round(random.uniform(0, 3), 2),
        "active_connections": random.randint(10, 200),
        "status":        "running",
        "region":        "asia-south1",
        "environment":   "production",
    }


def determine_severity(metrics: dict) -> str:
    cpu    = metrics.get("cpu_usage", 0)
    memory = metrics.get("memory_usage", 0)
    rt     = metrics.get("response_time", 0)
    errors = metrics.get("error_rate", 0)

    if cpu > 95 or memory > 95 or rt > 2000 or errors > 5:
        return "CRITICAL"
    if cpu > 80 or memory > 85 or rt > 500 or errors > 2:
        return "HIGH"
    if cpu > 60 or memory > 70 or rt > 200:
        return "MEDIUM"
    return "LOW"


def node_infra_agent(state: DevMindState) -> DevMindState:
    repo    = state["repo"]
    message = state["message"]
    history = state["history"]

    print(f" Infra Agent → checking infrastructure health")

    # get metrics
    metrics  = get_simulated_metrics()
    severity = determine_severity(metrics)

    context = f"""
INFRASTRUCTURE METRICS:
Timestamp:        {metrics['timestamp']}
Environment:      {metrics['environment']}
Region:           {metrics['region']}

PERFORMANCE:
CPU Usage:        {metrics['cpu_usage']}%
Memory Usage:     {metrics['memory_usage']}%
Disk Usage:       {metrics['disk_usage']}%
Response Time:    {metrics['response_time']}ms
Uptime:           {metrics['uptime_hours']} hours

TRAFFIC:
Requests/min:     {metrics['requests_per_min']}
Error Rate:       {metrics['error_rate']}%
Active Connections: {metrics['active_connections']}

COMPUTED SEVERITY: {severity}
"""

    # get AI analysis
    analysis = call_llm(
        system_prompt = SYSTEM_PROMPT,
        user_message  = f"Analyze infrastructure health: {message}",
        context       = context,
        history       = history,
    )

    # notify Slack if not healthy
    if severity in ["HIGH", "CRITICAL"]:
        send_slack_message(
            message  = f"*Infrastructure Alert*\n{analysis[:400]}",
            severity = severity,
            intent   = "infra_health",
        )

    action = f"Infrastructure health checked — severity: {severity}"
    print(f" Infra Agent → {action}")

    return {
        **state,
        "github_data":  metrics,
        "analysis":     analysis,
        "action_taken": action,
        "severity":     severity,
        "incident":     severity in ["HIGH", "CRITICAL"],
        "notification": f"Infrastructure report generated — {severity}",
        "response":     f"**Infrastructure Health Report**\n\n{analysis}",
        "agent":        "infra_agent",
    }
