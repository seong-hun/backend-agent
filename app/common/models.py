import os

import dotenv
from langchain.chat_models import init_chat_model


class ModelManager:
    def __init__(self):
        self._registry = {}
        dotenv.load_dotenv()

    def get_model(self, size: str):
        _model_info = self._registry.get(size)
        if not _model_info:
            _model_info = self.init_model(size)

        model = _model_info["model"]
        model.name = _model_info["model_name"]
        return model

    def init_model(self, size):
        model_key = f"MODEL_{size.upper()}"
        model_name = os.getenv(model_key, "gpt-oss-20b")
        model_provider = os.getenv(f"{model_key}_PROVIDER", "openai")

        if model_provider == "openrouter":
            base_url = "https://openrouter.ai/api/v1"
            api_key = os.getenv("OPENROUTER_API_KEY")
            model_provider = "openai"
        elif model_provider == "ollama":
            base_url = os.getenv("OLLAMA_BASE_URL")
            api_key = None
        else:
            base_url = os.getenv(f"{model_key}_PROVIDER_BASE_URL")
            api_key = None

        model = init_chat_model(
            model=model_name,
            model_provider=model_provider,
            base_url=base_url,
            api_key=api_key,
        )
        model_info = {
            "model_name": model_name,
            "model": model,
        }
        self._registry[size] = model_info
        return model_info


model_manager = ModelManager()


def get_model(size: str):
    return model_manager.get_model(size)
