import os
import time
import mlflow
from datetime import datetime

os.environ["MLFLOW_TRACKING_URI"] = "mlruns"

mlflow.set_experiment("DevMind-DevOps-Agent")


def track_run(
    message:       str,
    intent:        str,
    agent:         str,
    severity:      str,
    response_time: float,
    incident:      bool,
    action_taken:  str,
) -> None:

    with mlflow.start_run(
        run_name=f"{agent}-{datetime.now().strftime('%H%M%S')}"
    ):
        mlflow.log_params({
            "intent":       intent,
            "agent":        agent,
            "severity":     severity,
            "incident":     incident,
            "query_length": len(message.split()),
        })

        mlflow.log_metrics({
            "response_time_sec": round(response_time, 3),
            "response_length":   len(action_taken.split()),
        })

        mlflow.set_tags({
            "agent":   agent,
            "severity": severity,
            "project": "DevMind",
            "version": "1.0.0",
        })

        log_text = f"""
=== DevMind Run Log ===
Timestamp : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Intent    : {intent}
Agent     : {agent}
Severity  : {severity}
Incident  : {incident}
Resp Time : {round(response_time, 3)}s

Query:
{message}

Action Taken:
{action_taken}
""".strip()

        mlflow.log_text(log_text, artifact_file="run_log.txt")


def run_batch_eval(graph, queries: list = None) -> list:
    from graph import run_turn

    if queries is None:
        queries = [
            "Review the latest PR",
            "What is the CI/CD pipeline status?",
            "Check infrastructure health",
            "Are there any active incidents?",
            "Review PR #1",
            "Is the build passing?",
            "Check server CPU and memory",
            "Any pipeline failures today?",
            "What happened in the last deployment?",
            "Check overall DevOps health",
        ]

    print(f"\n{'='*50}")
    print(f"  DevMind Batch Evaluation — {len(queries)} queries")
    print(f"{'='*50}\n")

    results = []

    for i, query in enumerate(queries, 1):
        print(f"[{i}/{len(queries)}] {query[:50]}...")

        try:
            start  = time.time()
            result = run_turn(message=query, history=[], graph=graph)
            end    = time.time()

            response_time = round(end - start, 3)
            agent         = result.get("agent", "unknown")
            severity      = result.get("severity", "LOW")
            incident      = result.get("incident", False)
            action        = result.get("action_taken", "")

            track_run(
                message       = query,
                intent        = result.get("intent", "unknown"),
                agent         = agent,
                severity      = severity,
                response_time = response_time,
                incident      = incident,
                action_taken  = action,
            )

            results.append({
                "query":         query,
                "agent":         agent,
                "severity":      severity,
                "response_time": response_time,
                "incident":      incident,
            })

            print(f"      → Agent: {agent} | Severity: {severity} | Time: {response_time}s")

        except Exception as e:
            print(f"      ✗ Error: {e}")

    # summary
    print(f"\n{'='*50}")
    print("  Batch Evaluation Complete")
    print(f"{'='*50}")

    agent_counts = {}
    total_time   = 0
    for r in results:
        agent_counts[r["agent"]] = agent_counts.get(r["agent"], 0) + 1
        total_time += r["response_time"]

    print("\nAgent Distribution:")
    for agent, count in agent_counts.items():
        pct = round(count / len(results) * 100, 1)
        print(f"  {agent:20} → {count} queries ({pct}%)")

    print(f"\nAvg Response Time : {round(total_time / len(results), 3)}s")
    print(f"Total Queries     : {len(results)}")
    print(f"\nView results: mlflow ui")
    print(f"{'='*50}\n")

    return results


if __name__ == "__main__":
    from graph import build_graph
    graph = build_graph()
    run_batch_eval(graph)
