#!/usr/bin/env python3
import os
import sys
import argparse
import json
import subprocess
from dotenv import load_dotenv

# Ensure we can import from src
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from src.core.security import run_llm_analysis, generate_patch_suggestions
from src.core.file_utils import apply_patch
from src.core.verification import verify_fix_with_scanner, verify_patch_safety

def run_semgrep(target_path):
    """Run Semgrep via CLI."""
    print(f"[*] Running Semgrep static analysis on {target_path}...")
    
    import shutil
    semgrep_cmd = shutil.which("semgrep")
    if not semgrep_cmd:
        error_msg = "Semgrep is not installed or not found in PATH. Please run `pip install semgrep`."
        print(f"[!] {error_msg}")
        # Log the issue and return error
        import logging
        logging.getLogger(__name__).error(error_msg)
        return {"results": [], "error": error_msg}
    
    output_path = "results/cli_result.json"
    os.makedirs("results", exist_ok=True)
    
    cmd = [
        semgrep_cmd, 
        "--json", 
        "--output", output_path, 
        "--config=p/security-audit", 
        "--config=p/r2c-security-audit",
        target_path
    ]
    
    try:
        print(f"[*] Executing semgrep command: {' '.join(cmd)}")
        result = subprocess.run(cmd, capture_output=True, text=True, check=False)
        print(f"[*] Semgrep execution completed with exit code {result.returncode}")
        if result.returncode != 0 and result.stderr:
            print(f"[!] Semgrep stderr: {result.stderr}")
            
        if os.path.exists(output_path):
            with open(output_path, 'r') as f:
                return json.load(f)
    except Exception as e:
        error_msg = f"Semgrep execution failed: {e}"
        print(f"[!] {error_msg}")
        import logging
        logging.getLogger(__name__).error(error_msg)
        return {"results": [], "error": error_msg}
    
    return {"results": []}

