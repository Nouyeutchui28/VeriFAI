import subprocess
import json
import logging
import os
from typing import Optional, Any

logger = logging.getLogger(__name__)

class LocalLLM:
    def __init__(self):
        self.cli_path = "llama-cli" 
        self.model_path = os.path.join(os.getcwd(), "model", "Phi-3-mini-4k-instruct-q4.gguf")
        
    def generate(self, prompt, max_tokens=1024):
        if not os.path.exists(self.model_path):
            return {"error": "Model not found. Please run ./download_model.sh"}
            
        cmd = [
            self.cli_path,
            "-m", self.model_path,
            "-c", "2048",
            "-n", str(max_tokens),
            "--temp", "0.2",
            "-t", "4",
            "--prompt", prompt,
            "--no-display-prompt",
            "--log-disable"
        ]
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            return result.stdout.strip()
        except Exception as e:
            logger.error(f"Inference failed: {e}")
            return f"Error: {e}"

def generate_patch(vulnerability_data):
    llm = LocalLLM()
    prompt = f"Fix this vulnerability: {vulnerability_data}"
    return llm.generate(prompt)

def initialize_llm(temperature: float = 0.2) -> Optional[Any]:
    """
    Initialize the configured LLM client. Local Ollama is the default.
    """
    from openai import OpenAI

    provider = os.getenv("LLM_PROVIDER", "ollama").lower()

    if provider == "ollama":
        ollama_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434/v1")
        ollama_model = os.getenv("OLLAMA_MODEL", "llama3.2:latest")
        try:
            client = OpenAI(base_url=ollama_url, api_key="ollama")
            client.provider_type = "ollama"
            client.active_model = ollama_model
            return client
        except Exception as e:
            logger.debug(f"Ollama initialization failed: {e}")
            return None

    if provider != "cloud":
        logger.error("Unsupported LLM_PROVIDER %r. Choose 'ollama' or 'cloud'.", provider)
        return None

    # Cloud providers are available only when explicitly selected.
    nightshift_key = os.getenv("METERLESS_API_KEY") or os.getenv("NIGHTSHIFT_API_KEY")
    if nightshift_key and not nightshift_key.startswith("mock_"):
        base_url = os.getenv("METERLESS_BASE_URL", "https://api.meterless.ai/v1")
        model = os.getenv("NIGHTSHIFT_MODEL", "nvidia/llama-3.1-nemotron-70b-instruct")
        client = OpenAI(api_key=nightshift_key, base_url=base_url)
        client.provider_type = "nightshift"
        client.active_model = model
        return client

    # 2. Check Cloud API (Groq / OpenRouter)
    groq_key = os.getenv("GROQ_API_KEY")
    if groq_key:
        base_url = "https://openrouter.ai/api/v1" if groq_key.startswith("sk-or-") else "https://api.groq.com/openai/v1"
        model = os.getenv("GROQ_MODEL", "qwen/qwen-2.5-coder-32b-instruct")
        client = OpenAI(api_key=groq_key, base_url=base_url)
        client.provider_type = "cloud"
        client.active_model = model
        return client

    logger.warning("Cloud LLM selected, but no supported cloud provider key is configured.")
    return None

def list_local_ollama_models() -> list:
    """
    List models available in local Ollama instance.
    Checks Ollama API endpoint or falls back to CLI. Returns empty list if Ollama is unreachable.
    """
    import urllib.request

    base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    api_url = base_url.rstrip("/")
    if api_url.endswith("/v1"):
        api_url = api_url[:-3]
    api_endpoint = f"{api_url}/api/tags"

    try:
        req = urllib.request.Request(api_endpoint, headers={"User-Agent": "VeriFAI-LLM"})
        with urllib.request.urlopen(req, timeout=2) as response:
            if response.status == 200:
                data = json.loads(response.read().decode("utf-8"))
                return [m["name"] for m in data.get("models", []) if "name" in m]
    except Exception as e:
        logger.debug(f"Failed to fetch Ollama models via API: {e}")

    try:
        import shutil
        ollama_bin = shutil.which("ollama")
        if ollama_bin:
            res = subprocess.run([ollama_bin, "list"], capture_output=True, text=True, timeout=3)
            if res.returncode == 0:
                lines = res.stdout.strip().splitlines()
                models = []
                for line in lines[1:]:
                    parts = line.split()
                    if parts:
                        models.append(parts[0])
                return models
    except Exception as e:
        logger.debug(f"Failed to fetch Ollama models via CLI: {e}")

    return []
