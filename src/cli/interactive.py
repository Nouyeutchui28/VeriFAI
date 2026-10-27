"""
Interactive Terminal Interface for VeriFAI LLM
================================================
Provides a rich terminal-driven user experience for:
1. Scanning local Python files or projects
2. Scanning pasted code snippets directly from the terminal
3. Watching the 3-Agent Collaborative Loop in action (Planner -> Specialist -> Critic)
4. Reviewing diffs side-by-side and interactively applying patches to disk
5. Inspecting Meterless H-MEM hierarchical memory and Zetaris Data Fabric telemetry
6. Configuring AI providers (Nightshift NVIDIA / Ollama / Cloud)
"""

import os
import sys
import json
import tempfile
from typing import List, Dict, Any, Optional

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.prompt import Prompt, Confirm
from rich.syntax import Syntax
from rich.markdown import Markdown
from rich.text import Text

console = Console()

def render_banner():
    banner_text = Text()
    banner_text.append("🛡️  VeriFAI Agentic PatchOps\n", style="bold cyan")
    banner_text.append("Autonomous 3-Agent Collaborative Security Remediation\n", style="bold green")
    banner_text.append("Sponsors: Zetaris Data Fabric | Meterless Nightshift (NVIDIA) | Meterless H-MEM Engine", style="dim white")
    
    console.print(Panel(
        banner_text,
        border_style="cyan",
        padding=(1, 2)
    ))

def print_engine_status():
    from src.core.nightshift_client import get_nightshift_client
    from src.core.hmem_engine import get_hmem_engine
    from src.core.zetaris_connector import get_zetaris_connector

    nightshift = get_nightshift_client()
    hmem = get_hmem_engine()
    zetaris = get_zetaris_connector()

    status_table = Table(show_header=True, header_style="bold magenta", expand=True)
    status_table.add_column("Sponsor Technology", style="cyan")
    status_table.add_column("Active Configuration", style="white")
    status_table.add_column("Operational Status", style="green")

    provider_mode = "Live Cloud API" if nightshift.is_live else "Simulated Resilient"
    status_table.add_row("Meterless Nightshift", f"Model: {nightshift.default_model}", f"● {provider_mode}")

    hmem_episodes = len(hmem.episodic_memory)
    status_table.add_row("Meterless H-MEM", f"Hierarchical 3-Tier ({hmem_episodes} Episodes Stored)", "● Memory Active")

    zetaris_mode = f"Workspace: {zetaris.workspace_id}"
    status_table.add_row("Zetaris Data Fabric", zetaris_mode, "● Virtual Lake Ready")

    console.print(status_table)
    console.print()

def run_semgrep_cli(target_path: str) -> Dict[str, Any]:
    """Execute Semgrep scan on target path using core engine."""
    from src.core.security import run_semgrep_scan
    with console.status("[bold green]Running Semgrep AST Static Analysis...[/bold green]"):
        try:
            return run_semgrep_scan(target_path, metrics_enabled=False)
        except Exception as e:
            console.print(f"[bold red]Semgrep execution error: {e}[/bold red]")
            return {"results": []}

def calculate_score(findings: List[Dict[str, Any]]) -> tuple:
    score = 100
    sev_counts = {"high": 0, "medium": 0, "low": 0}
    for f in findings:
        sev = (f.get("extra", {}).get("severity") or "low").upper()
        if sev in ["ERROR", "HIGH"]:
            score -= 15
            sev_counts["high"] += 1
        elif sev in ["WARNING", "MEDIUM"]:
            score -= 5
            sev_counts["medium"] += 1
        else:
            score -= 1
            sev_counts["low"] += 1
    return max(0, score), sev_counts

def display_findings_table(findings: List[Dict[str, Any]]):
    table = Table(title="🔍 Detected Vulnerabilities", header_style="bold yellow", expand=True)
    table.add_column("#", style="dim", width=4)
    table.add_column("Severity", width=10)
    table.add_column("Rule / Check ID", style="bold white")
    table.add_column("Location", style="cyan")
    table.add_column("Description", style="dim")

    for idx, f in enumerate(findings, start=1):
        sev = (f.get("extra", {}).get("severity") or "low").upper()
        sev_style = "bold red" if sev in ["ERROR", "HIGH"] else "bold yellow" if sev in ["WARNING", "MEDIUM"] else "bold blue"
        check_id = f.get("check_id", "General")
        path = f.get("path", "")
        line = f.get("start", {}).get("line", "?")
        desc = f.get("extra", {}).get("message", "").strip().split("\n")[0][:80]
        
        table.add_row(str(idx), f"[{sev_style}]{sev}[/{sev_style}]", check_id, f"{path}:{line}", desc)

    console.print(table)
    console.print()

