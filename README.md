<div align="center">
  <img src="https://raw.githubusercontent.com/Nouyeutchui28/VeriFAI/main/assets/logo.png" width="200" alt="VeriFAI LLM Logo">
  
  <h1>🛡️ VeriFAI Agentic PatchOps</h1>
  <p align="center">
    <strong>Autonomous 3-Agent Security Remediation Loop with Dynamic Peer Critique & Self-Healing</strong>
  </p>

  <p align="center">
    <img src="https://img.shields.io/badge/Competition-Open%20Agent%20Hackathon%202026-00E5A0?style=for-the-badge" alt="Hackathon">
    <img src="https://img.shields.io/badge/AI%20Provider-Meterless%20Nightshift-76B900?style=for-the-badge" alt="Meterless Nightshift">
    <img src="https://img.shields.io/badge/Models-NVIDIA%20Nemotron-76B900?style=for-the-badge" alt="NVIDIA">
    <img src="https://img.shields.io/badge/Engine-Meterless%20H--MEM-00B4D8?style=for-the-badge" alt="H-MEM">
    <img src="https://img.shields.io/badge/Data%20Layer-Zetaris%20Data%20Fabric-9D4EDD?style=for-the-badge" alt="Zetaris">
    <img src="https://img.shields.io/badge/Static%20Engine-Semgrep%20AST-2962FF?style=for-the-badge" alt="Semgrep">
  </p>
</div>

<hr style="height: 2px; background: linear-gradient(to right, #00e5a0, #76b900, #00b4d8, #9d4edd);">

**VeriFAI Agentic PatchOps** is an autonomous multi-agent vulnerability remediation system submitted to the **Open Agent Hackathon 2026**. Rather than relying on simple linear prompt wrappers, VeriFAI implements a dynamic 3-agent cooperative loop where agents **plan**, **craft**, **critique each other's code**, and **self-heal from errors** before generating verified, production-ready security patches.

---

## 🏆 Mandatory Sponsor Technology Alignment

| Sponsor Requirement | VeriFAI Implementation | Key Files |
| :--- | :--- | :--- |
| **Primary AI Provider** | **Meterless Nightshift** — Dispatches prompt pipelines and receives streaming completions. | [`src/core/nightshift_client.py`](src/core/nightshift_client.py) |
| **Foundation Models** | **NVIDIA Models** (e.g. `nvidia/llama-3.1-nemotron-70b-instruct`) executed through Nightshift. | [`src/core/nightshift_client.py`](src/core/nightshift_client.py) |
| **Meterless Engine** | **H-MEM (Hierarchical Memory)** — 3-tier memory engine (Tier 1: Working AST findings; Tier 2: Episodic Critique history; Tier 3: Semantic Security invariants). | [`src/core/hmem_engine.py`](src/core/hmem_engine.py) |
| **Data Layer** | **Zetaris Data Fabric & Virtual Data Lake** — Virtualized data queries across code assets, CVE advisory catalogs (`python_advisory_index.json`), and audit telemetry. | [`src/core/zetaris_connector.py`](src/core/zetaris_connector.py) |

---

## 🤖 3-Agent Collaborative Architecture

