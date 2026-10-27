"""
Multi-Agent Orchestrator
========================
Coordinates the 3-agent cooperative loop:
  PlannerAgent ──▶ SpecialistAgent ──▶ EvaluatorAgent (Critic)
                         ▲                       │
                         └──── [Feedback Loop] ──┘

Features:
- Meterless H-MEM hierarchical memory persistence across iterations
- Zetaris Data Fabric virtualized queries
- Meterless Nightshift NVIDIA inference
- Yields live streaming events for UI & CLI display
"""

import logging
from typing import Dict, List, Any, Generator

from src.core.hmem_engine import get_hmem_engine, HMemEngine
from src.core.zetaris_connector import get_zetaris_connector, ZetarisConnector
from src.core.multi_agent.planner_agent import PlannerAgent
from src.core.multi_agent.specialist_agent import SpecialistAgent
from src.core.multi_agent.evaluator_agent import EvaluatorAgent

logger = logging.getLogger(__name__)

class MultiAgentOrchestrator:
    """Orchestrates dynamic multi-agent security triage, patching, and critique."""

    def __init__(self, session_id: str = None, max_critique_rounds: int = 3):
        self.session_id = session_id
        self.max_critique_rounds = max_critique_rounds
        self.hmem: HMemEngine = get_hmem_engine(session_id)
        self.zetaris: ZetarisConnector = get_zetaris_connector()

        self.planner = PlannerAgent(self.hmem)
        self.specialist = SpecialistAgent(self.hmem)
        self.evaluator = EvaluatorAgent(self.hmem)

    def run_remediation_pipeline(
        self,
        target_file: str,
        findings: List[Dict[str, Any]]
    ) -> Generator[Dict[str, Any], None, Dict[str, Any]]:
        """
        Execute the full multi-agent remediation loop, yielding progress events.
        """
        yield {
            "type": "status",
            "message": f"🚀 Initializing VeriFAI Agentic Remediation on `{target_file}`"
        }

        # 1. Planner Agent: Triage and scoping
        yield {
            "type": "agent_action",
            "agent": self.planner.name,
            "stage": "planning",
            "message": f"Analyzing {len(findings)} findings via AST and OWASP classification..."
        }
        plan = self.planner.analyze_and_plan(target_file, findings)
        yield {
            "type": "plan_ready",
            "agent": self.planner.name,
            "plan": plan
        }

        remediation_results = []

        # 2. Iterate through planned tasks
        for task in plan.get("execution_order", []):
            task_id = task.get("task_id")
            check_id = task.get("check_id")
            yield {
                "type": "task_start",
                "task": task,
                "message": f"Starting remediation for `{check_id}` (Severity: {task.get('severity')})"
            }

            patch_approved = False
            current_patch = None
            evaluation = None

            # 3. Dynamic Critique & Self-Healing Loop
            for iteration in range(1, self.max_critique_rounds + 1):
                yield {
                    "type": "agent_action",
                    "agent": self.specialist.name,
                    "stage": "patching",
                    "iteration": iteration,
                    "message": f"Querying Zetaris Data Fabric & H-MEM memory to craft patch (Attempt {iteration}/{self.max_critique_rounds})..."
                }

                current_patch = self.specialist.generate_patch(
                    target_file=target_file,
                    task=task,
                    iteration=iteration
                )

                yield {
                    "type": "patch_generated",
                    "agent": self.specialist.name,
                    "iteration": iteration,
                    "diff": current_patch.get("diff"),
                    "provider": current_patch.get("provider"),
                    "model": current_patch.get("model")
                }

                # Evaluator Agent critiques the candidate patch
                yield {
                    "type": "agent_action",
                    "agent": self.evaluator.name,
                    "stage": "evaluating",
                    "iteration": iteration,
                    "message": f"Performing AST syntax inspection and security regression check..."
                }

                evaluation = self.evaluator.evaluate_patch(
                    target_file=target_file,
                    task=task,
                    patch_result=current_patch,
                    iteration=iteration
                )

                yield {
                    "type": "critique_result",
                    "agent": self.evaluator.name,
                    "iteration": iteration,
                    "approved": evaluation.get("approved"),
                    "score": evaluation.get("score"),
                    "critique": evaluation.get("critique")
                }

                if evaluation.get("approved"):
                    patch_approved = True
                    break
                else:
                    yield {
                        "type": "self_healing_trigger",
                        "message": f"🔄 Dynamic Self-Healing: Evaluator rejected patch. Pushing critique to H-MEM and triggering revision."
                    }

            remediation_results.append({
                "task": task,
                "approved": patch_approved,
                "final_patch": current_patch,
                "final_evaluation": evaluation,
                "iterations_required": iteration
            })

        final_summary = {
            "target_file": target_file,
            "total_tasks": len(plan.get("execution_order", [])),
            "remediated_tasks": sum(1 for r in remediation_results if r["approved"]),
            "results": remediation_results,
            "hmem_state": self.hmem.export_summary()
        }

        yield {
            "type": "workflow_complete",
            "summary": final_summary
        }

        return final_summary
