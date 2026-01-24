from typing import TypedDict, List, Dict, Literal


DebateStage = Literal["opening", "rebuttal", "counter", "final_argument"]

class DebateMessage(TypedDict):
    speaker: str  
    content: str 
    stage: DebateStage 

class DebateState(TypedDict):
    debate_topic: str
    positions: Dict[str, str]
    messages: List[DebateMessage]
    opening_statement_pro_agent: str
    stage: str  # "opening", "rebuttal", "counter", "final_argument"
    speaker: str  
    financial_data: str
    news_data: str
    network_analysis: str