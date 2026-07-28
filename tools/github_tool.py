import os
import requests
from typing import Optional

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
BASE_URL     = "https://api.github.com"

HEADERS = {
    "Authorization": f"Bearer {GITHUB_TOKEN}",
    "Accept":        "application/vnd.github+json",
    "X-GitHub-Api-Version": "2022-11-28"
}


# ── Pull Requests ─────────────────────────────────────────────────────────────
def get_open_prs(repo: str) -> list:
    """Get all open PRs for a repo"""
    url      = f"{BASE_URL}/repos/{repo}/pulls?state=open"
    response = requests.get(url, headers=HEADERS)
    if response.status_code == 200:
        return response.json()
    return []


def get_pr_diff(repo: str, pr_number: int) -> str:
    """Get the code diff for a specific PR"""
    url     = f"{BASE_URL}/repos/{repo}/pulls/{pr_number}"
    headers = {**HEADERS, "Accept": "application/vnd.github.diff"}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.text[:8000]  # limit diff size
    return ""


def get_pr_details(repo: str, pr_number: int) -> dict:
    """Get full details of a specific PR"""
    url      = f"{BASE_URL}/repos/{repo}/pulls/{pr_number}"
    response = requests.get(url, headers=HEADERS)
    if response.status_code == 200:
        return response.json()
    return {}


def post_pr_comment(repo: str, pr_number: int, comment: str) -> bool:
    """Post a review comment on a PR"""
    url      = f"{BASE_URL}/repos/{repo}/issues/{pr_number}/comments"
    payload  = {"body": f"🤖 **DevMind AI Review**\n\n{comment}"}
    response = requests.post(url, headers=HEADERS, json=payload)
    return response.status_code == 201


def get_latest_pr(repo: str) -> Optional[dict]:
    """Get the most recent open PR"""
    prs = get_open_prs(repo)
    return prs[0] if prs else None


# ── GitHub Actions / CI/CD ────────────────────────────────────────────────────
def get_workflow_runs(repo: str, limit: int = 5) -> list:
    """Get recent workflow runs"""
    url      = f"{BASE_URL}/repos/{repo}/actions/runs?per_page={limit}"
    response = requests.get(url, headers=HEADERS)
    if response.status_code == 200:
        return response.json().get("workflow_runs", [])
    return []


def get_latest_run_status(repo: str) -> dict:
    """Get status of the most recent workflow run"""
    runs = get_workflow_runs(repo, limit=1)
    if not runs:
        return {"status": "unknown", "conclusion": "unknown"}

    run = runs[0]
    return {
        "id":           run.get("id"),
        "name":         run.get("name"),
        "status":       run.get("status"),
        "conclusion":   run.get("conclusion"),
        "branch":       run.get("head_branch"),
        "commit":       run.get("head_sha", "")[:7],
        "triggered_by": run.get("event"),
        "url":          run.get("html_url"),
        "created_at":   run.get("created_at"),
    }


def get_failed_runs(repo: str) -> list:
    """Get only failed workflow runs"""
    runs = get_workflow_runs(repo, limit=10)
    return [r for r in runs if r.get("conclusion") == "failure"]


def get_run_jobs(repo: str, run_id: int) -> list:
    """Get jobs for a specific workflow run"""
    url      = f"{BASE_URL}/repos/{repo}/actions/runs/{run_id}/jobs"
    response = requests.get(url, headers=HEADERS)
    if response.status_code == 200:
        return response.json().get("jobs", [])
    return []


def get_failed_steps(repo: str, run_id: int) -> list:
    """Get only the failed steps from a run"""
    jobs   = get_run_jobs(repo, run_id)
    failed = []
    for job in jobs:
        for step in job.get("steps", []):
            if step.get("conclusion") == "failure":
                failed.append({
                    "job":  job.get("name"),
                    "step": step.get("name"),
                    "url":  job.get("html_url"),
                })
    return failed


# ── Repository Info ───────────────────────────────────────────────────────────
def get_repo_info(repo: str) -> dict:
    """Get general repository information"""
    url      = f"{BASE_URL}/repos/{repo}"
    response = requests.get(url, headers=HEADERS)
    if response.status_code == 200:
        data = response.json()
        return {
            "name":         data.get("name"),
            "description":  data.get("description"),
            "stars":        data.get("stargazers_count"),
            "forks":        data.get("forks_count"),
            "open_issues":  data.get("open_issues_count"),
            "default_branch": data.get("default_branch"),
            "last_push":    data.get("pushed_at"),
            "url":          data.get("html_url"),
        }
    return {}


def get_recent_commits(repo: str, limit: int = 5) -> list:
    """Get recent commits"""
    url      = f"{BASE_URL}/repos/{repo}/commits?per_page={limit}"
    response = requests.get(url, headers=HEADERS)
    if response.status_code == 200:
        commits = response.json()
        return [{
            "sha":     c["sha"][:7],
            "message": c["commit"]["message"].split("\n")[0],
            "author":  c["commit"]["author"]["name"],
            "date":    c["commit"]["author"]["date"],
        } for c in commits]
    return []


def get_open_issues(repo: str) -> list:
    """Get open issues"""
    url      = f"{BASE_URL}/repos/{repo}/issues?state=open"
    response = requests.get(url, headers=HEADERS)
    if response.status_code == 200:
        return [{
            "number": i["number"],
            "title":  i["title"],
            "labels": [l["name"] for l in i.get("labels", [])],
            "url":    i["html_url"],
        } for i in response.json() if "pull_request" not in i]
    return []


print("***=== Github functionality load set up ===***")