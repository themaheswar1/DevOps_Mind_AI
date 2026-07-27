import os
from groq import Groq
from dotenv import load_dotenv
from typing import TypedDict, List, Optional

load_dotenv()

# ── Constants ─────────────────────────────────────────────────────────────────
GROQ_MODEL    = "llama-3.3-70b-versatile"
GITHUB_REPO   = os.getenv("GITHUB_REPO", "themaheswar1/shopsmart-ecommerce-api")
GITHUB_TOKEN  = os.getenv("GITHUB_TOKEN")
SLACK_WEBHOOK = os.getenv("SLACK_WEBHOOK_URL")
GROQ_API_KEY  = os.getenv("GROQ_API_KEY")

# ── Groq Client ───────────────────────────────────────────────────────────────
client = Groq(api_key=GROQ_API_KEY)


# ── Shared State ──────────────────────────────────────────────────────────────
class DevMindState(TypedDict):
    message:      str
    intent:       str
    repo:         str
    pr_number:    Optional[int]
    github_data:  dict
    analysis:     str
    action_taken: str
    notification: str
    incident:     bool
    severity:     str
    history:      List[dict]
    response:     str


# ── LLM Call ──────────────────────────────────────────────────────────────────
def call_llm(system_prompt: str, user_message: str,
             context: str = "", history: list = []) -> str:

    messages = [{"role": "system", "content": system_prompt}]

    for msg in history[-6:]:
        messages.append(msg)

    if context:
        user_message = f"Context:\n{context}\n\nRequest: {user_message}"

    messages.append({"role": "user", "content": user_message})

    response = client.chat.completions.create(
        model       = GROQ_MODEL,
        messages    = messages,
        temperature = 0.3,
        max_tokens  = 1024,
    )
    return response.choices[0].message.content.strip()


# ── Intent Detection ──────────────────────────────────────────────────────────
def detect_intent(message: str) -> str:

    SYSTEM_PROMPT = """You are a DevOps intent classifier.
Classify the message into exactly one intent:

- pr_review      → review PR, check pull request, code review
- cicd_status    → pipeline status, build status, CI/CD, tests
- infra_health   → infrastructure, server health, CPU, memory
- incident_check → incidents, outages, failures, alerts
- general        → anything else

Reply with ONLY the intent name. Nothing else."""

    response = client.chat.completions.create(
        model    = GROQ_MODEL,
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user",   "content": message}
        ],
        temperature = 0.0,
        max_tokens  = 10,
    )
    intent = response.choices[0].message.content.strip().lower()
    valid  = ["pr_review", "cicd_status", "infra_health",
              "incident_check", "general"]
    return intent if intent in valid else "general"


# ── Initial State Builder ─────────────────────────────────────────────────────
def build_initial_state(message: str, history: list = []) -> DevMindState:
    return DevMindState(
        message      = message,
        intent       = "",
        repo         = GITHUB_REPO,
        pr_number    = None,
        github_data  = {},
        analysis     = "",
        action_taken = "",
        notification = "",
        incident     = False,
        severity     = "LOW",
        history      = history,
        response     = "",
    )


print("✅ DevMind Core loaded")