def execute_agentic_loop(target_path: str, findings: List[Dict[str, Any]]) -> Optional[str]:
    """Execute the full 3-agent cooperative loop with live terminal telemetry."""
    from src.core.multi_agent.orchestrator import MultiAgentOrchestrator
    from src.core.file_utils import apply_patch

    console.print(Panel("[bold cyan]🤖 Initiating 3-Agent Collaborative Remediation[/bold cyan]\n"
                        "[dim]PlannerAgent (Triage) ──▶ SpecialistAgent (Nightshift NVIDIA) ──▶ EvaluatorAgent (Critic)[/dim]",
                        border_style="cyan"))

    orchestrator = MultiAgentOrchestrator(max_critique_rounds=3)
    pipeline = orchestrator.run_remediation_pipeline(target_path, findings)

    last_patch = None
    for event in pipeline:
        evt_type = event.get("type")
        if evt_type == "agent_action":
            agent = event.get("agent")
            iter_info = f" [Attempt #{event['iteration']}]" if "iteration" in event else ""
            console.print(f"[bold magenta]👉 [{agent}]{iter_info}[/bold magenta]: {event.get('message')}")
        
        elif evt_type == "plan_ready":
            plan = event.get("plan", {})
            plan_table = Table(title="📋 Planner Execution Order", show_header=True, header_style="bold green")
            plan_table.add_column("Priority", width=10)
            plan_table.add_column("Vulnerability ID")
            plan_table.add_column("OWASP Classification")
            for t in plan.get("execution_order", []):
                plan_table.add_row(t.get("severity"), t.get("check_id"), t.get("owasp_category"))
            console.print(plan_table)
            console.print()

        elif evt_type == "patch_generated":
            last_patch = event.get("diff")
            console.print(f"[bold green]📝 Candidate Patch Synthesized[/bold green] via [cyan]{event.get('provider')}[/cyan] ({event.get('model')})")
            if last_patch:
                console.print(Syntax(last_patch, "diff", theme="monokai", line_numbers=True))

        elif evt_type == "critique_result":
            approved = event.get("approved")
            score = event.get("score")
            critique = event.get("critique")
            badge = "[bold green]✅ APPROVED[/bold green]" if approved else "[bold red]❌ REVISION REQUIRED[/bold red]"
            console.print(Panel(
                f"{badge} (Score: {score}/100)\n\n[bold white]Critic Reasoning:[/bold white] {critique}",
                title="🧐 Evaluator Agent Critique",
                border_style="green" if approved else "red"
            ))

        elif evt_type == "self_healing_trigger":
            console.print(f"[bold yellow]🔄 Dynamic Self-Healing Triggered:[/bold yellow] {event.get('message')}\n")

        elif evt_type == "workflow_complete":
            summary = event.get("summary", {})
            console.print(Panel(
                f"[bold green]🎯 Remediation Loop Complete![/bold green]\n"
                f"Neutralized: {summary.get('remediated_tasks')}/{summary.get('total_tasks')} vulnerabilities\n"
                f"H-MEM Stored Episodes: {summary.get('hmem_state', {}).get('total_episodes')}\n"
                f"Audit Telemetry synced to Zetaris Data Fabric",
                border_style="green"
            ))

    return last_patch

