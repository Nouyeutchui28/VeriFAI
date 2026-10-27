# 🚀 VeriFAI LLM Setup & Deployment Guide

Follow these steps to get your enterprise security analysis platform running in minutes.

---

## 🛠️ Prerequisites

Before you begin, ensure you have the following installed:
*   **Python 3.10 or higher**
*   **Git**
*   **pip** (Python package manager)

### 🔑 LLM Engine Options
1.  **Local AI (Default):** Install [Ollama](https://ollama.com) and start it at `http://localhost:11434`. No API key or `.env` file is required.
2.  **Cloud AI (Optional):** Cloud providers are disabled by default. To opt in, set `LLM_PROVIDER=cloud` and provide the provider credential through your process environment, not a project file.

---

## 📥 Installation

1.  **Clone the Repository:**
    ```bash
    git clone https://github.com/Nouyeutchui28/VeriFAI.git
    cd VeriFAI
    ```

2.  **Create a Virtual Environment:**
    ```bash
    python -m venv venv
    
    # Windows:
    venv\Scripts\activate
    
    # Linux/macOS:
    source venv/bin/activate
    ```

3.  **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

---

## ⚙️ Configuration

1.  **Database Setup:**
    The system will automatically initialize a local `verifai_llm.db` (SQLite) upon the first run. For cloud persistence, ensure your InsForge project is configured in `.insforge/project.json`.

---

## 🚀 Deployment

### Method 1: All-in-One (Local)
```bash
streamlit run app.py
```

### Method 2: Render (Cloud)
VeriFAI LLM is pre-configured for **Render**.
1.  **Fork** this repository to your GitHub account.
2.  Log in to [Render](https://render.com/).
3.  Click **New +** > **Blueprint**.
4.  Connect your GitHub repository.
5.  Render will automatically detect the `render.yaml` file and set up:
    *   The Streamlit Web Service.
    *   Necessary environment variables.
6.  Local Ollama is required for local model inference. No provider API key is required.

### Method 3: Docker (Custom)
If you prefer using Docker:
```bash
# Build the image
docker build -t verifai-llm .

# Run the container (no env file required)
docker run -p 8501:8501 verifai-llm
```

---

## ✅ Post-Installation Checklist

1.  Open `http://localhost:8501` (or your Render URL) in your browser.
2.  **Sign In:** Create a new account or log in.
3.  **Check Sidebar:** Verify that it says **✅ qwen-2.5-coder-32b Active**.
4.  **Test Scan:** Paste a sample vulnerable script and verify detection.

---

## 🔧 Troubleshooting

| Issue | Solution |
| :--- | :--- |
| **Model unavailable** | Start Ollama at `http://localhost:11434` and make sure a model is installed. |
| **Semgrep Not Found** | Ensure `semgrep` is in your PATH. Try `pip install semgrep`. |
| **Login Persistence Fails** | Check if the file `.auth_session.json` is writable. |
| **Dashboard Zeros** | Run at least one scan to populate the dashboard metrics. |
