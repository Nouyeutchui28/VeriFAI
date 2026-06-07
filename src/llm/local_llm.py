import os
import threading
import logging
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)

_model_lock = threading.Lock()
_generator = None


def _load_generator(model_name: Optional[str] = None, device: Optional[int] = None):
    global _generator
    if _generator is not None:
        return _generator

    with _model_lock:
        if _generator is not None:
            return _generator

        try:
            from transformers import pipeline, AutoTokenizer, AutoModelForCausalLM
            model_name = model_name or os.environ.get("LOCAL_MODEL_NAME", "facebook/opt-1.3b")
            device_flag = -1
            # prefer GPU if available and requested
            if device is None:
                try:
                    import torch
                    device_flag = 0 if torch.cuda.is_available() else -1
                except Exception:
                    device_flag = -1
            else:
                device_flag = device

            logger.info(f"Loading local model: {model_name} on device {device_flag}")
            _generator = pipeline("text-generation", model=model_name, device=device_flag)
            return _generator
        except Exception as e:
            logger.exception("Failed to load local model")
            raise


class LocalLLM:
    def __init__(self, model_name: Optional[str] = None, device: Optional[int] = None):
        self.model_name = model_name or os.environ.get("LOCAL_MODEL_NAME", "facebook/opt-1.3b")
        self.device = device
        self._gen = None

    def _ensure(self):
        if self._gen is None:
            self._gen = _load_generator(self.model_name, self.device)

    def generate(self, prompt: str, max_tokens: int = 256, temperature: float = 0.1, **kwargs) -> Dict[str, Any]:
        """Generate text for a given prompt using the local model."""
        self._ensure()
        # transformers pipeline expects max_length total tokens; approximate by adding prompt length
        try:
            out = self._gen(prompt, max_length=max_tokens, do_sample=(temperature > 0.0), temperature=temperature, **kwargs)
            # pipeline returns a list of dicts with 'generated_text'
            text = out[0]["generated_text"] if isinstance(out, list) and len(out) > 0 else str(out)
            return {"text": text}
        except Exception as e:
            logger.exception("Local LLM generation failed")
            return {"error": str(e)}


def initialize_local_llm(model_name: Optional[str] = None, device: Optional[int] = None) -> LocalLLM:
    return LocalLLM(model_name=model_name, device=device)