def handle_scan_target(target_path: str):
    """Scan and process a validated target file or directory."""
    if not os.path.exists(target_path):
        console.print(f"[bold red]❌ Path not found: {target_path}[/bold red]")
        return

    semgrep_results = run_semgrep_cli(target_path)
    findings = semgrep_results.get("results", [])
    score, sev_counts = calculate_score(findings)

    score_color = "green" if score >= 80 else "yellow" if score >= 50 else "red"
    console.print(Panel(
        f"[bold {score_color}]Security Health Score: {score}/100[/bold {score_color}]\n"
        f"Distribution: [bold red]{sev_counts['high']} High[/bold red] | "
        f"[bold yellow]{sev_counts['medium']} Medium[/bold yellow] | "
        f"[bold blue]{sev_counts['low']} Low[/bold blue] (Total: {len(findings)} findings)",
        border_style=score_color,
        title=f"📊 Scan Results for {os.path.basename(target_path)}"
    ))

    if not findings:
        console.print("[bold green]🎉 Clean code! No security vulnerabilities detected.[/bold green]\n")
        return

    display_findings_table(findings)

    # Post-scan Action Submenu
    while True:
        console.print("\n[bold cyan]Select an action for this scan:[/bold cyan]")
        console.print("  [1] 🤖 Run 3-Agent Collaborative Remediation (Zetaris + Nightshift + H-MEM)")
        console.print("  [2] 📄 View Detailed Code Snippets for Findings")
        console.print("  [3] 📄 Export Security Audit Report (PDF)")
        console.print("  [4] ↩️  Return to Main Menu")
        
        sub_choice = Prompt.ask("Choose option", choices=["1", "2", "3", "4"], default="1")

        if sub_choice == "1":
            patch = execute_agentic_loop(target_path, findings)
            if patch and os.path.isfile(target_path):
                if Confirm.ask("\n💾 Apply verified security patch to disk?"):
                    from src.core.file_utils import apply_patch
                    target_dir = os.path.dirname(os.path.abspath(target_path))
                    res = apply_patch(patch, target_dir)
                    if res.get("applied"):
                        console.print("[bold green]✅ Patch applied cleanly to file on disk![/bold green]")
                    else:
                        console.print(f"[bold red]❌ Failed to apply patch: {res.get('error')}[/bold red]")

        elif sub_choice == "2":
            for idx, f in enumerate(findings, start=1):
                code = f.get("extra", {}).get("lines", "")
                rule = f.get("check_id")
                line = f.get("start", {}).get("line")
                console.print(f"\n[bold yellow]Finding #{idx}: {rule} (Line {line})[/bold yellow]")
                if code:
                    console.print(Syntax(code, "python", theme="monokai", line_numbers=True))
                else:
                    console.print("[dim]No code snippet available[/dim]")

        elif sub_choice == "3":
            try:
                from src.utils.report_gen import generate_pdf_report
                with open(target_path, 'r', encoding='utf-8', errors='ignore') as fp:
                    code_content = fp.read()
                pdf_bytes = generate_pdf_report(code_content, "CLI Security Analysis", semgrep_results)
                out_pdf = f"security_report_{os.path.basename(target_path)}.pdf"
                with open(out_pdf, "wb") as pf:
                    pf.write(pdf_bytes)
                console.print(f"[bold green]✅ PDF Audit report exported to: {out_pdf}[/bold green]")
            except Exception as e:
                console.print(f"[bold red]❌ PDF export failed: {e}[/bold red]")

        elif sub_choice == "4":
            break

def handle_paste_input():
    """Allows user to paste code snippet directly in terminal and scan it."""
    console.print("\n[bold cyan]📝 Paste Python Code Snippet[/bold cyan]")
    console.print("[dim]Paste your code below. Type 'EOF' on a new line and press Enter when finished:[/dim]\n")

    lines = []
    while True:
        try:
            line = input()
            if line.strip() == "EOF":
                break
            lines.append(line)
        except EOFError:
            break

    code_str = "\n".join(lines).strip()
    if not code_str:
        console.print("[bold yellow]⚠️ No code provided. Returning to menu.[/bold yellow]")
        return

    # Write to a temporary file
    temp_path = None
    try:
        temp_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "temp_code")
        os.makedirs(temp_dir, exist_ok=True)
        import uuid
        temp_path = os.path.join(temp_dir, f"snippet_{uuid.uuid4().hex[:8]}.py")
        with open(temp_path, "w", encoding="utf-8") as tf:
            tf.write(code_str)
    except OSError:
        try:
            with tempfile.NamedTemporaryFile(suffix=".py", mode="w", delete=False) as tf:
                tf.write(code_str)
                temp_path = tf.name
        except OSError as e:
            console.print(f"[bold red]❌ Cannot create temporary file (filesystem is read-only): {e}[/bold red]")
            return

    try:
        console.print(f"\n[dim]Saved temporary snippet to {temp_path}[/dim]")
        handle_scan_target(temp_path)
    finally:
        if os.path.exists(temp_path):
            try:
                os.remove(temp_path)
            except:
                pass

