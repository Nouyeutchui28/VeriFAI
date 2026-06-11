# 🛡️ VeriFAI LLM Master User Guide

Welcome to the comprehensive guide for **VeriFAI LLM**. This document will help you master every feature of the platform, from basic scanning to enterprise-scale security enforcement.

---

## 📖 Table of Contents
1.  [The Security Dashboard](#1-the-security-dashboard)
2.  [Security Scanner Workflow](#2-security-scanner-workflow)
3.  [Intelligent Patch Review](#3-intelligent-patch-review)
4.  [Scanning GitHub Repositories](#4-scanning-github-repositories)
5.  [Intelligence Chat](#5-intelligence-chat)
6.  [Command Line Interface (CLI)](#6-command-line-interface-cli)

---

## 1. The Security Dashboard
The **Dashboard** is your primary oversight panel for tracking security trends.

*   **Total Analyses:** The cumulative count of scans performed by your account.
*   **Threats Detected:** The total number of unique vulnerabilities identified.
*   **Risk Index:** A weighted security score (0-100). Higher is better.
*   **Analysis Velocity:** An area chart showing how often you scan your code.
*   **Threat Distribution:** A breakdown by severity (Critical, High, Medium, Low).

---

## 2. Security Scanner Workflow
The **Scanner** is the core of the platform. You can provide code in four ways:

1.  **Paste Code:** Best for quick snippets or individual functions.
2.  **File Upload:** Upload a single source file (`.py`, `.js`, `.java`, etc.).
3.  **ZIP Archive:** Upload an entire project for deep-trace analysis.
4.  **GitHub URL:** Clone and scan any public or private repository.

### Running a Scan
Click **Run Scan** to trigger the multi-stage pipeline:
*   **Stage 1:** Semgrep scans for known patterns.
*   **Stage 2:** Qwen2.5-Coder-32B performs deep reasoning on flagged sections.
*   **Stage 3:** The AI traces dependencies across files to confirm vulnerabilities.
*   **Stage 4:** A detailed PDF report is generated for download.

---

## 3. Intelligent Patch Review
After a scan, visit the **Patch Review** tab to see AI-generated fixes.

*   **Reviewing Changes:** Use the side-by-side diff viewer to compare your original code with the AI's secure version.
*   **Applying Patches:** Click **Apply to File** to staged the fix.
*   **Verification:** Once patches are applied, run a "Dry-Run" scan to verify the vulnerabilities are gone.
*   **Export:** Download the **Secured Project (ZIP)** containing your entire project with all patches permanently applied.

---

## 4. Scanning GitHub Repositories
Integrate your development workflow directly with GitHub.

1.  Navigate to the **Repositories** tab.
2.  Paste your repository URL (e.g., `https://github.com/user/repo`).
3.  Click **Clone**.
4.  Once cloned, click **Scan Repository**.
5.  *Note: For private repos, ensure your `GITHUB_TOKEN` is configured in the Settings tab.*

---

## 5. Intelligence Chat
Need more detail on a specific bug? Use the **Intelligence Chat**.

*   **Context-Aware:** The AI knows about your latest scan results.
*   **Interactive Help:** Ask things like:
    *   *"Why is this SQL injection dangerous in my specific case?"*
    *   *"How can I refactor this function to avoid this high-severity finding?"*
    *   *"Write a unit test that proves this vulnerability exists."*

---

## 6. Command Line Interface (CLI)
For power users and DevOps engineers, use `cli.py` for headless scanning.

```bash
# Basic file scan
python cli.py my_script.py

# Scan a directory and fail the build if score is below 85
python cli.py ./src --fail-under=85

# Export results to JSON
python cli.py ./src --output results.json
```

---

## 💡 Pro Tips for Best Results
*   **Multi-File Context:** When scanning ZIPs or Repos, the AI reads your imports and dependencies to provide much more accurate results.
*   **Temperature Control:** In **Settings**, lower the temperature (e.g., 0.1) for more consistent security fixes, or raise it (e.g., 0.4) for more creative refactoring suggestions.
*   **Session Persistence:** VeriFAI automatically remembers your session. You won't be logged out unless you explicitly click **Sign Out**.

---

## ⚖️ Responsibility Disclaimer
VeriFAI LLM is a powerful tool. Use it only on code you are authorized to test. The AI is a helper, not a replacement for a human security engineer—always verify patches before deploying to production.
