<div align="center">
  <img src="https://raw.githubusercontent.com/Nouyeutchui28/VeriFAI/main/assets/logo.png" width="200" alt="VeriFAI LLM Logo">
  
  <h1>🛡️ VeriFAI LLM</h1>
  <p align="center">
    <strong>Enterprise-Grade Security Analysis powered by qwen-2.5-coder-32b & Semgrep</strong>
  </p>

  <p align="center">
    <img src="https://img.shields.io/badge/Model-qwen--2.5--coder--32b-blueviolet?style=for-the-badge" alt="Model">
    <img src="https://img.shields.io/badge/Analysis-Semgrep-2962FF?style=for-the-badge" alt="Semgrep">
    <img src="https://img.shields.io/badge/Interface-Streamlit-FF4B4B?style=for-the-badge" alt="Streamlit">
    <img src="https://img.shields.io/badge/Backend-FastAPI-009688?style=for-the-badge" alt="FastAPI">
  </p>
</div>

<hr style="height: 2px; background: linear-gradient(to right, #1a237e, #0d47a1);">

VeriFAI LLM is an advanced security analysis platform that fuses the surgical precision of **Semgrep's** static analysis with the deep reasoning capabilities of the **qwen-2.5-coder-32b** model. Designed for developers and security researchers, it provides a comprehensive suite for detecting, analyzing, and auto-remediating vulnerabilities in modern codebases.

---

## ✨ Key Features

### 🧠 Ultra-Intelligence Engine
Powered by **qwen-2.5-coder-32b**, VeriFAI provides deep-trace security analysis that understands complex logic, data flow, and architectural vulnerabilities that traditional tools miss.

### 📊 Security Command Center (Dashboard)
Real-time oversight of your security posture.
*   **Analysis Velocity:** Track your scanning frequency over time.
*   **Threat Distribution:** Visual breakdown of vulnerabilities by severity (Critical, High, Medium, Low).
*   **Risk Index:** A weighted score that measures the overall health of your projects.

### 🛠️ Interactive Remediation (Patch Review)
Don't just find bugs—fix them.
*   **AI-Generated Patches:** Get high-quality, secure-by-default code fixes.
*   **Side-by-Side Diff:** Review changes before applying them.
*   **Project-Wide Export:** Apply multiple fixes and export a secured ZIP of your entire project.

### 📦 Agentic Multi-File Scanning
VeriFAI can clone GitHub repositories or process ZIP archives, tracing dependencies across multiple files to find cross-component vulnerabilities.

---

## 🚀 Quick Start

### 1. Prerequisites
*   Python 3.10+
*   [Groq API Key](https://console.groq.com/keys) (Required for the Intelligence Engine)

### 2. Installation
```bash
# Clone the repository
git clone https://github.com/Nouyeutchui28/VeriFAI.git
cd VeriFAI

# Install dependencies
pip install -r requirements.txt
```

### 3. Configuration
Create a `.env` file from the example:
```bash
cp .env.example .env
```
Add your `GROQ_API_KEY` and `GITHUB_TOKEN` to the `.env` file.

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
*   **Intelligence:** Groq API (Qwen-2.5-Coder-32B or other supported models).
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
