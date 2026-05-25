<div align="center">
  <img src="assets/logo_transparent.png" width="240" alt="VeriFAI LLM Logo">
  <h1>VeriFAI LLM</h1>
  <p align="center">
    <strong>Enterprise-Grade, Privacy-First Security Analysis Powered by Local AI (Ollama)</strong>
  </p>

  <p align="center">
    <a href="https://github.com/Nouyeutchui28/VeriFAI/stargazers">
      <img src="https://img.shields.io/github/stars/Nouyeutchui28/VeriFAI?style=for-the-badge&color=00e5a0" alt="Stars">
    </a>
    <a href="https://github.com/Nouyeutchui28/VeriFAI/issues">
      <img src="https://img.shields.io/github/issues/Nouyeutchui28/VeriFAI?style=for-the-badge&color=ff4060" alt="Issues">
    </a>
    <a href="https://github.com/Nouyeutchui28/VeriFAI/blob/main/LICENSE">
      <img src="https://img.shields.io/github/license/Nouyeutchui28/VeriFAI?style=for-the-badge&color=0066ff" alt="License">
    </a>
  </p>
</div>

<hr style="height: 2px; background: linear-gradient(to right, #001a33, #0066ff);">

## 🛡️ Project Overview

**VeriFAI LLM** is a sophisticated security analysis platform designed for the modern enterprise. Unlike traditional scanners that rely solely on static patterns, VeriFAI combines the mathematical precision of **Semgrep** with the deep contextual reasoning of **Local Large Language Models (Ollama)**. 

Our mission is to provide developers with a private, high-speed auditor that not only finds vulnerabilities but also **writes the code to fix them**.

---

## 🧠 AI Intelligence & Training

### How the Model "Thinks"
VeriFAI LLM uses a **Hybrid Knowledge Architecture**. Instead of sending your sensitive code to the cloud, we leverage a locally hosted **Phi-3** engine that has been specialized for cybersecurity.

<div align="center">
  <img src="https://images.unsplash.com/photo-1550751827-4bd374c3f58b?auto=format&fit=crop&w=800&q=80" width="600" alt="Cybersecurity Data Analysis" style="border-radius: 12px; margin: 20px 0;">
</div>

**The Alignment Strategy:**
1.  **Knowledge Kernel:** We "anchor" the AI with the **OWASP Top 10** dataset and thousands of curated "Vulnerable vs. Secure" code pairs.
2.  **Persona Hardening:** The system is programmed with a **Senior Security Auditor** persona, forcing it to prioritize exploit path analysis and logical data flow over generic coding suggestions.
3.  **Deterministic Logic:** By locking the engine to a **0.0 Temperature**, we ensure that every analysis is logical, repeatable, and enterprise-ready.

---

## 🚀 Enterprise Features

### 1. Agentic Deep-Trace Analysis
VeriFAI LLM is "Agentic." It doesn't just scan one file; it **navigates your project**. It automatically resolves local module dependencies (Controllers, Models, Helpers) to trace how user input moves from your API routes to your database, catching logical bugs that single-file scanners miss.

<div align="center">
  <img src="https://images.unsplash.com/photo-1531482615713-2afd69097998?auto=format&fit=crop&w=800&q=80" width="600" alt="African Tech Team Collaboration" style="border-radius: 12px; margin: 20px 0;">
</div>

### 2. CI/CD Gatekeeper Mode
VeriFAI can act as an automated security officer. Using the CLI, you can set a **Security Score threshold (0-100)**. If a Pull Request drops the score below your standard (e.g., 80), VeriFAI will **block the build**, ensuring only secure code reaches production.

### 3. Parallel Multi-File Scanner
Our optimized pipeline utilizes your computer's full hardware potential. By running multiple AI analyses in parallel across CPU cores, we deliver deep-scan results 4x faster than traditional AI agents.

---

## 🛠️ Technology Stack

| Layer | Technology | Purpose |
| :--- | :--- | :--- |
| **Static Engine** | [Semgrep](https://semgrep.dev/) | High-speed pattern matching & CVE detection |
| **AI Reasoning** | [Ollama (Phi-3)](https://ollama.com/) | 100% Private, local contextual analysis |
| **Interface** | [Streamlit](https://streamlit.io/) | Sleek, interactive Security Command Center |
| **Backend** | [FastAPI](https://fastapi.tiangolo.com/) | Production-grade high-performance API node |
| **Database** | [SQLAlchemy](https://www.sqlalchemy.org/) | Encrypted storage for scan history & metrics |

---

## ⚡ Quick Start

```bash
# 1. Clone the repository
git clone https://github.com/Nouyeutchui28/VeriFAI.git

# 2. Setup your local AI
ollama pull phi3
ollama create secure-patch-model -f Modelfile

# 3. Launch the platform
./start_app.sh
```

---

<div align="center">
  <sub>Built with precision for the global developer community.</sub><br>
  <strong>VeriFAI LLM: Secure. Private. Fast.</strong>
</div>
