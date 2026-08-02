from core import DevMindState, call_llm
from tools.github_tool import (
    get_latest_pr, get_pr_diff, get_pr_details,
    post_pr_comment, get_open_prs
)
from tools.slack_tool import send_pr_notification

SYSTEM_PROMPT = """You are DevMind — an expert AI code reviewer for a DevOps team.

You review pull requests professionally and constructively.

Your review must include:
1. **Summary** — What does this PR do? (1-2 sentences)
2. **Code Quality** — Is the code clean, readable, maintainable?
3. **Potential Issues** — Bugs, edge cases, security concerns
4. **Suggestions** — Specific improvements with line references
5. **Decision** — APPROVE ✅ or REQUEST CHANGES ❌

Rules:
- Be specific — reference actual code from the diff
- Be constructive — explain WHY something is an issue
- Be concise — max 400 words
- Always end with APPROVE or REQUEST CHANGES"""


def node_pr_agent(state: DevMindState) -> DevMindState:
    repo      = state["repo"]
    message   = state["message"]
    history   = state["history"]
    pr_number = state.get("pr_number")

    print(f" PR Agent → reviewing PR #{pr_number or 'latest'}")

    # get PR details
    if pr_number:
        pr      = get_pr_details(repo, pr_number)
        diff    = get_pr_diff(repo, pr_number)
    else:
        pr = get_latest_pr(repo)
        if not pr:
            return {
                **state,
                "response":     "No open pull requests found in the repository.",
                "action_taken": "no_prs_found",
                "agent":        "pr_agent",
            }
        pr_number = pr["number"]
        diff      = get_pr_diff(repo, pr_number)

    # build context for LLM
    context = f"""
PR #{pr_number}: {pr.get('title', 'Unknown')}
Author: {pr.get('user', {}).get('login', 'Unknown')}
Branch: {pr.get('head', {}).get('ref', 'Unknown')} → {pr.get('base', {}).get('ref', 'main')}
Description: {pr.get('body', 'No description provided')}

CODE DIFF:
{diff if diff else 'No diff available'}
"""

    # get AI review
    review = call_llm(
        system_prompt = SYSTEM_PROMPT,
        user_message  = f"Review this pull request: {message}",
        context       = context,
        history       = history,
    )

    # post comment to GitHub
    pr_url     = pr.get("html_url", "")
    commented  = post_pr_comment(repo, pr_number, review)

    # notify Slack
    send_pr_notification(
        pr_number      = pr_number,
        repo           = repo,
        review_summary = review[:300],
        url            = pr_url,
    )

    action = f"Reviewed PR #{pr_number}, posted comment: {commented}"
    print(f" ==> PR Agent → {action}")

    return {
        **state,
        "github_data":  {"pr": pr, "diff_length": len(diff)},
        "analysis":     review,
        "action_taken": action,
        "notification": f"PR #{pr_number} review posted to GitHub and Slack",
        "response":     f"**PR #{pr_number} Review Complete**\n\n{review}",
        "agent":        "pr_agent",
    }
