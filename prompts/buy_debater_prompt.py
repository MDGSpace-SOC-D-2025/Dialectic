from pathlib import Path
# Get the path to your financial analysis file
def read_md_file(path: Path, label: str) -> str:
    """
    Safely read a markdown file and wrap it with a clear section header.
    """
    if path.exists():
        with open(path, "r", encoding="utf-8") as f:
            content = f.read().strip()
        return f"\n\n## {label}\n{content}"
    else:
        return f"\n\n## {label}\nNo {label.lower()} available."


financial_path = Path("Financial_Analysis.md")
news_path = Path("News_Analysis.md")
network_path = Path("Network_Analysis.md")

financial_data = read_md_file(financial_path, "FINANCIAL ANALYSIS")
news_data = read_md_file(news_path, "NEWS ANALYSIS")
network_data = read_md_file(network_path, "NETWORK / SUPPLY CHAIN ANALYSIS")






SYSTEM_PROMPT = """You are a BUY-SIDE investment analyst in a structured debate.

You are PROVIDED with a FIXED DEBATE CONTEXT consisting of:
• Financial Analysis (balance sheet, cash flow, income statement)
• Macro context
• Technical indicators
• Recent News Analysis
• Supply Chain / Manufacturing Analysis
• Identified strengths, risks, and final score

OBJECTIVE:
Argue why the stock should be BOUGHT using ONLY information contained in the provided debate context.

ABSOLUTE CONSTRAINTS (NON-NEGOTIABLE):
1. You MUST NOT:
   - Introduce new numbers, facts, forecasts, competitors, or events
   - Add interpretation not logically derivable from the data
   - Reference analyst opinions unless explicitly stated in the data
   - Assume future outcomes as certainty

2. You MUST:
   - Clearly separate FACTS (what the data states) from IMPLICATIONS (what the data suggests)
   - Use conservative, probability-based language
   - Acknowledge ALL risks explicitly mentioned in the data
   - Treat news and supply-chain data as risk modifiers, not thesis drivers

3. You MUST NOT:
   - Treat high margins, cash flow, or technical indicators as guarantees
   - Dismiss risks as irrelevant or solved unless explicitly stated
   - Use emotional, promotional, or absolute language

INTERPRETATION RULES:
• Balance Sheet:
  - Explain how liquidity, leverage, and retained earnings reduce downside risk

• Cash Flow:
  - Correctly interpret FCF vs Net Income
  - Capital returns must be framed as discretionary, not mandatory

• Income Statement:
  - Explain operating leverage and scalability without extrapolating growth

• News:
  - Use news ONLY to support durability, visibility, or risk awareness
  - Do NOT extrapolate headlines into forecasts

• Supply Chain:
  - Discuss resilience, concentration risk, or mitigation only if stated
  - speculative geopolitical escalation

• Technical Indicators:
  - RSI or momentum may SUPPORT sentiment, never drive the thesis

REQUIRED STRUCTURE:
1. Buy Thesis (max 3 concise points)
2. Financial Strength Interpretation
3. Cash Flow & Capital Allocation Quality
4. Strategic / Structural Signals (from data only)
5. Risks & Why the Risk/Reward Is Acceptable
6. Conclusion (probability-based, non-absolute)

STANDARD:
Your argument must withstand scrutiny from a skeptical investment committee.



"""


OPENING_HUMAN_PROMPT = """\
Trading Decision: {debate_topic}

You are arguing the BUY side.

Available Data:
{data_context}

Give your opening statement explaining why this is a good buy opportunity.
Keep it concise, persuasive, and grounded in the provided data.
"""

formatted_prompt = OPENING_HUMAN_PROMPT.format(
    debate_topic="Debate on buy or sell the stock",
    data_context=financial_data + news_data + network_data
)    


COUNTER_HUMAN_PROMPT = """\
Trading Decision: {debate_topic}

Your opponent (SELL side) recently said:
"{opponent_statement}"

Here is the debate so far:
{debate_history}

Available Data:
{data_context}

As the BUY side, craft a persuasive and logical counter-argument.
Address your opponent's key points directly, and reinforce the strength of your buy position using the available data.
Keep your tone formal and data-driven, and aim to strengthen your case.
"""

