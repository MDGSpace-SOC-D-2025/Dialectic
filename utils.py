from debate_state import DebateMessage, DebateState, DebateStage
from typing import List

def create_debate_message(speaker: str, content: str, stage: DebateStage) -> DebateMessage:
    return DebateMessage(
        speaker=speaker,
        content=content,
        stage=stage
    )

def get_debate_history(messages: List[DebateMessage]) -> str:
    return "\n".join(
        f"[{msg['stage'].upper()}] {msg['speaker'].upper()}: {msg['content']}"
        for msg in messages
    )

def format_data_context(state: DebateState) -> str:
    """Format all available data into a context string for prompts."""
    parts = []
    
    if state.get("financial_data"):
        parts.append(f"Financial Data:\n{state['financial_data']}\n")
    
    if state.get("news_data"):
        parts.append(f"News Data:\n{state['news_data']}\n")
    
    if state.get("network_analysis"):
        parts.append(f"Network Analysis:\n{state['network_analysis']}\n")
    
    if state.get("supply_chain_data"):
        parts.append(f"Supply Chain Data:\n{state['supply_chain_data']}\n")
    
    if not parts:
        return "No additional data provided."
    
    return "\n".join(parts)


