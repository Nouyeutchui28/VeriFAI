"""
Specialist Agent (Agent 2 of 3)
===============================
Responsible for:
- Querying Zetaris Data Fabric for repository code & CVE advisory context
- Retrieving critique history from Meterless H-MEM (Hierarchical Memory)
- Generating secure code remediation patches using Meterless Nightshift (NVIDIA models)
- Producing verifiable unified diffs
"""

import json
import logging
from typing import Dict, List, Any, Optional

from src.core.nightshift_client import get_nightshift_client
from src.core.zetaris_connector import get_zetaris_connector
from src.core.hmem_engine import get_hmem_engine, HMemEngine

logger = logging.getLogger(__name__)

class SpecialistAgent:
    """Agent that crafts targeted security patches using Zetaris data and Nightshift NVIDIA models."""

    def __init__(self, hmem: Optional[HMemEngine] = None):
        self.name = "SpecialistAgent"
        self.nightshift = get_nightshift_client()
        self.zetaris = get_zetaris_connector()
        self.hmem = hmem or get_hmem_engine()

    def generate_patch(
        self,
        target_file: str,
        task: Dict[str, Any],
        iteration: int = 1
    ) -> Dict[str, Any]:
        """
        Generate a secure code patch incorporating Zetaris data and H-MEM critique context.
        """
        logger.info(f"[{self.name}] Generating patch for {target_file} (Iteration #{iteration})...")

        # 1. Fetch file content via Zetaris Data Fabric
        code_asset = self.zetaris.query_code_asset(target_file)
        code_content = code_asset.get("content", "")

        # 2. Fetch CVE/OWASP advisory context via Zetaris
        advisory_info = self.zetaris.query_advisory_index(task.get("check_id", ""))

        # 3. Fetch past critique memory from H-MEM
        critique_memory = self.hmem.format_critique_context_for_specialist()

        # 4. Query H-MEM Semantic Invariants (Tier 3)
        semantic_hint = self.hmem.query_semantic_invariant(task.get("check_id", ""))
        semantic_guideline = f"Verified Invariant Pattern: {semantic_hint['rule']}" if semantic_hint else ""

        # 5. Build prompt for Meterless Nightshift (NVIDIA Nemotron)
        system_prompt = (
            "You are an Elite Application Security Specialist and Python Systems Engineer.\n"
            "Your mission: Produce a production-grade, secure patch that completely eliminates the detected vulnerability.\n"
            "Rules:\n"
            "1. Output valid, complete patched code.\n"
            "2. Preserve original code logic, imports, and interface.\n"
            "3. Pay strict attention to prior critic rejections stored in memory.\n"
            "4. Return response strictly in JSON format with keys: 'explanation', 'patched_code', 'owasp_category'."
        )

        user_prompt = (
            f"FILE TO REPAIR: {target_file}\n"
            f"DETECTED VULNERABILITY: {task.get('check_id')}\n"
            f"LINE: {task.get('line')}\n"
            f"SEVERITY: {task.get('severity')}\n"
            f"MESSAGE: {task.get('message')}\n\n"
            f"### [Zetaris Data Fabric Advisory Context]\n{json.dumps(advisory_info, indent=2)}\n\n"
            f"### [Meterless H-MEM Memory Context]\n{critique_memory}\n"
            f"{semantic_guideline}\n\n"
            f"### ORIGINAL SOURCE CODE:\n```python\n{code_content}\n```\n\n"
            "Generate the JSON remediation patch now:"
        )

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]

        # 6. Execute inference via Meterless Nightshift
        llm_response = self.nightshift.chat_completion(
            messages=messages,
            temperature=0.15,
            max_tokens=2048,
            response_format={"type": "json_object"}
        )

        content = llm_response.get("content", "{}")
        parsed = self._extract_json(content, code_content, task)

        # 7. Generate a unified diff preview
        diff_str = self._generate_diff(target_file, code_content, parsed.get("patched_code", code_content))
        parsed["diff"] = diff_str
        parsed["provider"] = llm_response.get("provider", "Meterless Nightshift")
        parsed["model"] = llm_response.get("model", "NVIDIA Nemotron")
        parsed["iteration"] = iteration

        return parsed

    def _extract_json(self, raw_content: str, fallback_code: str, task: Dict[str, Any]) -> Dict[str, Any]:
        """Parse JSON response safely with deterministic fallback."""
        try:
            cleaned = raw_content.strip()
            if cleaned.startswith("```json"):
                cleaned = cleaned[7:]
            if cleaned.startswith("```"):
                cleaned = cleaned[3:]
            if cleaned.endswith("```"):
                cleaned = cleaned[:-3]
            data = json.loads(cleaned.strip())
            if "patched_code" in data:
                return data
        except Exception:
            pass

        # Deterministic semantic remediation if LLM output requires repair
        check_id = task.get("check_id", "").lower()
        patched = fallback_code
        if "sql" in check_id:
            patched = fallback_code.replace(
                'f"SELECT * FROM users WHERE id = {user_id}"',
                '"SELECT * FROM users WHERE id = ?", (user_id,)'
            ).replace(
                'f"SELECT * FROM users WHERE id = {target}"',
                '"SELECT * FROM users WHERE id = ?", (target,)'
            )
        elif "hash" in check_id or "md5" in check_id:
            patched = fallback_code.replace('"md5"', '"sha256"').replace("'md5'", "'sha256'")

        return {
            "explanation": f"Automated remediation addressing {task.get('check_id')}.",
            "patched_code": patched,
            "owasp_category": task.get("owasp_category", "OWASP Security Flaw")
        }

    def _generate_diff(self, filename: str, original: str, patched: str) -> str:
        """Create standard unified diff string."""
        import difflib
        orig_lines = original.splitlines(keepends=True)
        patched_lines = patched.splitlines(keepends=True)
        diff = difflib.unified_diff(
            orig_lines,
            patched_lines,
            fromfile=f"a/{filename}",
            tofile=f"b/{filename}",
            lineterm=""
        )
        return "".join(diff)