```mermaid
flowchart TD
    TargetCode["📁 Code Repository / Target File"] --> Planner["📋 Agent 1: Planner Agent\n(Triage, OWASP Scoping, AST Ranking)"]
    
    subgraph HMEM ["🧠 Meterless H-MEM Engine (Hierarchical Memory)"]
        T1["Tier 1: Working Context"]
        T2["Tier 2: Episodic Critique Log"]
        T3["Tier 3: Semantic Invariants"]
    end
    
    Planner -->|Initializes Working Memory| T1
    Planner -->|Remediation Task Package| Specialist["📝 Agent 2: Specialist Agent\n(Nightshift + NVIDIA Nemotron)"]
    
    Zetaris["🌐 Zetaris Data Fabric\n(Virtualized Code & CVE Lake)"] -->|Code Asset + Advisory Context| Specialist
    T2 -->|Prior Rejection Feedback| Specialist
    T3 -->|Verified Security Templates| Specialist
    
    Specialist -->|Draft Candidate Patch| Evaluator["🧐 Agent 3: Evaluator Agent (Critic)\n(AST Syntax Check & Regression Test)"]
    
    Evaluator -->|AST Failure / Residual Flaw| Feedback{"Critic Approval?"}
    Feedback -- "❌ REJECTED" -->|Push Detailed Critique to Memory| T2
    T2 -->|Trigger Self-Healing Loop| Specialist
    
    Feedback -- "✅ APPROVED" --> CleanPatch["🛡️ Verified Clean Security Patch"]
    CleanPatch -->|Promote Invariant| T3
    CleanPatch -->|Sync Audit Telemetry| Zetaris
```

### The Three Agents:
1. **`PlannerAgent` (Triage & Scoping)**:
   - Ingests AST scan findings, maps CWEs to OWASP Top 10 categories, ranks remediation priority, and configures H-MEM Tier-1 Working Memory.
2. **`SpecialistAgent` (Patch Synthesis)**:
   - Queries **Zetaris Data Fabric** for surrounding repo context and vulnerability benchmarks, reads critique history from **H-MEM**, and synthesizes an exact patch using **Meterless Nightshift (NVIDIA Nemotron)**.
3. **`EvaluatorAgent` (Critic & Verifier)**:
   - Validates AST syntax, tests that the vulnerability is neutralized, and checks for regressions. If a flaw remains, it generates actionable critique, stores the episode in **H-MEM**, and prompts the Specialist Agent to self-heal. Once clean, it syncs audit telemetry to **Zetaris**.

---

## ⚡ Quick Start for Judges (Runs in < 2 Minutes)

### 1. Environment Setup
```bash
# Clone the repository
git clone https://github.com/Nouyeutchui28/VeriFAI.git
cd VeriFAI

# No API key or .env file is required. Install and start Ollama locally.
```

### 2. Run the 3-Agent Cooperative CLI Demo
Demonstrates the full autonomous triage, Nightshift NVIDIA patch generation, Critic evaluation, and Zetaris telemetry in your terminal:
```bash
python cli.py sample_misconfig_test.py --agentic
```
Or test the standalone multi-agent pipeline:
```bash
python test_agentic_pipeline.py
```

### 3. Launch the Interactive Dashboard
```bash
streamlit run app.py
```
Navigate to **🤖 Agentic PatchOps** in the sidebar to visualize the real-time agent debate stream, live H-MEM episode count, and Zetaris data telemetry!

### 4. Run the Platform
```bash
# Start the security dashboard
streamlit run app.py
```

---

## ⚖️ Legal & Ethical Usage

**IMPORTANT:** VeriFAI LLM is intended for **defensive security research** and **authorized testing** only. 

*   **Authorized Use Only:** You must only scan codebases you own or have explicit written permission to test.
*   **CFAA Compliance:** Unauthorized scanning may violate international cybercrime laws (e.g., Computer Fraud and Abuse Act).
*   **AI Disclaimer:** AI-generated code may contain "hallucinations" or bugs. Always manually review and test patches in a staging environment before production use.

---

## 🏗️ Architecture

VeriFAI LLM is built on a modular stack:
*   **Frontend:** Streamlit with a custom-engineered "Malware Analyzer" dark theme.
*   **Intelligence:** Local Ollama by default; cloud providers are opt-in.
*   **Static Analysis:** Semgrep OSS Engine.
*   **Storage:** SQLite (Local) & InsForge (Cloud Persistence).

---

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for more details.

---

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

<div align="center">
  <sub>Built with ❤️ for a more secure web by <a href="https://github.com/Nouyeutchui28">@NouyeutchuiBrondon</a></sub>
</div>
