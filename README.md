<div align="center">
  <svg width="240" height="240" viewBox="0 0 240 240" xmlns="http://www.w3.org/2000/svg">
    <defs>
      <linearGradient id="grad" x1="0%" y1="0%" x2="100%" y2="100%">
        <stop offset="0%" style="stop-color:#1a237e;stop-opacity:1" />
        <stop offset="100%" style="stop-color:#0d47a1;stop-opacity:1" />
      </linearGradient>
    </defs>
    <circle cx="120" cy="120" r="110" fill="url(#grad)" />
    <text x="120" y="130" text-anchor="middle" fill="white" font-family="Arial" font-weight="bold" font-size="42">VeriFAI LLM</text>
    <text x="120" y="155" text-anchor="middle" fill="white" font-family="Arial" font-size="16">Security Analysis Tool</text>
  </svg>

  <h1>VeriFAI LLM</h1>
  <p align="center">
    <strong>Advanced Security Analysis Powered by Large Language Models and Semgrep</strong>
  </p>

  <p align="center">
    <a href="https://github.com/codebytemirza/VeriFAI-LLM/stargazers">
      <img src="https://img.shields.io/github/stars/codebytemirza/VeriFAI-LLM?style=for-the-badge" alt="Stars">
    </a>
    <a href="https://github.com/codebytemirza/VeriFAI-LLM/network/members">
      <img src="https://img.shields.io/github/forks/codebytemirza/VeriFAI-LLM?style=for-the-badge" alt="Forks">
    </a>
    <a href="https://github.com/codebytemirza/VeriFAI-LLM/issues">
      <img src="https://img.shields.io/github/issues/codebytemirza/VeriFAI-LLM?style=for-the-badge" alt="Issues">
    </a>
    <a href="https://github.com/codebytemirza/VeriFAI-LLM/blob/main/LICENSE">
      <img src="https://img.shields.io/github/license/codebytemirza/VeriFAI-LLM?style=for-the-badge" alt="License">
    </a>
  </p>
</div>

<hr style="height: 2px; background: linear-gradient(to right, #1a237e, #0d47a1);">

<div align="center">
  <img src="docs/assets/demo.gif" alt="VeriFAI LLM Demo" style="max-width: 800px; border-radius: 8px; box-shadow: 0 4px 8px rgba(0,0,0,0.1);">
</div>

<h2 align="center">Intelligent Security Analysis</h2>

VeriFAI LLM combines the precision of Semgrep's static analysis with the power of Local Large Language Models (via Ollama) to deliver comprehensive security scanning, interactive vulnerability discussions, and intelligent rule generation capabilities.

<div align="center">
  <table>
    <tr>
      <th width="33%">Static Analysis</th>
      <th width="33%">Local AI Intelligence</th>
      <th width="33%">Custom Rules</th>
    </tr>
    <tr align="center">
      <td>Semgrep-powered code scanning with pattern matching</td>
      <td>Ollama-driven vulnerability assessment (Phi-3)</td>
      <td>Automated security rule generation</td>
    </tr>
  </table>
</div>

## Core Features

<table>
<tr>
<td width="50%" valign="top">

**Analysis Engine**
- Dual-engine security scanning
- Pattern-based vulnerability detection
- Machine learning insights
- Real-time code analysis
- Comprehensive security reports

</td>
<td width="50%" valign="top">

**Intelligence Layer**
- Context-aware security chat
- Vulnerability explanation
- Code improvement suggestions
- Security best practices
- Custom rule generation

</td>
</tr>
<tr>
<td width="50%" valign="top">

**Patch Management** ✨ NEW
- AI-generated security patches
- Side-by-side diff preview
- Interactive patch review
- One-click patch application
- Automatic backup creation
- Patch validation (dry-run)

</td>
<td width="50%" valign="top">

**Safety Features**
- Git-integrated patching
- Rollback support
- Backup creation
- Dry-run validation
- Error recovery

</td>
</tr>
</table>

## Quick Start

```bash
# Clone repository
git clone https://github.com/codebytemirza/VeriFAI-LLM.git

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env

# Launch application
streamlit run app.py
```

<details>
<summary><strong>Docker Deployment</strong></summary>

```bash
docker build -t verifai_llm .
docker run -p 8501:8501 --env-file .env verifai_llm
```
</details>

## Architecture

<div align="center">
  <table>
    <tr>
      <th>Component</th>
      <th>Technology</th>
      <th>Purpose</th>
    </tr>
    <tr>
      <td>Static Analysis</td>
      <td>Semgrep</td>
      <td>Pattern matching & vulnerability detection</td>
    </tr>
    <tr>
      <td>AI Engine</td>
      <td>Groq LLM</td>
      <td>Intelligent code analysis</td>
    </tr>
    <tr>
      <td>Interface</td>
      <td>Streamlit</td>
      <td>Interactive web application</td>
    </tr>
  </table>
</div>

## Security Analysis Workflow

1. **Code Input**
   - Direct code entry
   - File upload support
   - Multi-file analysis
   
2. **Analysis Process**
   - Semgrep pattern scanning
   - LLM-based code review
   - Vulnerability assessment
   
3. **Results & Insights**
   - Detailed findings report
   - Security recommendations
   - Interactive consultation

## Advanced Configuration

| Parameter | Description | Default |
|-----------|-------------|----------|
| Model | LLM model selection | deepseek-r1 |
| Temperature | Response variation | 0.1 |
| Rules | Custom Semgrep rules | Optional |
| Metrics | Performance tracking | Disabled |

## Development

```bash
# Setup development environment
python -m venv .venv
source .venv/bin/activate

# Install development dependencies
pip install -r requirements-dev.txt
```

## Contributing

We welcome contributions to VeriFAI LLM. Please review our [Contributing Guidelines](CONTRIBUTING.md) before submitting pull requests.

<table>
<tr>
<td>

**Contribution Process**
1. Fork repository
2. Create feature branch
3. Implement changes
4. Submit pull request

</td>
<td>

**Code Standards**
- PEP 8 compliance
- Comprehensive testing
- Documentation updates
- Clean commit history

</td>
</tr>
</table>

## License

VeriFAI LLM is released under the MIT License. See the [LICENSE](LICENSE) file for details.

<div align="center">
  <h2>Technology Stack</h2>
  <p>
    <a href="https://semgrep.dev/"><img src="https://img.shields.io/badge/Analysis-Semgrep-2962FF?style=for-the-badge" alt="Semgrep"></a>
    <a href="https://ollama.com/"><img src="https://img.shields.io/badge/LLM-Ollama-000000?style=for-the-badge" alt="Ollama"></a>
    <a href="https://streamlit.io/"><img src="https://img.shields.io/badge/UI-Streamlit-FF4B4B?style=for-the-badge" alt="Streamlit"></a>
  </p>
</div>

<div align="center">
  <sub>Built with precision by <a href="https://github.com/codebytemirza">@codebytemirza</a></sub>
</div>
/div>
# VeriFAI
