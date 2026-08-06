# DevOpsMind — AI-Powered DevOps Agent

```
██████╗ ███████╗██╗   ██╗███╗   ███╗██╗███╗   ██╗██████╗ 
██╔══██╗██╔════╝██║   ██║████╗ ████║██║████╗  ██║██╔══██╗
██║  ██║█████╗  ██║   ██║██╔████╔██║██║██╔██╗ ██║██║  ██║
██║  ██║██╔══╝  ╚██╗ ██╔╝██║╚██╔╝██║██║██║╚██╗██║██║  ██║
██████╔╝███████╗ ╚████╔╝ ██║ ╚═╝ ██║██║██║ ╚████║██████╔╝
╚═════╝ ╚══════╝  ╚═══╝  ╚═╝     ╚═╝╚═╝╚═╝  ╚═══╝╚═════╝ 
```

**Not a monitoring dashboard. Not a chatbot. An agent that actually does things.**

![Python](https://img.shields.io/badge/Python-3.13-3776AB?style=flat-square&logo=python&logoColor=white)
![LangGraph](https://img.shields.io/badge/LangGraph-1.0.10-FF6B35?style=flat-square)
![Groq](https://img.shields.io/badge/Groq-llama--3.3--70b-F55036?style=flat-square)
![Streamlit](https://img.shields.io/badge/Streamlit-1.45-FF4B4B?style=flat-square&logo=streamlit&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-Containerized-2496ED?style=flat-square&logo=docker&logoColor=white)
![MLflow](https://img.shields.io/badge/MLflow-3.10-0194E2?style=flat-square&logo=mlflow&logoColor=white)
![CI](https://github.com/themaheswar1/DevOps_Mind_AI/actions/workflows/ci.yml/badge.svg)

---

## What is DevMind?

Most "AI DevOps tools" are dashboards with a chatbot bolted on.

DevMind is different. It's a **multi-agent system** where each agent has a specific job, real tool access, and the ability to take action — not just report.

```
You ask:  "Review the latest PR"

DevMind:  → Calls GitHub API to fetch the PR diff
          → Sends diff to Groq LLM for expert code review
          → Posts the review comment directly on the PR
          → Notifies your Slack channel
          → Logs the entire interaction to MLflow

You didn't click anything. DevMind did it.
```

---

## Try DevOps Mind

> 🚀 **[Launch DevMind →](https://your-deployment-link)**
>
> *First load takes ~30 seconds. 5 agents initializing.*

---

## Architecture

```
                    ┌─────────────────────┐
  User Input ──────▶│   ORCHESTRATOR      │
                    │  intent detection   │
                    │  + PR extraction    │
                    └──────────┬──────────┘
                               │
              ┌────────────────┼───────────────┬──────────────┐
              ▼                ▼               ▼              ▼
       ┌──────────┐    ┌──────────┐    ┌──────────┐   ┌─────────────┐
       │    PR    │    │  CI/CD   │    │  INFRA   │   │  INCIDENT   │
       │  REVIEW  │    │ MONITOR  │    │  HEALTH  │   │  DETECTION  │
       │  AGENT   │    │  AGENT   │    │  AGENT   │   │   AGENT     │
       └────┬─────┘    └────┬─────┘    └────┬─────┘   └──────┬──────┘
            │               │               │                 │
            ▼               ▼               ▼                 ▼
       GitHub API    GitHub Actions    GCP Metrics      GitHub API
       PR Diff       Pipeline Runs     Health Report    Jira Tickets
       Post Comment  Failed Steps      Anomaly Alert    Slack Alerts
            │               │               │                 │
            └───────────────┴───────────────┴─────────────────┘
                                    │
                         ┌──────────▼──────────┐
                         │  NOTIFICATION AGENT  │
                         │   Slack · GitHub     │
                         └─────────────────────┘
```

---

## The 5 Agents

### 🔍 PR Review Agent
Reads the actual code diff from GitHub, sends it to Groq LLM for expert review, and posts the review comment directly on the pull request.

**Tools:** GitHub API (diff fetch + comment post) · Groq LLM
**Output:** Review comment on PR + Slack notification

### ⚙️ CI/CD Monitor Agent
Watches GitHub Actions pipelines in real time. When a build fails, it tells you exactly which step failed and why, then suggests the fix.

**Tools:** GitHub Actions API (workflow runs + job steps) · Groq LLM
**Output:** Pipeline report + failure analysis + Slack alert

### 🏗️ Infrastructure Agent
Monitors server health — CPU, memory, disk, response time, error rate. Detects anomalies and generates actionable reports with GREEN / YELLOW / RED status.

**Tools:** GCP Monitoring API · Groq LLM
**Output:** Health report with severity classification

### 🚨 Incident Detection Agent
Correlates signals across all tools. Pipeline failure + infrastructure spike = incident. Auto-creates a Jira ticket and dispatches a full incident response plan.

**Tools:** GitHub API · Jira API · Slack · Groq LLM
**Output:** Jira ticket + Slack incident alert + response plan

### 📢 Notification Agent
The communication layer. Every other agent routes through here. Formats alerts by severity and routes to the right Slack channel.

**Tools:** Slack Webhooks
**Output:** Formatted Slack messages with severity context

---

## Benchmark Results

Evaluated across **10 real DevOps queries** against a live GitHub repository:

| Metric | Value |
|--------|-------|
| Total queries evaluated | 10 |
| Avg end-to-end response time | 6.9s |
| PR reviews posted to GitHub | ✅ Real API calls |
| Slack notifications sent | ✅ Real webhooks |
| MLflow experiment runs logged | 10 |
| Agent routing accuracy | 100% |

**Agent distribution across query types:**

```
CI/CD Agent      ████████████████░░░░░░░░  40%
Infra Agent      ████████████░░░░░░░░░░░░  30%
PR Review Agent  ████████░░░░░░░░░░░░░░░░  20%
Incident Agent   ████░░░░░░░░░░░░░░░░░░░░  10%
```

---

## Tool Integrations

| Tool | Purpose | Type |
|------|---------|------|
| GitHub API | PR diffs, pipeline runs, issue creation | Real |
| GitHub Actions | CI/CD workflow monitoring | Real |
| Slack Webhooks | Team notifications | Real |
| Jira REST API | Incident ticket creation | Simulated* |
| Docker Hub API | Container image monitoring | Real |
| Groq LLM | All AI analysis and generation | Real |

*Jira simulated via adapter pattern — swap implementation without touching agent code*

---

## Tech Stack

```
Agent Orchestration  →  LangGraph 1.0.10
LLM                  →  Groq · llama-3.3-70b-versatile
Tool Layer           →  GitHub API · Slack · Jira · Docker Hub
Experiment Tracking  →  MLflow 3.10
UI                   →  Streamlit 1.45
Containerization     →  Docker + Docker Compose
CI/CD                →  GitHub Actions
Deployment           →  GCP Cloud Run
```

---

## Project Structure

```
DevOps_Mind_AI/
│
├── agents/
│   ├── orchestrator.py       # intent detection + routing
│   ├── pr_agent.py           # GitHub PR review
│   ├── cicd_agent.py         # pipeline monitoring
│   ├── infra_agent.py        # infrastructure health
│   ├── incident_agent.py     # incident detection + Jira
│   └── notification_agent.py # Slack coordination
│
├── tools/
│   ├── github_tool.py        # GitHub API wrapper
│   ├── slack_tool.py         # Slack webhooks
│   ├── jira_tool.py          # Jira ticket creation
│   └── docker_tool.py        # Docker Hub API
│
├── core.py                   # LLM client · state schema · intent detection
├── graph.py                  # LangGraph orchestration
├── app.py                    # Streamlit dashboard
├── eval.py                   # MLflow batch evaluation
├── Dockerfile
├── docker-compose.yml
└── .github/workflows/ci.yml  # GitHub Actions CI
```

---

## Quickstart

```bash
git clone https://github.com/themaheswar1/DevOps_Mind_AI.git
cd DevOps_Mind_AI

python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env
# fill in your keys

streamlit run app.py
```

### Environment Variables

```bash
GROQ_API_KEY=your_groq_api_key
GITHUB_TOKEN=your_github_token
GITHUB_REPO=owner/repository-to-monitor
SLACK_WEBHOOK_URL=your_slack_webhook
```

### Docker

```bash
docker compose up --build
# open http://localhost:8501
```

### Run Batch Evaluation

```bash
python eval.py
mlflow ui   # open http://localhost:5000
```

---

## Git Branching Strategy

```
master        →  production · always stable
dev           →  integration branch
feature/xxx   →  individual feature branches

feature/* → dev → master
```

---

## Roadmap

- [x] 5-agent LangGraph orchestration
- [x] Real GitHub API integration
- [x] Real Slack notifications
- [x] MLflow experiment tracking
- [x] Docker containerization
- [x] GCP Cloud Run deployment
- [ ] GitHub webhook auto-trigger on PR open
- [ ] Multi-repo monitoring
- [ ] PagerDuty integration for on-call alerts
- [ ] Slack slash command interface

---

## Author

**Mahesh** — [@themaheswar1](https://github.com/themaheswar1)

Built as Project 2 of 3 in an AI Engineering portfolio series.
Project 1 → [Multi-Agent Customer Support System](https://github.com/themaheswar1/Multi-Agent-Customer-Support-System)

---

*Built by someone who believed agents should do things, not just talk about them.*
