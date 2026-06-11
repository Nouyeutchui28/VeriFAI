# 🚀 VeriFAI LLM Setup & Deployment Guide

Follow these steps to get your enterprise security analysis platform running in minutes.

---

## 🛠️ Prerequisites

Before you begin, ensure you have the following installed:
*   **Python 3.10 or higher**
*   **Git**
*   **pip** (Python package manager)

### 🔑 Required API Keys
1.  **Hugging Face Token:** Create a free account at [huggingface.co](https://huggingface.co/) and generate a **Read** token at [Settings > Tokens](https://huggingface.co/settings/tokens). This is required to access the **Qwen2.5-Coder-32B** model.
2.  **GitHub Token (Optional):** Required only if you plan to scan your private repositories. Generate a Classic PAT at [GitHub Settings](https://github.com/settings/tokens).

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

1.  **Environment Variables:**
    Copy the template and fill in your keys:
    ```bash
    cp .env.example .env
    ```
    Edit `.env` and add:
    *   `HF_TOKEN=hf_...`
    *   `GITHUB_TOKEN=ghp_...` (optional)

2.  **Database Setup:**
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
6.  Go to the **Environment** settings of your new service and add your `HF_TOKEN`.

### Method 3: Docker (Custom)
If you prefer using Docker:
```bash
# Build the image
docker build -t verifai-llm .

# Run the container
docker run -p 8501:8501 --env-file .env verifai-llm
```

---

## ✅ Post-Installation Checklist

1.  Open `http://localhost:8501` (or your Render URL) in your browser.
2.  **Sign In:** Create a new account or log in.
3.  **Check Sidebar:** Verify that it says **✅ Qwen2.5-Coder-32B Active**.
4.  **Test Scan:** Paste a sample vulnerable script and verify detection.

---

## 🔧 Troubleshooting

| Issue | Solution |
| :--- | :--- |
| **Model Error (401/403)** | Your `HF_TOKEN` is invalid or missing. Update it in `.env` or Render settings. |
| **Semgrep Not Found** | Ensure `semgrep` is in your PATH. Try `pip install semgrep`. |
| **Login Persistence Fails** | Check if the file `.auth_session.json` is writable. |
| **Dashboard Zeros** | Run at least one scan to populate the dashboard metrics. |
