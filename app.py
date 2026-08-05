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
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

* { font-family: 'Inter', sans-serif !important; }

/* ── Background ── */
.stApp { background: #1c1c1e; color: #e5e5e7; }
.block-container { padding-top: 2rem; max-width: 920px; }

section[data-testid="stSidebar"] {
    background: #2c2c2e !important;
    border-right: 1px solid #3a3a3c !important;
}

/* ── Header ── */
.dm-header {
    background: #2c2c2e;
    border: 1px solid #3a3a3c;
    border-radius: 12px;
    padding: 20px 24px;
    margin-bottom: 20px;
    display: flex;
    align-items: center;
    justify-content: space-between;
}
.dm-title {
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 22px !important;
    font-weight: 700 !important;
    color: #ffffff !important;
    margin: 0 !important;
}
.dm-sub {
    font-size: 12px;
    color: #8e8e93;
    margin-top: 4px;
}
.dm-status {
    display: flex;
    align-items: center;
    gap: 8px;
    background: #1c1c1e;
    border: 1px solid #3a3a3c;
    border-radius: 20px;
    padding: 6px 14px;
    font-size: 12px;
    color: #30d158;
    font-family: 'JetBrains Mono', monospace !important;
}
.dm-dot {
    width: 7px; height: 7px;
    background: #30d158;
    border-radius: 50%;
    animation: pulse 2s infinite;
}
@keyframes pulse {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.4; }
}

