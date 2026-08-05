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
.block-container { padding-top: 1.5rem; max-width: 900px; }

/* header */
.devmind-header {
    padding: 20px 0 10px 0;
    border-bottom: 1px solid #1a1a2e;
    margin-bottom: 20px;
}
.devmind-title {
    font-family: 'Space Mono', monospace !important;
    font-size: 24px !important;
    font-weight: 700 !important;
    color: #ffffff !important;
    margin: 0 !important;
    letter-spacing: -0.5px;
}
.devmind-subtitle {
    font-size: 12px;
    color: #444;
    margin-top: 4px;
    font-family: 'Space Mono', monospace !important;
}

/* agent badges */
.agent-badge {
    display: inline-block;
    padding: 3px 12px;
    border-radius: 4px;
    font-size: 11px;
    font-weight: 600;
    margin-bottom: 8px;
    letter-spacing: 0.5px;
    font-family: 'Space Mono', monospace !important;
}
.badge-pr_agent       { background: #0d1f35; color: #4a9eca; border: 1px solid #1a3a5c; }
.badge-cicd_agent     { background: #0d2a1a; color: #4aca7e; border: 1px solid #1a4a2e; }
.badge-infra_agent    { background: #2a1a0d; color: #ca9a4a; border: 1px solid #4a3a1a; }
.badge-incident_agent { background: #2a0d0d; color: #ca4a4a; border: 1px solid #4a1a1a; }

/* severity pill */
.severity-pill {
    display: inline-block;
    padding: 2px 8px;
    border-radius: 4px;
    font-size: 10px;
    margin-left: 8px;
    font-family: 'Space Mono', monospace !important;
}
.pill-LOW      { background: #0d2a1a; color: #4aca7e; }
.pill-MEDIUM   { background: #2a2a0d; color: #caaa4a; }
.pill-HIGH     { background: #2a1a0d; color: #ca7a4a; }
.pill-CRITICAL { background: #2a0d0d; color: #ca4a4a; }

/* chat messages */
[data-testid="stChatMessageContent"] {
    background: #111118 !important;
    border: 1px solid #1e1e2e !important;
    border-radius: 6px !important;
    padding: 14px 16px !important;
    font-size: 14px !important;
    line-height: 1.7 !important;
}

/* sidebar */
section[data-testid="stSidebar"] {
    background: #0d0d14 !important;
    border-right: 1px solid #1a1a2e !important;
}
section[data-testid="stSidebar"] > div {
    padding-top: 1.5rem !important;
}
section[data-testid="stSidebar"] p,
section[data-testid="stSidebar"] li {
    font-size: 12px !important;
    color: #666 !important;
    line-height: 1.6 !important;
}
section[data-testid="stSidebar"] h3 {
    font-size: 10px !important;
    color: #444 !important;
    text-transform: uppercase !important;
    letter-spacing: 1.5px !important;
    font-weight: 600 !important;
    margin-bottom: 8px !important;
}

/* metric cards */
[data-testid="stMetric"] {
    background: #111118 !important;
    border: 1px solid #1e1e2e !important;
    border-radius: 6px !important;
    padding: 10px !important;
}
[data-testid="stMetricLabel"] {
    font-size: 10px !important;
    color: #555 !important;
}
[data-testid="stMetricValue"] {
    font-size: 20px !important;
    color: #fff !important;
    font-family: 'Space Mono', monospace !important;
}

/* input */
textarea[data-testid="stChatInputTextArea"] {
    background: #111118 !important;
    border: 1px solid #1e1e2e !important;
    border-radius: 6px !important;
    color: #ddd !important;
    font-size: 13px !important;
}

/* clear button */
.stButton button {
    background: transparent !important;
    border: 1px solid #222 !important;
    color: #555 !important;
    font-size: 11px !important;
    border-radius: 4px !important;
    font-family: 'Space Mono', monospace !important;
}
.stButton button:hover {
    border-color: #444 !important;
    color: #888 !important;
}

/* divider */
hr { border-color: #1a1a2e !important; }
</style>
""", unsafe_allow_html=True)


# Header
st.markdown(f"""
<div class="devmind-header">
    <div class="devmind-title">🤖 DevMind</div>
    <div class="devmind-subtitle">
        AI-Powered DevOps Agent &nbsp;·&nbsp;
        monitoring <code>{os.getenv('GITHUB_REPO', 'your-repo')}</code>
    </div>
</div>
""", unsafe_allow_html=True)

# Session State
if "messages" not in st.session_state:
    st.session_state.messages = []

if "history" not in st.session_state:
    st.session_state.history = []

if "graph" not in st.session_state:
    with st.spinner("Loading DevMind agents..."):
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

# Sidebar
with st.sidebar:

    # Session Stats
    st.markdown("### Session Stats")
    stats = st.session_state.session_stats
    c1, c2 = st.columns(2)
    c1.metric("PR Reviews",   stats["pr_reviews"])
    c2.metric("CI/CD Checks", stats["cicd_checks"])
    c1.metric("Infra Checks", stats["infra_checks"])
    c2.metric("Incidents",    stats["incidents"])

    st.divider()

    # Try These 
    st.markdown("### Try These")
    st.markdown("""
- Review the latest PR
- What is the CI/CD pipeline status?
- Check infrastructure health
- Any active incidents?
- Review PR #3
- Is the build passing?
""")

    st.divider()

    # Clear 
    if st.button("clear conversation"):
        st.session_state.messages      = []
        st.session_state.history       = []
        st.session_state.active_agent  = None
        st.session_state.session_stats = {
            "pr_reviews": 0, "cicd_checks": 0,
            "infra_checks": 0, "incidents": 0
        }
        st.rerun()

    st.markdown(
        f'<p style="font-size:10px;color:#333;margin-top:8px;">'
        f'{len(st.session_state.messages)} messages this session</p>',
        unsafe_allow_html=True
    )

# Agent Labels
AGENT_LABELS = {
    "pr_agent":       "◈ PR REVIEW",
    "cicd_agent":     "◉ CI/CD",
    "infra_agent":    "◈ INFRASTRUCTURE",
    "incident_agent": "⚠ INCIDENT",
}

# Render Past Messages
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        if msg["role"] == "assistant":
            agent    = msg.get("agent", "pr_agent")
            severity = msg.get("severity", "LOW")

            st.markdown(
                f'<span class="agent-badge badge-{agent}">'
                f'{AGENT_LABELS.get(agent, "◈ AGENT")}'
                f'</span>'
                f'<span class="severity-pill pill-{severity}">'
                f'{severity}</span>',
                unsafe_allow_html=True
            )
            st.markdown(msg["content"])

            if msg.get("action"):
                st.caption(f"↳ {msg['action']}")
        else:
            st.markdown(msg["content"])

# Chat Input 
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
        response = result.get("response", "I could not process that request.")
        action   = result.get("action_taken", "")

        st.markdown(
            f'<span class="agent-badge badge-{agent}">'
            f'{AGENT_LABELS.get(agent, "◈ AGENT")}'
            f'</span>'
            f'<span class="severity-pill pill-{severity}">'
            f'{severity}</span>',
            unsafe_allow_html=True
        )
        st.markdown(response)

        if action:
            st.caption(f"↳ {action}")

    # save
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

    st.session_state.active_agent = agent
    st.session_state.history.append({"role": "user",      "content": prompt})
    st.session_state.history.append({"role": "assistant", "content": response})

    st.rerun()