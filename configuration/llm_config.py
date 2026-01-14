import os
from dataclasses import dataclass
from typing import Union

@dataclass
class OpenAILLMConfig:
    """
    A data class to store configuration details for Openrouter models.

    Attributes:
        model (str): The name of the OpenRouter model to use.
        api_key (str): The API key for authenticating with the OpenAI service.
    """
    model: str
    api_key: str
    base_url: str = "https://openrouter.ai/api/v1"




# OpenAI config map
llm_config_map = {
    "gpt-4o": OpenAILLMConfig(
        model="mistralai/devstral-2512:free",
        api_key=os.environ.get("OPENROUTER_API_KEY"),
        base_url=os.environ.get("OPENAI_API_BASE"),
        
    ),
    "gpt-4.1": OpenAILLMConfig(
        model="gpt-4.1",
        api_key=os.environ.get("OPENROUTER_API_KEY"),
        base_url=os.environ.get("OPENAI_API_BASE"),
    )
}