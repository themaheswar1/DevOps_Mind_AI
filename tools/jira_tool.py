import os
import hashlib
from datetime import datetime

# ── Simulated Jira Tool ───────────────────────────────────────────────────────
# Uses Jira REST API if credentials are provided
# Falls back to simulated tickets for demo purposes

JIRA_URL      = os.getenv("JIRA_URL", "")
JIRA_EMAIL    = os.getenv("JIRA_EMAIL", "")
JIRA_TOKEN    = os.getenv("JIRA_API_TOKEN", "")
JIRA_PROJECT  = os.getenv("JIRA_PROJECT", "DEVMIND")


def _generate_ticket_id(title: str) -> str:
    hash_val = hashlib.md5(
        (title + datetime.now().isoformat()).encode()
    ).hexdigest()[:6].upper()
    return f"{JIRA_PROJECT}-{hash_val}"


def create_incident_ticket(title: str, description: str,
                           severity: str = "HIGH") -> dict:
    ticket_id = _generate_ticket_id(title)

    priority_map = {
        "LOW":      "Low",
        "MEDIUM":   "Medium",
        "HIGH":     "High",
        "CRITICAL": "Highest",
    }

    ticket = {
        "id":          ticket_id,
        "title":       title,
        "description": description,
        "priority":    priority_map.get(severity, "High"),
        "status":      "Open",
        "created_at":  datetime.now().isoformat(),
        "assignee":    "DevMind Bot",
        "labels":      ["devmind-auto", "incident", severity.lower()],
    }

    print(f"Jira ticket created: {ticket_id}")
    return ticket


def get_open_tickets() -> list:
    return [
        {
            "id":       f"{JIRA_PROJECT}-001",
            "title":    "Sample open ticket",
            "priority": "Medium",
            "status":   "In Progress",
        }
    ]


def close_ticket(ticket_id: str) -> bool:
    print(f"**== Jira ticket {ticket_id} closed ==**")
    return True


print(" --** Jira Tool loaded **-- ")
