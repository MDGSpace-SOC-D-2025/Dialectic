import sys
from pathlib import Path
_project_root = Path(__file__).parent.parent
if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))

from nodes.base_component import BaseComponent
from debate_state import DebateState
from typing import Dict, Any
from configuration.debate_constant import (
    STAGE_REBUTTAL,
    SPEAKER_SELL, SPEAKER_BUY
)
from prompts.sell_debater_prompt import (
    SYSTEM_PROMPT,
    REBUTTAL_HUMAN_PROMPT,
)
from utils import create_debate_message, get_debate_history, format_data_context
  
class SellNode(BaseComponent):
    def __init__(self, llm_config, temperature: float = 0.7):
        super().__init__(llm_config, temperature)
        self.rebuttal_chain = self.create_chain(SYSTEM_PROMPT, REBUTTAL_HUMAN_PROMPT)

    def __call__(self, state: DebateState) -> Dict[str, Any]:
        super().__call__(state)
        debate_topic = state["debate_topic"]
        messages = state.get("messages", [])
        stage = state["stage"]
        speaker = state["speaker"]
        
        # Format data context from state
        data_context = format_data_context(state)

        if stage == STAGE_REBUTTAL and speaker == SPEAKER_SELL:
            opponent_msg = self._get_last_message_by(SPEAKER_BUY, messages)
            debate_history = get_debate_history(messages)
            result = self.rebuttal_chain.invoke({
                "debate_topic": debate_topic,
                "opponent_statement": opponent_msg,
                "debate_history": debate_history,
                "data_context": data_context 
            })

        else:
            raise ValueError(f"Unknown turn for SellNode: stage={stage}, speaker={speaker}")

        new_message = create_debate_message(speaker=SPEAKER_SELL, content=result, stage=stage)
        return {
            "messages": messages + [new_message]
        }

    def _get_last_message_by(self, speaker: str, messages: list) -> str:
        for m in reversed(messages):
            if m["speaker"] == speaker:
                return m["content"]
        return ""

