import sys
from pathlib import Path
_project_root = Path(__file__).parent.parent
if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))

from nodes.base_component import BaseComponent
from debate_state import DebateState
from typing import Dict, Any
from prompts.buy_debater_prompt import (
    SYSTEM_PROMPT,
    OPENING_HUMAN_PROMPT,
)
from utils import create_debate_message, format_data_context
from configuration.debate_constant import (
    STAGE_OPENING,
    SPEAKER_BUY,
)

class BuyNode(BaseComponent):
    def __init__(self, llm_config, temperature: float = 0.7):
        super().__init__(llm_config, temperature)
        self.opening_chain = self.create_chain(SYSTEM_PROMPT, OPENING_HUMAN_PROMPT) 

    def __call__(self, state: DebateState) -> Dict[str, Any]:
        super().__call__(state) #way of executing the logic of a parent class while passing a specific "state" (data) through it.

        # Accesing all the data from the state dictionary in DebateState
        debate_topic = state.get("debate_topic")
        messages = state.get("messages", [])
        stage = state.get("stage")
        speaker = state.get("speaker")
        
        # Format data context from state
        data_context = format_data_context(state)

        if stage == STAGE_OPENING and speaker == SPEAKER_BUY:
            result = self.opening_chain.invoke({
                "debate_topic": debate_topic,
                "data_context": data_context
            })
        else:
            raise ValueError(f"Unknown turn for BuyNode: stage={stage}, speaker={speaker}")
        
        new_message = create_debate_message(speaker=SPEAKER_BUY, content=result, stage=stage)

        return {
            "messages": messages + [new_message]
        }


