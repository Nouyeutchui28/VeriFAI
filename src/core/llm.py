import os
from openai import OpenAI

def initialize_llm(model="mixtral-8x7b-32768", temperature=0.1):
    """
    Compatibility function for initializing OpenRouter/Groq client.
    """
    groq_api_key = os.getenv("GROQ_API_KEY")
    if not groq_api_key:
        return None
    try:
        return OpenAI(api_key=groq_api_key, base_url="https://openrouter.ai/api/v1")
    except Exception:
        return None
