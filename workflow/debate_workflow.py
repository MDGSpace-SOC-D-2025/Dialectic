import sys
from pathlib import Path
_project_root = Path(__file__).parent.parent
if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))

from langgraph.graph import StateGraph, END
from debate_state import DebateState
from nodes.buy_debater_node import BuyNode
from nodes.sell_debater_node import SellNode
from nodes.debate_moderator_node import DebateModeratorNode
from nodes.judge_node import JudgeNode
from configuration.llm_config import llm_config_map
from configuration.debate_constant import (
    STAGE_OPENING, SPEAKER_BUY,
    NODE_BUY_DEBATER, NODE_SELL_DEBATER, NODE_DEBATE_MODERATOR, NODE_JUDGE
)

class DebateWorkflow:

    def _initialize_workflow(self) -> StateGraph:
        workflow = StateGraph(DebateState)
        # Nodes
        workflow.add_node(NODE_BUY_DEBATER, BuyNode(llm_config_map["gpt-4o"]))
        workflow.add_node(NODE_SELL_DEBATER, SellNode(llm_config_map["gpt-4o"]))
        workflow.add_node(NODE_DEBATE_MODERATOR, DebateModeratorNode())
        workflow.add_node(NODE_JUDGE, JudgeNode(llm_config_map["gpt-4o"]))

        # Entry point - start with buy node
        workflow.set_entry_point(NODE_BUY_DEBATER)

        # Flow - buy and sell nodes go to moderator
        workflow.add_edge(NODE_BUY_DEBATER, NODE_DEBATE_MODERATOR)
        workflow.add_edge(NODE_SELL_DEBATER, NODE_DEBATE_MODERATOR)
        workflow.add_edge(NODE_JUDGE, END)
        return workflow

    async def run(self, initial_state: dict):
        workflow = self._initialize_workflow()
        graph = workflow.compile()
        
        # Ensure initial state has required fields
        if "stage" not in initial_state:
            initial_state["stage"] = STAGE_OPENING
        if "speaker" not in initial_state:
            initial_state["speaker"] = SPEAKER_BUY
        if "messages" not in initial_state:
            initial_state["messages"] = []
        if "positions" not in initial_state:
            initial_state["positions"] = {
                "buy": "In favor of buying",
                "sell": "In favor of selling"
            }
        
        final_state = await graph.ainvoke(initial_state, config={"recursion_limit": 50})
        return final_state
