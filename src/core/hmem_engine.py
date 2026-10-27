"""
Meterless H-MEM Engine (Hierarchical Memory)
===========================================
Implements the Meterless H-MEM engine architecture for multi-agent systems.
Provides:
1. Tier-1: Working Context Memory (short-term scratchpad & active AST findings)
2. Tier-2: Episodic Critique Memory (patch revision history, compiler errors, critic feedback)
3. Tier-3: Semantic Security Knowledge (learned OWASP fixes & architectural invariants)

Enables dynamic self-healing loops where agents remember past critiques and adapt.
"""

import time
import json
import logging
from typing import Dict, List, Any, Optional

logger = logging.getLogger(__name__)

class HMemEngine:
    """Meterless Hierarchical Memory Engine for autonomous multi-agent reasoning."""

    def __init__(self, session_id: Optional[str] = None):
        self.session_id = session_id or f"hmem_{int(time.time())}"
        # Tier 1: Working Memory
        self.working_memory: Dict[str, Any] = {
            "current_target": None,
            "raw_findings": [],
            "active_plan": [],
            "iteration_count": 0
        }
        # Tier 2: Episodic Memory (revisions & critiques)
        self.episodic_memory: List[Dict[str, Any]] = []
        # Tier 3: Semantic Security Invariants
        self.semantic_memory: Dict[str, Any] = {
            "python.sqlite3.sql-injection": {
                "rule": "Always use DB-API parameterized queries with ? or named placeholders; never use f-strings or % formatting.",
                "verified_template": "cursor.execute('SELECT * FROM tbl WHERE id = ?', (target_id,))"
            },
            "python.flask.security.audit.hardcoded-config": {
                "rule": "Load sensitive configurations and DEBUG flags strictly from environment variables.",
                "verified_template": "app.config['DEBUG'] = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'"
            },
            "python.lang.security.insecure-hash-function": {
                "rule": "Replace weak hashes (MD5, SHA1) with SHA256 or SHA512 for integrity, and argon2/bcrypt for passwords.",
                "verified_template": "hashlib.sha256(data).hexdigest()"
            }
        }

    # ---------------- Tier 1: Working Memory ----------------
    def set_working_target(self, target_path: str, findings: List[Dict[str, Any]]):
        """Set active file and AST scanner findings in Tier-1 Working Memory."""
        self.working_memory["current_target"] = target_path
        self.working_memory["raw_findings"] = findings
        self.working_memory["iteration_count"] = 0
        logger.debug(f"[H-MEM] Initialized Working Memory for {target_path} with {len(findings)} findings.")

    def set_active_plan(self, plan: List[Dict[str, Any]]):
        """Store Planner Agent's execution strategy."""
        self.working_memory["active_plan"] = plan

    def get_working_state(self) -> Dict[str, Any]:
        """Retrieve current short-term state."""
        return self.working_memory

    # ---------------- Tier 2: Episodic Memory ----------------
    def record_iteration(
        self,
        iteration: int,
        agent_name: str,
        patch_diff: str,
        critic_approved: bool,
        critic_feedback: str,
        residual_vulnerabilities: int
    ):
        """Record an episode in the critique loop for multi-turn learning."""
        episode = {
            "timestamp": time.time(),
            "iteration": iteration,
            "agent": agent_name,
            "patch_diff": patch_diff,
            "critic_approved": critic_approved,
            "critic_feedback": critic_feedback,
            "residual_vulnerabilities": residual_vulnerabilities
        }
        self.episodic_memory.append(episode)
        self.working_memory["iteration_count"] = iteration
        logger.info(f"[H-MEM] Stored Episode #{iteration} ({'APPROVED' if critic_approved else 'REVISION_NEEDED'}).")

    def get_critique_history(self) -> List[Dict[str, Any]]:
        """Return the sequence of agent critiques for feedback-driven self-healing."""
        return self.episodic_memory

    def format_critique_context_for_specialist(self) -> str:
        """Format prior rejected attempts into a guidance prompt for the Specialist Agent."""
        if not self.episodic_memory:
            return "No previous critique episodes. This is the first patch generation attempt."

        context_lines = ["### [H-MEM] Memory of Prior Attempts & Critic Rejections:"]
        for ep in self.episodic_memory:
            status = "PASSED" if ep["critic_approved"] else "REJECTED"
            context_lines.append(
                f"- Attempt {ep['iteration']} [{status}]: Critic Feedback: {ep['critic_feedback']}. "
                f"Residual Issues: {ep['residual_vulnerabilities']}"
            )
        context_lines.append(
            "CRITICAL INSTRUCTION: You MUST address all critic concerns noted above and NOT repeat the prior mistakes."
        )
        return "\n".join(context_lines)

    # ---------------- Tier 3: Semantic Knowledge ----------------
    def query_semantic_invariant(self, check_id: str) -> Optional[Dict[str, str]]:
        """Query long-term semantic knowledge base for verified security patterns."""
        for pattern_key, info in self.semantic_memory.items():
            if pattern_key in check_id or check_id in pattern_key:
                return info
        return None

    def record_successful_remediation(self, check_id: str, rule: str, template: str):
        """Persist newly verified security patch pattern into Tier-3 Semantic Memory."""
        self.semantic_memory[check_id] = {
            "rule": rule,
            "verified_template": template
        }
        logger.info(f"[H-MEM] Promoted verified fix for {check_id} into Tier-3 Semantic Memory.")

    def export_summary(self) -> Dict[str, Any]:
        """Export state summary for UI telemetry and audit logging."""
        return {
            "session_id": self.session_id,
            "working_target": self.working_memory.get("current_target"),
            "total_episodes": len(self.episodic_memory),
            "episodes": self.episodic_memory,
            "semantic_patterns_count": len(self.semantic_memory)
        }

# Global singleton instance
_hmem_instance = None

def get_hmem_engine(session_id: Optional[str] = None) -> HMemEngine:
    global _hmem_instance
    if _hmem_instance is None or session_id:
        _hmem_instance = HMemEngine(session_id=session_id)
    return _hmem_instance
