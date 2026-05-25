# VeriFAI LLM Setup Guide

## 🚀 Quick Start

### 1️⃣ Install Ollama

1. Download and install Ollama from **https://ollama.com/**
2. Ensure Ollama is running in your background/system tray.

### 2️⃣ Prepare the Security Model

Open your terminal and run the following commands to pull the base model and create the specialized security engine:

```bash
# Pull the base Phi-3 model
ollama pull phi3

# Create the custom secure-patch-model (if using provided Modelfile)
ollama create secure-patch-model -f Modelfile
```

### 3️⃣ Configure Environment

1. Copy the example environment file:
   ```bash
   cp .env.example .env
   ```
2. Open `.env` and configure your database and secret keys. (No API keys required for the local engine!)

### 4️⃣ Launch the Application

```bash
# Start both Backend and Frontend
./start_app.sh
```

Or run them manually:
```bash
# Terminal 1: Backend
python -m uvicorn src.api.main:app --port 8000

# Terminal 2: Frontend
streamlit run app.py --server.port 8502
```

---

## ✅ Verify Setup

1. Open the app at `http://localhost:8502`
2. Check the **Model Status** in the sidebar.
3. You should see **✅ Local AI Active (secure-patch-model)**.
4. If you see a connection error, ensure Ollama is running and you've run `ollama create secure-patch-model`.

---

## 🔧 Troubleshooting

| Error | Solution |
|-------|----------|
| **❌ Ollama Connection Error** | Ensure the Ollama app is running on your machine. |
| **⚠️ Model not found** | Run `ollama list` to check if `secure-patch-model` exists. |
| **Timeout during analysis** | First run may take longer to load the model into RAM. |

---

## 🎯 What Next?

Once the local engine is active:
1. **Direct Code**: Paste code in the input area
2. **Upload ZIP**: Drop a `.zip` file with project code
3. **Click**: Run Security Scan 🔍
4. **View Results**: Check AI Analysis and Patch Suggestions tabs
5. **Apply**: Download or apply patches directly

Enjoy your private, local security analysis! 🛡️
