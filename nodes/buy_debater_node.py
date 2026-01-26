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
    COUNTER_HUMAN_PROMPT,
)
from utils import create_debate_message, get_debate_history, format_data_context
from configuration.debate_constant import (
    STAGE_OPENING,
    STAGE_COUNTER,
    SPEAKER_BUY,
    SPEAKER_SELL
)

class BuyNode(BaseComponent):
    def __init__(self, llm_config, temperature: float = 0.7):
        super().__init__(llm_config, temperature)
        self.opening_chain = self.create_chain(SYSTEM_PROMPT, OPENING_HUMAN_PROMPT) #Used at the start. Focuses on presenting a fresh thesis based on data.
        self.counter_chain = self.create_chain(SYSTEM_PROMPT, COUNTER_HUMAN_PROMPT) #Used later. Focuses on listening to the "Sell" agent and attacking their specific points.

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
        elif stage == STAGE_COUNTER and speaker == SPEAKER_BUY:
            opponent_msg = self._get_last_message_by(SPEAKER_SELL, messages)
            debate_history = get_debate_history(messages)
            result = self.counter_chain.invoke({
                "debate_topic": debate_topic,
                "opponent_statement": opponent_msg,
                "debate_history": debate_history,
                "data_context": data_context
            })
        else:
            raise ValueError(f"Unknown turn for BuyNode: stage={stage}, speaker={speaker}")
        
        new_message = create_debate_message(speaker=SPEAKER_BUY, content=result, stage=stage)
        #Uses the parent's log_debate_event to print the argument in [green]BUY[/] color in your terminal.
        self.log_debate_event(
            f"[bold]{stage.upper()}[/]\n"
            f"{result}\n",
            prefix="BUY"
        )

        return {
            "messages": messages + [new_message]
        }

    def _get_last_message_by(self, speaker_prefix, messages): #It scans the chat history backwards (reversed) to find the most recent thing the opponent (SELL) said
        for m in reversed(messages):
            if m.get("speaker") == speaker_prefix:
                return m["content"]
        return ""

