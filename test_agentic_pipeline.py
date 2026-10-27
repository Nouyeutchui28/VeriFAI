#!/usr/bin/env python3
"""
Test script for the VeriFAI 3-Agent Collaborative Remediation Pipeline.
Demonstrates:
- PlannerAgent (OWASP Triage & Scoping)
- SpecialistAgent (Zetaris Data Fabric & Meterless Nightshift with NVIDIA models)
- EvaluatorAgent (Critic, AST Verification & Dynamic Self-Healing)
- Meterless H-MEM Hierarchical Memory
"""

import os
import sys
from pathlib import Path

# Add project root to sys.path
BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))

from dotenv import load_dotenv
load_dotenv(BASE_DIR / ".env")

from src.core.multi_agent.orchestrator import MultiAgentOrchestrator

def main():
    print("=" * 70)
    print("  VERIFAI AGENTIC PATOPS: 3-AGENT COOPERATIVE VERIFICATION DEMO")
    print("  Sponsor Tech: Zetaris Data Fabric | Meterless Nightshift (NVIDIA) | H-MEM Engine")
    print("=" * 70)

    target_file = str(BASE_DIR / "vuln_test.py")

    # Mock/Parsed Semgrep Finding for vuln_test.py
    findings = [
        {
            "check_id": "python.sqlite3.security.sql-injection",
            "start": {"line": 6, "col": 5},
            "end": {"line": 6, "col": 89},
            "extra": {
                "message": "Detected SQL string formatting in execute call (SQL Injection risk).",
                "severity": "ERROR",
                "metadata": {
                    "cwe": "CWE-89",
                    "owasp": "A03:2021 - Injection"
                }
            }
        }
    ]

    orchestrator = MultiAgentOrchestrator(max_critique_rounds=3)
    pipeline = orchestrator.run_remediation_pipeline(target_file, findings)

    for event in pipeline:
        evt_type = event.get("type")
        if evt_type == "status":
            print(f"\n[STATUS] {event['message']}")
        elif evt_type == "agent_action":
            agent = event.get("agent")
            iter_info = f" (Attempt #{event['iteration']})" if "iteration" in event else ""
            print(f"\n🤖 [{agent}]{iter_info}: {event['message']}")
        elif evt_type == "plan_ready":
            print("\n📋 Execution Plan:")
            for t in event["plan"]["execution_order"]:
                print(f"   • [{t['severity']}] {t['check_id']} -> {t['owasp_category']}")
        elif evt_type == "patch_generated":
            print(f"\n📝 Generated Patch (via {event.get('provider')} - {event.get('model')}):")
            diff = event.get("diff", "")
            if diff:
                for line in diff.splitlines()[:15]:
                    print(f"   {line}")
        elif evt_type == "critique_result":
            status = "✅ APPROVED" if event["approved"] else "❌ REJECTED"
            print(f"\n🧐 [Critic Evaluation] {status} (Score: {event.get('score')}/100)")
            print(f"   Critique: {event.get('critique')}")
        elif evt_type == "self_healing_trigger":
            print(f"   {event['message']}")
        elif evt_type == "workflow_complete":
            print("\n" + "=" * 70)
            print("  PIPELINE COMPLETE - AUDIT SUMMARY")
            print("=" * 70)
            summary = event["summary"]
            print(f"Target File: {summary['target_file']}")
            print(f"Total Tasks: {summary['total_tasks']} | Remediated: {summary['remediated_tasks']}")
            print(f"H-MEM Stored Episodes: {summary['hmem_state']['total_episodes']}")
            print("Audit Telemetry logged to Zetaris Virtual Fabric successfully!")

if __name__ == "__main__":
    main()
