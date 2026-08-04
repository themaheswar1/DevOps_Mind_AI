import streamlit as st
from graph import build_graph, run_turn
import os

st.set_page_config(
    page_title = "DevMind — AI DevOps Agent",
    page_icon  = "🛜",
    layout     = "wide"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600&family=Space+Mono&display=swap');

* { font-family: 'Inter', sans-serif !important; }

.stApp { background: #0a0a0f; color: #e0e0e0; }
.block-container { padding-top: 1.5rem; }

.agent-badge {
    display: inline-block;
    padding: 3px 12px;
    border-radius: 20px;
    font-size: 11px;
    font-weight: 600;
    margin-bottom: 8px;
    letter-spacing: 0.5px;
}
.badge-pr_agent       { background: #0d1f35; color: #4a9eca; border: 1px solid #1a3a5c; }
.badge-cicd_agent     { background: #0d2a1a; color: #4aca7e; border: 1px solid #1a4a2e; }
.badge-infra_agent    { background: #2a1a0d; color: #ca9a4a; border: 1px solid #4a3a1a; }
.badge-incident_agent { background: #2a0d0d; color: #ca4a4a; border: 1px solid #4a1a1a; }

.severity-pill {
    display: inline-block;
    padding: 2px 8px;
    border-radius: 10px;
    font-size: 10px;
    margin-left: 8px;
}
.pill-LOW      { background: #0d2a1a; color: #4aca7e; }
.pill-MEDIUM   { background: #2a2a0d; color: #caaa4a; }
.pill-HIGH     { background: #2a1a0d; color: #ca7a4a; }
.pill-CRITICAL { background: #2a0d0d; color: #ca4a4a; }

.metric-card {
    background: #111118;
    border: 1px solid #1e1e2e;
    border-radius: 8px;
    padding: 16px;
    margin-bottom: 8px;
}

.agent-card {
    padding: 8px 12px;
    border-radius: 6px;
    margin-bottom: 6px;
    border: 1px solid #1e1e2e;
    font-size: 12px;
}
.agent-card.active {
    border-color: #2e6da4;
    background: #0d1f35;
}
.dot {
    display: inline-block;
    width: 7px; height: 7px;
    border-radius: 50%;
    margin-right: 6px;
}
.dot-idle   { background: #333; }
.dot-active { background: #4aca7e; animation: blink 1s infinite; }

@keyframes blink {
    0%, 100% { opacity: 1; }
    50%       { opacity: 0.2; }
}

section[data-testid="stSidebar"] {
    background: #0d0d14 !important;
    border-right: 1px solid #1a1a2e !important;
}

[data-testid="stChatMessageContent"] {
    background: #111118 !important;
    border: 1px solid #1e1e2e !important;
    border-radius: 8px !important;
}
</style>
""", unsafe_allow_html=True)


# ── Header ────────────────────────────────────────────────────────────────────
col1, col2 = st.columns([3, 1])
with col1:
    st.markdown("## 🛜 DevMind")
    st.caption(f"AI-Powered DevOps Agent · Monitoring `{os.getenv('GITHUB_REPO', 'your-repo')}`")
with col2:
    st.markdown("")
    repo_info_placeholder = st.empty()

st.divider()

# ── Session State ─────────────────────────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []

if "history" not in st.session_state:
    st.session_state.history = []

if "graph" not in st.session_state:
    status = st.status("🗽 Starting DevMind...", expanded=True)
    with status:
        st.write("🔗 Connecting to GitHub API...")
        st.write("🤖 Loading Groq LLM...")
        st.write("🕸️ Building LangGraph pipeline...")
        st.write("⚙️ Wiring 5 agents...")
        st.write("📢 Connecting Slack webhook...")
        st.session_state.graph = build_graph()
        status.update(
            label    = " DevMind online — 5 agents ready",
            state    = "complete",
            expanded = False
        )

if "active_agent" not in st.session_state:
    st.session_state.active_agent = None

if "session_stats" not in st.session_state:
    st.session_state.session_stats = {
        "pr_reviews":  0,
        "cicd_checks": 0,
        "infra_checks": 0,
        "incidents":   0,
    }

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 🤖 Agent System")
    st.caption("last active agent highlighted")
    st.markdown("")

    agents = [
        {"key": "pr_agent",       "icon": "🔍", "name": "PR Review Agent",
         "desc": "Code review · PR comments · Approval"},
        {"key": "cicd_agent",     "icon": "⚙️", "name": "CI/CD Agent",
         "desc": "Pipeline · Build status · Failures"},
        {"key": "infra_agent",    "icon": "🏗️", "name": "Infrastructure Agent",
         "desc": "CPU · Memory · Uptime · Health"},
        {"key": "incident_agent", "icon": "🚨", "name": "Incident Agent",
         "desc": "Incidents · Jira tickets · Alerts"},
    ]

    for ag in agents:
        is_active  = st.session_state.active_agent == ag["key"]
        card_class = "agent-card active" if is_active else "agent-card"
        dot_class  = "dot dot-active" if is_active else "dot dot-idle"

        st.markdown(f"""
        <div class="{card_class}">
            <span class="{dot_class}"></span>
            <strong>{ag['icon']} {ag['name']}</strong>
            <div style="font-size:10px;color:#555;margin-top:2px;">{ag['desc']}</div>
            {"<div style='font-size:10px;color:#2e6da4;margin-top:3px;'>▶ handled last message</div>" if is_active else ""}
        </div>
        """, unsafe_allow_html=True)

    st.divider()

    st.markdown("### 💬 Try These")
    examples = [
        "Review the latest PR",
        "What is the CI/CD pipeline status?",
        "Check infrastructure health",
        "Any active incidents?",
        "Review PR #3",
    ]
    for ex in examples:
        st.markdown(f"→ *{ex}*")

    st.divider()
    st.markdown("### 📊 Session Stats")

    stats = st.session_state.session_stats
    c1, c2 = st.columns(2)
    c1.metric("PR Reviews",   stats["pr_reviews"])
    c2.metric("CI/CD Checks", stats["cicd_checks"])
    c1.metric("Infra Checks", stats["infra_checks"])
    c2.metric("Incidents",    stats["incidents"])

    st.divider()

    if st.button("🗑️ Clear Chat"):
        st.session_state.messages      = []
        st.session_state.history       = []
        st.session_state.active_agent  = None
        st.session_state.session_stats = {
            "pr_reviews": 0, "cicd_checks": 0,
            "infra_checks": 0, "incidents": 0
        }
        st.rerun()

# ── Render Past Messages ──────────────────────────────────────────────────────
AGENT_LABELS = {
    "pr_agent":       "🔍 PR Review Agent",
    "cicd_agent":     "⚙️ CI/CD Agent",
    "infra_agent":    "🏗️ Infrastructure Agent",
    "incident_agent": "🚨 Incident Agent",
}

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        if msg["role"] == "assistant":
            agent    = msg.get("agent", "pr_agent")
            severity = msg.get("severity", "LOW")

            st.markdown(
                f'<span class="agent-badge badge-{agent}">'
                f'{AGENT_LABELS.get(agent, "🤖 Agent")}'
                f'</span>'
                f'<span class="severity-pill pill-{severity}">'
                f'{severity}</span>',
                unsafe_allow_html=True
            )
            st.markdown(msg["content"])

            if msg.get("action"):
                st.caption(f"🔧 {msg['action']}")
        else:
            st.markdown(msg["content"])

# ── Chat Input ────────────────────────────────────────────────────────────────
if prompt := st.chat_input("Ask DevMind anything — review PRs, check pipelines, analyze incidents..."):

    with st.chat_message("user"):
        st.markdown(prompt)

    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("assistant"):
        with st.spinner("🤔 DevMind is analyzing..."):
            result = run_turn(
                message = prompt,
                history = st.session_state.history,
                graph   = st.session_state.graph,
            )

        agent    = result.get("agent", "pr_agent")
        severity = result.get("severity", "LOW")
        response = result.get("response", "I couldn't process that request.")
        action   = result.get("action_taken", "")

        st.markdown(
            f'<span class="agent-badge badge-{agent}">'
            f'{AGENT_LABELS.get(agent, "🤖 Agent")}'
            f'</span>'
            f'<span class="severity-pill pill-{severity}">'
            f'{severity}</span>',
            unsafe_allow_html=True
        )
        st.markdown(response)

        if action:
            st.caption(f"🔧 {action}")

    # save message
    st.session_state.messages.append({
        "role":     "assistant",
        "content":  response,
        "agent":    agent,
        "severity": severity,
        "action":   action,
    })

    # update stats
    stats_map = {
        "pr_agent":       "pr_reviews",
        "cicd_agent":     "cicd_checks",
        "infra_agent":    "infra_checks",
        "incident_agent": "incidents",
    }
    stat_key = stats_map.get(agent)
    if stat_key:
        st.session_state.session_stats[stat_key] += 1

    # update active agent + history
    st.session_state.active_agent = agent
    st.session_state.history.append({"role": "user",      "content": prompt})
    st.session_state.history.append({"role": "assistant", "content": response})

    st.rerun()