/* ── Agent Badges ── */
.agent-badge {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding: 4px 12px;
    border-radius: 6px;
    font-size: 11px;
    font-weight: 600;
    margin-bottom: 8px;
    font-family: 'JetBrains Mono', monospace !important;
    letter-spacing: 0.3px;
}
.badge-pr_agent       { background: #1c3a5c; color: #64d2ff; border: 1px solid #2c5282; }
.badge-cicd_agent     { background: #1c3a2c; color: #30d158; border: 1px solid #2c5a3c; }
.badge-infra_agent    { background: #3a2c1c; color: #ffd60a; border: 1px solid #5a4a2c; }
.badge-incident_agent { background: #3a1c1c; color: #ff453a; border: 1px solid #5a2c2c; }

/* ── Severity Pills ── */
.sev-pill {
    display: inline-block;
    padding: 2px 10px;
    border-radius: 20px;
    font-size: 10px;
    font-weight: 600;
    margin-left: 6px;
    font-family: 'JetBrains Mono', monospace !important;
    letter-spacing: 0.5px;
}
.sev-LOW      { background: #1c3a2c; color: #30d158; }
.sev-MEDIUM   { background: #3a3a1c; color: #ffd60a; }
.sev-HIGH     { background: #3a2a1c; color: #ff9f0a; }
.sev-CRITICAL { background: #3a1c1c; color: #ff453a; }

/* ── Chat Bubbles ── */
[data-testid="stChatMessageContent"] {
    background: #2c2c2e !important;
    border: 1px solid #3a3a3c !important;
    border-radius: 10px !important;
    padding: 14px 18px !important;
    font-size: 14px !important;
    line-height: 1.75 !important;
    color: #e5e5e7 !important;
}

/* ── Sidebar ── */
section[data-testid="stSidebar"] > div {
    padding: 1.5rem 1rem !important;
}
section[data-testid="stSidebar"] p,
section[data-testid="stSidebar"] li {
    font-size: 12px !important;
    color: #8e8e93 !important;
    line-height: 1.7 !important;
}
section[data-testid="stSidebar"] h3 {
    font-size: 10px !important;
    color: #636366 !important;
    text-transform: uppercase !important;
    letter-spacing: 1.5px !important;
    font-weight: 600 !important;
    margin-bottom: 10px !important;
}
section[data-testid="stSidebar"] hr {
    border-color: #3a3a3c !important;
    margin: 12px 0 !important;
}

/* ── Metric Cards ── */
[data-testid="stMetric"] {
    background: #1c1c1e !important;
    border: 1px solid #3a3a3c !important;
    border-radius: 8px !important;
    padding: 10px 12px !important;
}
[data-testid="stMetricLabel"] p {
    font-size: 10px !important;
    color: #636366 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.8px !important;
}
[data-testid="stMetricValue"] {
    font-size: 22px !important;
    color: #ffffff !important;
    font-family: 'JetBrains Mono', monospace !important;
}

/* ── Input ── */
textarea[data-testid="stChatInputTextArea"] {
    background: #2c2c2e !important;
    border: 1px solid #3a3a3c !important;
    border-radius: 10px !important;
    color: #e5e5e7 !important;
    font-size: 14px !important;
}
.stChatInputContainer {
    border-top: 1px solid #3a3a3c !important;
    background: #1c1c1e !important;
    padding-top: 12px !important;
}

/* ── Button ── */
.stButton button {
    background: #2c2c2e !important;
    border: 1px solid #3a3a3c !important;
    color: #8e8e93 !important;
    font-size: 11px !important;
    border-radius: 6px !important;
    width: 100% !important;
    font-family: 'JetBrains Mono', monospace !important;
    transition: all 0.2s !important;
}
.stButton button:hover {
    border-color: #636366 !important;
    color: #e5e5e7 !important;
}


/* kill white toolbar */
header[data-testid="stHeader"] {
    background: #1c1c1e !important;
    border-bottom: 1px solid #3a3a3c !important;
}

/* kill white bottom bar */
.stBottom, .stBottom > div {
    background: #1c1c1e !important;
    border-top: 1px solid #3a3a3c !important;
}

/* kill any white gaps */
.stApp > div:first-child {
    background: #1c1c1e !important;
}

/* deploy button area */
[data-testid="stToolbar"] {
    background: #1c1c1e !important;
}

/* main content area top */
[data-testid="stAppViewContainer"] {
    background: #1c1c1e !important;
}

/* chat input bottom container */
[data-testid="stChatInput"] {
    background: #1c1c1e !important;
}

/* scrollbar */
::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: #1c1c1e; }
::-webkit-scrollbar-thumb { background: #3a3a3c; border-radius: 3px; }

/* ── Action caption ── */
.action-line {
    font-family: 'JetBrains Mono', monospace;
    font-size: 11px;
    color: #636366;
    margin-top: 6px;
    padding: 4px 8px;
    background: #1c1c1e;
    border-radius: 4px;
    border-left: 2px solid #3a3a3c;
}

/* ── Example items ── */
.example-item {
    padding: 6px 10px;
    background: #1c1c1e;
    border: 1px solid #3a3a3c;
    border-radius: 6px;
    font-size: 11px;
    color: #8e8e93;
    margin-bottom: 5px;
    cursor: pointer;
    font-family: 'JetBrains Mono', monospace;
}
</style>
""", unsafe_allow_html=True)


# ── Session State ─────────────────────────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []

if "history" not in st.session_state:
    st.session_state.history = []

if "graph" not in st.session_state:
    with st.spinner("Initializing DevMind agents..."):
        st.session_state.graph = build_graph()

if "active_agent" not in st.session_state:
    st.session_state.active_agent = None

if "session_stats" not in st.session_state:
    st.session_state.session_stats = {
        "pr_reviews":   0,
        "cicd_checks":  0,
        "infra_checks": 0,
        "incidents":    0,
    }

# ── Header ────────────────────────────────────────────────────────────────────
repo = os.getenv("GITHUB_REPO", "your-repo")
st.markdown(f"""
<div class="dm-header">
    <div>
        <div class="dm-title">🤖 DevMind</div>
        <div class="dm-sub">AI-Powered DevOps Automation Agent &nbsp;·&nbsp; monitoring <code style="background:#1c1c1e;padding:2px 6px;border-radius:4px;color:#64d2ff;">{repo}</code></div>
    </div>
    <div class="dm-status">
        <div class="dm-dot"></div>
        5 agents online
    </div>
</div>
""", unsafe_allow_html=True)

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:

    st.markdown("### 📊 Session Stats")
    stats = st.session_state.session_stats
    c1, c2 = st.columns(2)
    c1.metric("PR Reviews",   stats["pr_reviews"])
    c2.metric("CI/CD",        stats["cicd_checks"])
    c1.metric("Infra",        stats["infra_checks"])
    c2.metric("Incidents",    stats["incidents"])

    st.divider()

    st.markdown("### 💬 Try These")
    examples = [
        "Review the latest PR",
        "CI/CD pipeline status?",
        "Check infrastructure health",
        "Any active incidents?",
        "Review PR #1",
        "Is the build passing?",
    ]
    for ex in examples:
        st.markdown(
            f'<div class="example-item">→ {ex}</div>',
            unsafe_allow_html=True
        )

    st.divider()

    if st.button("🗑 clear conversation"):
        st.session_state.messages      = []
        st.session_state.history       = []
        st.session_state.active_agent  = None
        st.session_state.session_stats = {
            "pr_reviews": 0, "cicd_checks": 0,
            "infra_checks": 0, "incidents": 0
        }
        st.rerun()

    st.markdown(
        f'<p style="font-size:10px;color:#3a3a3c;margin-top:10px;text-align:center;">'
        f'{len(st.session_state.messages)} messages · DevMind v1.0</p>',
        unsafe_allow_html=True
    )

# ── Agent config ──────────────────────────────────────────────────────────────
AGENT_LABELS = {
    "pr_agent":       "⬡ PR REVIEW",
    "cicd_agent":     "⬡ CI/CD",
    "infra_agent":    "⬡ INFRASTRUCTURE",
    "incident_agent": "⚠ INCIDENT",
}

# ── Render Past Messages ──────────────────────────────────────────────────────
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        if msg["role"] == "assistant":
            agent    = msg.get("agent", "pr_agent")
            severity = msg.get("severity", "LOW")

            st.markdown(
                f'<span class="agent-badge badge-{agent}">'
                f'{AGENT_LABELS.get(agent, "⬡ AGENT")}'
                f'</span>'
                f'<span class="sev-pill sev-{severity}">'
                f'{severity}</span>',
                unsafe_allow_html=True
            )
            st.markdown(msg["content"])

            if msg.get("action"):
                st.markdown(
                    f'<div class="action-line">↳ {msg["action"]}</div>',
                    unsafe_allow_html=True
                )
        else:
            st.markdown(msg["content"])

# ── Chat Input ────────────────────────────────────────────────────────────────
if prompt := st.chat_input("Ask DevMind — review PRs, check pipelines, analyze incidents..."):

    with st.chat_message("user"):
        st.markdown(prompt)

    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("assistant"):
        with st.spinner(""):
            result = run_turn(
                message = prompt,
                history = st.session_state.history,
                graph   = st.session_state.graph,
            )

        agent    = result.get("agent", "pr_agent")
        severity = result.get("severity", "LOW")
        response = result.get("response", "Could not process that request.")
        action   = result.get("action_taken", "")

        st.markdown(
            f'<span class="agent-badge badge-{agent}">'
            f'{AGENT_LABELS.get(agent, "⬡ AGENT")}'
            f'</span>'
            f'<span class="sev-pill sev-{severity}">'
            f'{severity}</span>',
            unsafe_allow_html=True
        )
        st.markdown(response)

        if action:
            st.markdown(
                f'<div class="action-line">↳ {action}</div>',
                unsafe_allow_html=True
            )

    st.session_state.messages.append({
        "role":     "assistant",
        "content":  response,
        "agent":    agent,
        "severity": severity,
        "action":   action,
    })

    stats_map = {
        "pr_agent":       "pr_reviews",
        "cicd_agent":     "cicd_checks",
        "infra_agent":    "infra_checks",
        "incident_agent": "incidents",
    }
    stat_key = stats_map.get(agent)
    if stat_key:
        st.session_state.session_stats[stat_key] += 1

    st.session_state.active_agent = agent
    st.session_state.history.append({"role": "user",      "content": prompt})
    st.session_state.history.append({"role": "assistant", "content": response})

    st.rerun()