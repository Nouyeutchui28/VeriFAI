# VeriFAI LLM — Project Report

**Generated:** May 15, 2026

## Executive Summary
- Project: VeriFAI LLM — hybrid security analysis platform combining Semgrep-based static analysis with an aligned large language model (LLM).
- Purpose: Provide accurate vulnerability detection, exploit reasoning, and automated remediation with an interactive Streamlit interface.
- Status: v1.0.0-PRO (documentation and training guidance included in repository).

## Project Details
- Lead Architect: NOUYEUTCHUI YOUMBI JUNIOR BRONDON
- Main repo files: [README.md](README.md), [MODEL_SPEC.md](MODEL_SPEC.md), [PROJECT_REPORT_DETAILS.md](PROJECT_REPORT_DETAILS.md), [TRAINING_GUIDE.md](TRAINING_GUIDE.md)

## Architecture & Components
- Static Gate: Semgrep for pattern-based scanning and primary filtering of suspect code.
- Intelligence Layer: An aligned LLM (LLaMA-family or licensed base) specialized via instruction tuning and reinforcement alignment to perform exploit reasoning and remediation generation.
- Interface: Streamlit application for uploads, interactive analysis, and reports (`app.py`).
- Persistence: InsForge-backed PostgreSQL (scan history, users, results).
- Remediation Engine: Automated unified-diff patch generator producing ready-to-apply fixes.

### Analysis Flow
1. Code input (direct paste / multi-file upload / repository snapshot)
2. Semgrep pattern scan to identify suspect code
3. LLM confirmation and exploitability reasoning
4. Patch generation (unified-diff)
5. Persist results and present interactive findings in the UI

## AI Training & Alignment (summary)
- Approach: Instruction Alignment Tuning and supervised fine-tuning (SFT) on curated security data; optional reward-model + PPO tuning for instruction following.
- Key design choices: Chain-of-Thought style reasoning, low temperature for determinism, newline-aware chunking for long-context code analysis.
- Verification: Dual-gate verification — Semgrep must flag a pattern and the LLM must confirm exploitability before a high-confidence report is issued.

See the full, actionable training and alignment instructions in [TRAINING_GUIDE.md](TRAINING_GUIDE.md).

## Training Guide — Highlights
- Data: curated vulnerability writeups (CVE, exploit-db), vulnerable/fixed code pairs, Semgrep rule annotations, and Chain-of-Thought traces.
- Preprocessing: preserve code formatting, add file boundary tokens, use newline-aware chunking (e.g., 2k token window, 200 token stride).
- Objectives & Equations: cross-entropy (MLE), optional knowledge distillation, and reinforcement tuning via PPO with a learned reward model. Key equations are provided in [TRAINING_GUIDE.md](TRAINING_GUIDE.md).
- Practical commands: examples for SFT with Hugging Face Transformers, DeepSpeed/Accelerate, reward model training, and PPO-based alignment.

## Evaluation & Metrics
- Precision/Recall on labeled vulnerability corpora (per-vuln-type).
- False positive rate via manual review sampling.
- Patch correctness validated by running existing unit tests after applying patches.
- Production readiness score reported in project docs: 85/100 (OWASP-compliance metric, see [PROJECT_REPORT_DETAILS.md](PROJECT_REPORT_DETAILS.md)).

## Deployment & Usage
- Local run: install dependencies and run Streamlit:

```bash
pip install -r requirements.txt
streamlit run app.py
```

- Docker: build and run using instructions in [README.md](README.md).
- Configurable parameters: model selection, temperature, and Semgrep rule set (see `configs/` and `README.md`).

## Limitations & Assumptions
- The repository contains alignment and instruction-tuning recipes; it does not claim that the repository-trained LLM replaces or reproduces any proprietary third-party models.
- Results depend on base-model capabilities and Semgrep rule coverage; manual review is advisable for high-severity fixes.

## Recommendations
- Add a human-in-the-loop review step for high-severity patch application.
- Run precision/recall benchmarks continuously against labeled corpora and log results to improve rules and reward model.
- Expand Semgrep rule coverage using historical findings persisted in the backend.
- Integrate scan runs into CI gating to prevent regressions.

## Appendix & Sources
- Project docs: [README.md](README.md), [MODEL_SPEC.md](MODEL_SPEC.md), [PROJECT_REPORT_DETAILS.md](PROJECT_REPORT_DETAILS.md)
- Training & alignment instructions: [TRAINING_GUIDE.md](TRAINING_GUIDE.md)
- Tests & coverage: `tests/` and `htmlcov/` folders in the repository

---

End of report.