def handle_inspect_memory():
    """Inspects H-MEM memory tiers and Zetaris Data Fabric state."""
    from src.core.hmem_engine import get_hmem_engine
    from src.core.zetaris_connector import get_zetaris_connector

    hmem = get_hmem_engine()
    zetaris = get_zetaris_connector()

    console.print("\n[bold cyan]🧠 Meterless H-MEM Engine Inspection[/bold cyan]")
    console.print(f"Active Session ID: [bold white]{hmem.session_id}[/bold white]")
    console.print(f"Tier-1 Working Target: [yellow]{hmem.working_memory.get('current_target') or 'None'}[/yellow]")
    console.print(f"Tier-2 Episodic Rejections Stored: [bold green]{len(hmem.episodic_memory)}[/bold green]")

    if hmem.episodic_memory:
        for idx, ep in enumerate(hmem.episodic_memory, start=1):
            console.print(f"  • Episode #{idx}: Target={ep.get('task')}, Iteration={ep.get('iteration')}")
            console.print(f"    Critique: [italic]{ep.get('critic_feedback')}[/italic]")

    console.print("\nTier-3 Learned Semantic Invariants:")
    for k, v in hmem.semantic_memory.items():
        console.print(f"  • [bold green]{k}[/bold green]: {v.get('rule')}")

    console.print("\n[bold cyan]🌐 Zetaris Data Fabric Telemetry[/bold cyan]")
    console.print(f"Endpoint: [white]{zetaris.endpoint}[/white]")
    console.print(f"Workspace: [white]{zetaris.workspace_id}[/white]")
    console.print(f"Live Connection: [{'green' if zetaris.is_live else 'yellow'}]{zetaris.is_live}[/{'green' if zetaris.is_live else 'yellow'}]")
    console.print()

def start_interactive_cli():
    """Main interactive terminal loop."""
    render_banner()
    print_engine_status()

    while True:
        console.print("[bold cyan]═══════════════════════ MAIN MENU ═══════════════════════[/bold cyan]")
        console.print("  [1] 📁 Scan a Python File or Repository Directory")
        console.print("  [2] 📝 Scan Pasted Code Snippet")
        console.print("  [3] 🤖 Run 3-Agent Autonomous Demo on Sample Target")
        console.print("  [4] 🧠 Inspect H-MEM Memory & Zetaris Telemetry")
        console.print("  [5] ⚙️  View Engine Configuration & AI Status")
        console.print("  [6] 🚪 Exit")
        console.print("[bold cyan]═════════════════════════════════════════════════════════[/bold cyan]")

        choice = Prompt.ask("Select an option", choices=["1", "2", "3", "4", "5", "6"], default="1")

        if choice == "1":
            target = Prompt.ask("\nEnter path to file or directory to scan")
            if not target.strip():
                console.print("[yellow]Empty path. Aborting.[/yellow]")
            else:
                handle_scan_target(target.strip())

        elif choice == "2":
            handle_paste_input()

        elif choice == "3":
            console.print("\n[bold cyan]Select a sample target for the 3-Agent Collaborative Loop:[/bold cyan]")
            console.print("  [1] SQLite SQL Injection (OWASP A03:2021) - vuln_test.py")
            console.print("  [2] Flask Debug Misconfiguration (OWASP A05:2021) - sample_misconfig_test.py")
            demo_pick = Prompt.ask("Choose target", choices=["1", "2"], default="1")
            demo_file = "vuln_test.py" if demo_pick == "1" else "sample_misconfig_test.py"
            handle_scan_target(demo_file)

        elif choice == "4":
            handle_inspect_memory()

        elif choice == "5":
            print_engine_status()

        elif choice == "6":
            console.print("[bold cyan]👋 Thank you for using VeriFAI LLM. Stay secure![/bold cyan]")
            sys.exit(0)
