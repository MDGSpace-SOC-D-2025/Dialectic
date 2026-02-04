import sys
from pathlib import Path
_project_root = Path(__file__).parent.parent
if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))


from langgraph.types import Command
from typing import Literal
from debate_state import DebateState
from configuration.debate_constant import (
    STAGE_OPENING, STAGE_REBUTTAL, STAGE_COUNTER, STAGE_FINAL_ARGUMENT,
    SPEAKER_BUY, SPEAKER_SELL,
    NODE_BUY_DEBATER, NODE_SELL_DEBATER, NODE_JUDGE,NODE_DEBATE_MODERATOR
)

class DebateModeratorNode:
    def __call__(self, state: DebateState) -> Command[Literal["buy_debater_node", "sell_debater_node", "judge_node", "__end__"]]:
        stage = state["stage"]
        speaker = state["speaker"]

        if stage == STAGE_OPENING and speaker == SPEAKER_BUY:
            return Command(
                update={"stage": STAGE_REBUTTAL, "speaker": SPEAKER_SELL},
                goto=NODE_SELL_DEBATER
            )
        elif stage == STAGE_REBUTTAL and speaker == SPEAKER_SELL:
            return Command(
                update={},
                goto=NODE_JUDGE
            )

        raise ValueError(f"Unexpected stage/speaker combo: stage={stage}, speaker={speaker}")
