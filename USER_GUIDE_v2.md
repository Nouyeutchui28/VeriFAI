# 🛡️ VeriFAI LLM: Master User Guide (Enterprise Edition)

VeriFAI LLM has been upgraded to a professional-grade security platform. This guide explains how to leverage its most powerful new features.

---

## 1. Real-Time Security Command Center (Dashboard)
The home screen is now your executive oversight panel.
*   **What it does:** Tracks your personal scan history, total vulnerabilities found, and successful auto-remediations.
*   **How to use:** Simply log in and click **🏠 Dashboard**. 
*   **Key Metric:** Watch your **Risk Index**. A higher score means your codebases are becoming safer over time as you apply the AI's patches.

---

## 2. Agentic Deep-Trace Analysis (AI Intelligence)
The AI now "understands" your project structure by browsing related files.
*   **What it does:** If you scan a file that imports a database controller, the AI automatically reads that controller to trace if your data is being handled securely.
*   **How to use:** Upload a **ZIP file** or a **GitHub Repository**. The "Agentic Navigator" only works on multi-file projects where it can trace dependencies.
*   **Pro Tip:** Look for the "RELATED CONTEXT FILES" mentioned in the AI Security Analysis section—this shows you which files the AI "browsed" to find the bug.

---

## 3. High-Speed Parallel Scanner
Scans are now up to 4x faster on large projects.
*   **What it does:** Instead of scanning one file at a time, VeriFAI uses all your CPU cores to analyze multiple vulnerable files simultaneously.
*   **How to use:** Start a scan as usual. You will see a live progress bar showing: *Analyzed 3/10 vulnerable files...*
*   **Benefit:** Even large repositories with dozens of files can now be audited in under 2 minutes.

---

## 4. Multi-File Patch Review & Export
You can now fix entire projects and download the "Clean" version.
*   **How to use:**
    1.  After a scan, go to the **🛠️ Patch Review** tab.
    2.  Use the **Dropdown Selector** at the top to switch between different vulnerable files.
    3.  Review the fix, click **✅ Apply to File** for each one.
    4.  Once finished, click **🛡️ Verify Fix**. 
    5.  Download the **📦 Secured Project (ZIP)** to get your entire project back with all fixes applied.

---

## 5. CI/CD "Gatekeeper" Mode (CLI)
Protect your production branch by blocking insecure code.
*   **What it does:** Forces the scanner to return an "Error" if the security score is too low, stopping your build or merge.
*   **How to run (Manually):**
    ```bash
    # Fail the process if security score is below 90
    python cli.py /path/to/your/project --fail-under=90
    ```
*   **GitHub Integration:** 
    I have created a `.github/workflows/verifai-gatekeeper.yml` file. Copy this into your `.github/workflows/` folder on GitHub. Every time someone makes a Pull Request, VeriFAI will automatically scan the code and "Red-X" the PR if it finds critical bugs.

---

## 🔧 Technical Summary for this Computer
*   **AI Engine:** Local Ollama (Phi-3)
*   **Hardware Setup:** Optimized for 4-core physical CPU performance.
*   **Memory:** `keep_alive` is active, so the second scan will be much faster than the first!

Enjoy your private, local, and professional security auditor! 🛡️🚀
