"""
Planner Agent (Agent 1 of 3)
============================
Responsible for:
- Ingesting raw static scan findings (Semgrep AST results)
- Triage and prioritization based on OWASP Top 10 / CWE risk
- Formulating the strategic remediation plan
- Initializing Tier-1 Working Memory in Meterless H-MEM
"""

import logging
from typing import Dict, List, Any
from src.core.hmem_engine import HMemEngine, get_hmem_engine

logger = logging.getLogger(__name__)

class PlannerAgent:
    """Agent that plans and scopes the security remediation workflow."""

    def __init__(self, hmem: HMemEngine = None):
        self.name = "PlannerAgent"
        self.hmem = hmem or get_hmem_engine()

    def analyze_and_plan(self, target_file: str, findings: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Analyze scanner findings and produce an execution plan for the Specialist Agent.
        """
        logger.info(f"[{self.name}] Analyzing {len(findings)} findings for {target_file}")
        
        # Priority mapping for common OWASP / CWE categories
        severity_order = {"ERROR": 1, "WARNING": 2, "INFO": 3}
        
        prioritized_tasks = []
        for idx, finding in enumerate(findings):
            check_id = finding.get("check_id", "unknown-rule")
            extra = finding.get("extra", {})
            severity = extra.get("severity", "WARNING").upper()
            message = extra.get("message", "Potential vulnerability detected.")
            line = finding.get("start", {}).get("line", 1)

            # Determine OWASP classification
            owasp_cat = "A03:2021-Injection" if "sql" in check_id.lower() or "injection" in check_id.lower() \
                else "A02:2021-Cryptographic Failures" if "hash" in check_id.lower() or "crypto" in check_id.lower() \
                else "A05:2021-Security Misconfiguration" if "config" in check_id.lower() or "debug" in check_id.lower() \
                else "A01:2021-Broken Access Control"

            task = {
                "task_id": f"task_{idx + 1}",
                "check_id": check_id,
                "severity": severity,
                "owasp_category": owasp_cat,
                "message": message,
                "line": line,
                "priority_rank": severity_order.get(severity, 2)
            }
            prioritized_tasks.append(task)

        # Sort tasks by severity priority
        prioritized_tasks.sort(key=lambda t: t["priority_rank"])

        plan = {
            "target_file": target_file,
            "total_vulnerabilities": len(findings),
            "highest_severity": prioritized_tasks[0]["severity"] if prioritized_tasks else "NONE",
            "execution_order": prioritized_tasks,
            "strategy": "Remediate high-severity injection and cryptographic flaws before configuration warnings."
        }

        # Initialize H-MEM Tier-1 Working Memory
        self.hmem.set_working_target(target_file, findings)
        self.hmem.set_active_plan(prioritized_tasks)

        logger.info(f"[{self.name}] Plan created with {len(prioritized_tasks)} remediation steps.")
        return plan
