import os

from dotenv import load_dotenv
from autogen import LLMConfig

load_dotenv()

LLM_PROVIDER = os.getenv("LLM_PROVIDER", "ollama").lower()
LLM_BASE_URL = os.getenv("LLM_BASE_URL", "http://localhost:11434")
LLM_NUM_CTX = int(os.getenv("LLM_NUM_CTX", "8192"))

REASONING_MODEL = os.getenv("REASONING_MODEL", "qwen3:latest")
REASONING_TEMPERATURE = float(os.getenv("REASONING_TEMPERATURE", "0.7"))

CODE_MODEL = os.getenv("CODE_MODEL", "qwen3:latest")
CODE_TEMPERATURE = float(os.getenv("CODE_TEMPERATURE", "0.3"))


def _build_config(model, temperature):
    if LLM_PROVIDER == "ollama":
        return LLMConfig(
            {
                "api_type": "ollama",
                "model": model,
                "client_host": LLM_BASE_URL,
                "num_ctx": LLM_NUM_CTX,
                "temperature": temperature,
            }
        )
    elif LLM_PROVIDER == "lmstudio":
        return LLMConfig(
            {
                "model": model,
                "base_url": LLM_BASE_URL,
                "api_key": "lm-studio",
                "temperature": temperature,
            }
        )
    else:
        raise ValueError(f"Unsupported LLM_PROVIDER: {LLM_PROVIDER}. Use 'ollama' or 'lmstudio'.")


reasoning_config = _build_config(REASONING_MODEL, REASONING_TEMPERATURE)
code_config = _build_config(CODE_MODEL, CODE_TEMPERATURE)
