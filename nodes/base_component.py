"""
This module defines the BaseComponent class, which provides a foundation
for managing LLM-based workflows.
"""
import sys
import time
from pathlib import Path
from typing import Optional, Type, Any

# Ensure project root is in Python path for imports
_project_root = Path(__file__).parent.parent
if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables.base import RunnableSequence
from langchain_openai import ChatOpenAI
from pydantic import BaseModel
from debate_state import DebateState
from configuration.llm_config import OpenAILLMConfig


class BaseComponent:
    """
    A foundational class for managing LLM-based workflows.
    """

    def __init__(
        self,
        llm_config: OpenAILLMConfig,
        temperature: float = 0.0,
        max_retries: int = 5,
    ):
        """
        Initializes the BaseComponent with optional LLM configuration and temperature.

        Args:
            llm_config (OpenAILLMConfig): Configuration for OpenRouter.
            temperature (float): Controls the randomness of LLM outputs. Defaults to 0.0.
            max_retries (int): How many times to retry on 429 errors.
        """
        self.llm: Optional[ChatOpenAI] = None
        self.output_parser: Optional[StrOutputParser] = None
        self.state: Optional[DebateState] = None
        self.prompt_template: Optional[ChatPromptTemplate] = None
        self.chain: Optional[RunnableSequence] = None
        self.max_retries = max_retries

        if llm_config is not None:
            self.llm = self._init_llm(llm_config, temperature)
            self.output_parser = StrOutputParser()


    def _init_llm(self, llm_config_map: OpenAILLMConfig, temperature: float):
        """
        Initializes an LLM instance for OpenAI.
        """
        if isinstance(llm_config_map, OpenAILLMConfig): # checks if the llm_config_map is of type OpenAILLMConfig
            return ChatOpenAI(
                model=llm_config_map.model,
                api_key=llm_config_map.api_key,
                base_url=llm_config_map.base_url,
                temperature=temperature,
            )
        else:
            raise ValueError("Unsupported LLMConfig type. Expected OpenAILLMConfig.")
    def validate_initialization(self) -> None:
        if not self.llm:
            raise ValueError("LLM is not initialized. Ensure `llm_config` is provided.")
        if not self.output_parser:
            raise ValueError("Output parser is not initialized.")

    def execute_chain(self, inputs: Any) -> Any:
        if not self.chain:
            raise ValueError("No chain is initialized for execution.")

        retry_wait = 1  # Initial wait time in seconds

        for attempt in range(self.max_retries):
            try: #Starts a block of code that might crash
                result = self.chain.invoke(inputs)
                return result

            except Exception as e:
                # If the error mentions 429, do exponential backoff and retry
                if "429" in str(e):
                    print(
                        f"Rate limit reached. Retrying in {retry_wait} seconds... "
                        f"(Attempt {attempt + 1}/{self.max_retries})"
                    )
                    time.sleep(retry_wait)
                    retry_wait *= 2 #Exponential Backoff
                else:
                    print(f"Unexpected error: {str(e)}")
                    raise e

        raise Exception("API request failed after maximum number of retries")

    def create_chain(
        self, system_template: str, human_template: str
    ) -> RunnableSequence:
        """
        Creates a chain for unstructured outputs.
        """
        self.validate_initialization()
        self.prompt_template = ChatPromptTemplate.from_messages(
            [
                ("system", system_template),
                ("human", human_template),
            ]
        )
        self.chain = self.prompt_template | self.llm | self.output_parser
        return self.chain

    def create_structured_output_chain(
        self, system_template: str, human_template: str, output_model: Type[BaseModel]
    ) -> RunnableSequence:
        """
        Creates a chain that yields structured outputs (parsed into a Pydantic model).
        """
        self.validate_initialization()
        self.prompt_template = ChatPromptTemplate.from_messages(
            [
                ("system", system_template),
                ("human", human_template),
            ]
        )
        self.chain = self.prompt_template | self.llm.with_structured_output(output_model, method="json_mode")
        return self.chain

    def __call__(self, state: DebateState) -> None:
        """
        Updates the node's local copy of the state.
        """
        self.state = state
        for key, value in state.items():
            setattr(self, key, value)
