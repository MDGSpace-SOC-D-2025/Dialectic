import sys
from pathlib import Path
_project_root = Path(__file__).parent.parent
if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))


from nodes.base_component import BaseComponent
from prompts.judge_prompt import JUDGE_SYSTEM_PROMPT, JUDGE_HUMAN_PROMPT
from utils import get_debate_history, format_data_context
from configuration.debate_constant import SPEAKER_JUDGE
from debate_state import DebateState
from typing import Dict, Any, Literal, Union, List
from pydantic import BaseModel, Field

class DebateVerdict(BaseModel):
    """
    Judgment of a trading debate based on analytical performance.

    Attributes:
        winner (Literal): Either 'buy' or 'sell', indicating which position was more convincing.
        justification (str): The reason for the judgment, focusing on data analysis, logical reasoning, and argument quality.
    """

    winner: Literal["buy", "sell"] = Field(
        description="Indicates the winner of the debate. Must be 'buy' or 'sell'."
    )
    justification: Union[str, List[str]] = Field(
        description="A concise explanation or list of points explaining why this position won. Focus on data analysis quality, logical reasoning, and argument strength."
    )

class JudgeNode(BaseComponent):
    def __init__(self, llm_config, temperature: float = 0.3):
        super().__init__(llm_config, temperature)
        self.chain = self.create_structured_output_chain(JUDGE_SYSTEM_PROMPT, JUDGE_HUMAN_PROMPT, DebateVerdict)

    def __call__(self, state: DebateState) -> Dict[str, Any]:
        super().__call__(state)

        debate_topic = state.get("debate_topic")
        messages = state.get("messages", [])
        debate_history = get_debate_history(messages)
        data_context = format_data_context(state)

        result = self.execute_chain({
            "debate_topic": debate_topic,
            "debate_history": debate_history,
            "data_context": data_context
        })

        justification = result.justification
        if isinstance(justification, list):
            justification = "\n".join(f"- {item}" for item in justification)

        return {
            "judge_verdict": result.model_dump() if hasattr(result, 'model_dump') else result.dict(),
            "messages": messages + [{
                "speaker": SPEAKER_JUDGE,
                "content": f"WINNER: {result.winner.upper()}\n\nREASON:\n{justification}",
                "stage": "verdict"
            }]
        }