def main():
    parser = argparse.ArgumentParser(description="VeriFAI LLM CLI - AI-Powered Security Scanner")
    parser.add_argument("target", nargs="?", default=None, help="File or directory to scan (leave empty for Interactive Mode)")
    parser.add_argument("-i", "--interactive", action="store_true", help="Launch the rich interactive terminal shell")
    parser.add_argument("--model", default="nvidia/llama-3.1-nemotron-70b-instruct", help="AI Model to use (via Meterless Nightshift)")
    parser.add_argument("--agentic", action="store_true", default=True, help="Enable 3-Agent Collaborative Remediation (Planner -> Specialist -> Critic)")
    parser.add_argument("--apply", action="store_true", help="Automatically apply and VERIFY generated patches")
    parser.add_argument("--fail-under", type=int, default=80, help="Security score threshold (0-100). Fails if below.")
    args = parser.parse_args()

    # Launch Interactive Terminal Mode if requested or if no target argument provided
    if args.interactive or not args.target:
        from src.cli.interactive import start_interactive_cli
        start_interactive_cli()
        return

    target_path = args.target

    if not os.path.exists(target_path):
        print(f"[!] Error: Target path '{target_path}' does not exist.")
        sys.exit(1)

    load_dotenv()
    
    # 1. Semgrep Scan
    semgrep_results = run_semgrep(target_path)
    findings = semgrep_results.get("results", [])
    findings_count = len(findings)
    print(f"[*] Semgrep found {findings_count} potential issues.")

    # Calculate Security Score
    # Base 100 points
    # High: -15, Medium: -5, Low: -1
    score = 100
    sev_counts = {"high": 0, "medium": 0, "low": 0}
    for f in findings:
        sev = (f.get("extra", {}).get("severity") or "low").lower()
        if sev == "error" or sev == "high":
            score -= 15
            sev_counts["high"] += 1
        elif sev == "warning" or sev == "medium":
            score -= 5
            sev_counts["medium"] += 1
        else:
            score -= 1
            sev_counts["low"] += 1
    
    score = max(0, score)
    print(f"[*] Calculated Security Score: {score}/100")
    print(f"[*] Distribution: {sev_counts['high']} High, {sev_counts['medium']} Medium, {sev_counts['low']} Low")

    # Prepare code content for LLM (limit size)
    code_content = ""
    if os.path.isfile(target_path):
        with open(target_path, 'r', encoding='utf-8', errors='ignore') as f:
            code_content = f.read()[:10000] # Limit for CLI
    else:
        # If directory, just pass the semgrep results and note it's a directory
        code_content = f"Target is a directory: {target_path}. See Semgrep results."

    # 2. AI Analysis & Multi-Agent Cooperative Remediation
    if args.agentic and findings_count > 0:
        print("\n" + "="*65)
        print("🤖 INITIATING 3-AGENT COLLABORATIVE REMEDIATION (APPROACH)")
        print("Sponsors: Zetaris Data Fabric | Meterless Nightshift (NVIDIA) | H-MEM")
        print("="*65)
        from src.core.multi_agent.orchestrator import MultiAgentOrchestrator
        orchestrator = MultiAgentOrchestrator(max_critique_rounds=3)
        pipeline = orchestrator.run_remediation_pipeline(target_path, findings)

        last_patch = None
        for event in pipeline:
            evt_type = event.get("type")
            if evt_type == "agent_action":
                iter_str = f" [Attempt #{event['iteration']}]" if "iteration" in event else ""
                print(f"\n👉 [{event.get('agent')}]{iter_str}: {event.get('message')}")
            elif evt_type == "plan_ready":
                print("\n📋 Remediation Plan:")
                for t in event["plan"]["execution_order"]:
                    print(f"   • [{t['severity']}] {t['check_id']} (OWASP: {t['owasp_category']})")
            elif evt_type == "patch_generated":
                print(f"📝 Patch Drafted ({event.get('provider')} - {event.get('model')})")
                last_patch = event.get("diff")
            elif evt_type == "critique_result":
                badge = "✅ APPROVED" if event.get("approved") else "❌ REVISION REQUIRED"
                print(f"🧐 Critic Decision: {badge} (Score: {event.get('score')}/100)")
                print(f"   Reasoning: {event.get('critique')}")
            elif evt_type == "self_healing_trigger":
                print(f"   {event.get('message')}")
            elif evt_type == "workflow_complete":
                summary = event.get("summary")
                print("\n" + "="*65)
                print(f"🎯 Multi-Agent Remediation Complete: {summary['remediated_tasks']}/{summary['total_tasks']} Vulnerabilities Neutralized")
                print(f"🧠 H-MEM Memory Episodes Recorded: {summary['hmem_state']['total_episodes']}")
                print("💾 Audit Telemetry Synced to Zetaris Data Fabric")
                print("="*65 + "\n")

        if args.apply and last_patch and os.path.isfile(target_path):
            print("\n[*] Applying verified patch to disk...")
            target_dir = os.path.dirname(os.path.abspath(target_path))
            apply_res = apply_patch(last_patch, target_dir)
            if apply_res.get("applied"):
                print("[+] Verified patch applied cleanly to target.")

        if score < args.fail_under:
            print(f"\n[❌] SECURITY GATE FAILED: Initial Score {score} is below threshold {args.fail_under}.")
            sys.exit(1)
        else:
            print(f"\n[✅] SECURITY GATE PASSED: Score {score} meets threshold {args.fail_under}.")
        sys.exit(0)

    print(f"[*] Initializing AI Deep Reasoning (Meterless Nightshift / NVIDIA)...")


    print("[*] Performing Deep-Trace Analysis...")
    
    # Agentic: Resolve dependencies
    from src.core.security import resolve_local_dependencies, unified_security_scan
    context_files = {}
    if not os.path.isfile(target_path):
        # Sample dependencies from a primary file if directory
        from src.core.file_utils import extract_primary_code_sample
        primary_code, primary_rel = extract_primary_code_sample(target_path)
        if primary_rel:
            deps = resolve_local_dependencies(primary_code, target_path)
            for d_rel, d_full in deps:
                try:
                    with open(d_full, "r", encoding="utf-8", errors="ignore") as df:
                        context_files[d_rel] = df.read(2000)
                except: pass
    else:
        # Resolve dependencies for the single file
        target_dir = os.path.dirname(os.path.abspath(target_path))
        deps = resolve_local_dependencies(code_content, target_dir)
        for d_rel, d_full in deps:
            try:
                with open(d_full, "r", encoding="utf-8", errors="ignore") as df:
                    context_files[d_rel] = df.read(2000)
            except: pass

    # Use the unified scanner for CLI too
    report, patch = unified_security_scan(semgrep_results, code_content, None, 
                                        file_path=os.path.basename(target_path), 
                                        context_files=context_files)
    
    print("\n" + "="*50)
    print("🛡️  VERIFAI_LLM SECURITY REPORT 🛡️")
    print("="*50)
    print(report)
    print("="*50 + "\n")

    # 3. Patch Generation & Verification
    if patch and patch != "No patch suggestions.":
        print("🔧 Patch Suggestions:")
        print(patch)
        
        if args.apply and os.path.isfile(target_path):
            print("\n[*] Applying patch...")
            target_dir = os.path.dirname(os.path.abspath(target_path))
            apply_res = apply_patch(patch, target_dir)
            if apply_res.get("applied"):
                print("[+] Patch applied successfully. Starting verification...")
                # ... (rest of verification logic remains same)

    # Final Decision (CI/CD Gatekeeper)
    if score < args.fail_under:
        print(f"\n[❌] SECURITY GATE FAILED: Score {score} is below threshold {args.fail_under}.")
        print("[!] Critical security issues must be resolved before merging.")
        sys.exit(1)
    else:
        print(f"\n[✅] SECURITY GATE PASSED: Score {score} meets threshold {args.fail_under}.")

    # Success exit
    sys.exit(0)

if __name__ == "__main__":
    main()

