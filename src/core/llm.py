import os
import streamlit as st
import json
import requests
import dotenv
from typing import Any, List, Optional
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import BaseMessage, AIMessage, HumanMessage, SystemMessage
from langchain_core.outputs import ChatResult, ChatGeneration

class LocalOllamaChat(BaseChatModel):
    """
    A custom wrapper for local Ollama API that inherits from BaseChatModel
    for full LangChain compatibility.
    """
    model_name: str = "secure-patch-model"
    temperature: float = 0
    url: str = "http://127.0.0.1:11434/v1/chat/completions"

    def _generate(
        self,
        messages: List[BaseMessage],
        stop: Optional[List[str]] = None,
        run_manager: Optional[Any] = None,
        **kwargs: Any,
    ) -> ChatResult:
        """
        Implementation of the required _generate method.
        """
        formatted_messages = []
        for msg in messages:
            if isinstance(msg, SystemMessage):
                role = "system"
            elif isinstance(msg, AIMessage):
                role = "assistant"
            else:
                role = "user"
            formatted_messages.append({"role": role, "content": msg.content})

        payload = {
            "model": self.model_name,
            "messages": formatted_messages,
            "options": {
                "temperature": self.temperature,
                "num_thread": 4,      # Optimized for physical cores (4) to avoid thread thrashing
                "num_ctx": 4096       # Balanced context for speed + depth
            },
            "stream": False,
            "keep_alive": -1          # Keep in memory permanently while app is active
        }

        try:
            response = requests.post(self.url, json=payload, timeout=300)
            response.raise_for_status()
            data = response.json()
            
            content = data["choices"][0]["message"]["content"]
            message = AIMessage(content=content)
            generation = ChatGeneration(message=message)
            return ChatResult(generations=[generation])
        except Exception as e:
            st.error(f"Ollama Connection Error: {str(e)}")
            raise

    @property
    def _llm_type(self) -> str:
        return "ollama-local"

def initialize_llm(model="secure-patch-model", temperature=0):
    """
    Initialize and return a local Ollama model wrapper.
    """
    # Load environment variables (kept for compatibility)
    dotenv.load_dotenv()

    try:
        # We always return the local model as requested
        return LocalOllamaChat(model_name="secure-patch-model", temperature=temperature)
    except Exception as e:
        st.error(f"❌ Local LLM Error: {str(e)}")
        return None