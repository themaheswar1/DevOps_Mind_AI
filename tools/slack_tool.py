import os
import requests

SLACK_WEBHOOK = os.getenv("SLACK_WEBHOOK_URL")

# severity → emoji mapping
SEVERITY_EMOJI = {
    "LOW":      "✅",
    "MEDIUM":   "⚠️",
    "HIGH":     "🔴",
    "CRITICAL": "🚨",
}

# intent → channel mapping
CHANNEL_MAP = {
    "pr_review":      "#pr-reviews",
    "cicd_status":    "#devops-alerts",
    "infra_health":   "#devops-alerts",
    "incident_check": "#incidents",
    "general":        "#devops-alerts",
}


def send_slack_message(message: str, severity: str = "LOW",
                       intent: str = "general") -> bool:
    if not SLACK_WEBHOOK:
        print(" !! -- Slack webhook not configured -- !! ")
        return False

    emoji   = SEVERITY_EMOJI.get(severity, "ℹ️")
    channel = CHANNEL_MAP.get(intent, "#devops-alerts")

    payload = {
        "blocks": [
            {
                "type": "header",
                "text": {
                    "type":  "plain_text",
                    "text":  f"{emoji} DevMind Alert",
                    "emoji": True
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": message
                }
            },
            {
                "type": "context",
                "elements": [
                    {
                        "type": "mrkdwn",
                        "text": f"*Severity:* {severity} | *Channel:* {channel} | *Powered by DevMind AI*"
                    }
                ]
            },
            {"type": "divider"}
        ]
    }

    response = requests.post(SLACK_WEBHOOK, json=payload)
    return response.status_code == 200


def send_pr_notification(pr_number: int, repo: str,
                         review_summary: str, url: str) -> bool:
    message = (
        f"*🔍 PR #{pr_number} Reviewed*\n"
        f"*Repo:* `{repo}`\n"
        f"*Summary:*\n{review_summary[:500]}\n"
        f"*View PR:* {url}"
    )
    return send_slack_message(message, severity="LOW", intent="pr_review")


def send_cicd_notification(repo: str, status: str,
                           conclusion: str, url: str,
                           failure_reason: str = "") -> bool:
    if conclusion == "success":
        severity = "LOW"
        header   = " Build Passed"
    elif conclusion == "failure":
        severity = "HIGH"
        header   = " Build Failed"
    else:
        severity = "MEDIUM"
        header   = " Build Status Unknown"

    message = (
        f"*{header}*\n"
        f"*Repo:* `{repo}`\n"
        f"*Status:* {status} | *Conclusion:* {conclusion}\n"
    )

    if failure_reason:
        message += f"*Failure Reason:*\n{failure_reason[:300]}\n"

    message += f"*View Run:* {url}"

    return send_slack_message(message, severity=severity, intent="cicd_status")


def send_incident_notification(repo: str, severity: str,
                               description: str, jira_ticket: str = "") -> bool:
    message = (
        f"*INCIDENT DETECTED*\n"
        f"*Repo:* `{repo}`\n"
        f"*Severity:* {severity}\n"
        f"*Description:*\n{description[:400]}\n"
    )
    if jira_ticket:
        message += f"*Jira Ticket:* {jira_ticket}"

    return send_slack_message(message, severity=severity, intent="incident_check")


print(" ** == Slack Tool loaded == **")
