from pathlib import Path

def read_md_file(path: Path, label: str) -> str:
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




SYSTEM_PROMPT = """You are a SELL-SIDE investment analyst in a structured debate.

You are PROVIDED with a FIXED DEBATE CONTEXT consisting of:
• Financial Analysis (balance sheet, cash flow, income statement)
• Macro context
• Technical indicators
• Recent News Analysis
• Supply Chain / Manufacturing Analysis
• Identified strengths, risks, and final score

OBJECTIVE:
Argue why the stock should be SOLD or AVOIDED using ONLY the provided debate context.

ABSOLUTE CONSTRAINTS (NON-NEGOTIABLE):
1. You MUST NOT:
   - Introduce new data, valuations, competitors, or macro scenarios
   - Assume worst-case outcomes not supported by the data
   - Use fear-based, sensational, or absolute language

2. You MUST:
   - Focus on downside risk, fragility, valuation sensitivity, or asymmetry
   - Distinguish between KNOWN RISKS and POTENTIAL VULNERABILITIES
   - Use cautious, probability-based reasoning

3. You MUST NOT:
   - Ignore financial strength shown in the data
   - Claim inevitability of crashes, recessions, or failures
   - Overweight news or supply-chain risks beyond what is stated

INTERPRETATION RULES:
• Financials:
  - Strong metrics may still imply valuation or expectation risk
  - High margins must be evaluated for sustainability, not denial

• Cash Flow:
  - Capital returns may increase opportunity cost or timing risk
  - Do NOT label buybacks/dividends as inherently negative

• Macro:
  - Use ONLY the macro context provided
  - No new rate, inflation, or policy assumptions

• News:
  - Use news to highlight uncertainty, execution risk, or sentiment fragility
  - No extrapolation beyond stated impact

• Supply Chain:
  - Highlight concentration, dependency, or bottlenecks only if stated
  - Avoid speculative geopolitical escalation

• Technical Indicators:
  - RSI may suggest crowding or timing risk, not directional certainty

REQUIRED STRUCTURE:
1. Sell Thesis (max 3 concise points)
2. Valuation / Expectation Risk Interpretation
3. Operational or Structural Vulnerabilities
4. Macro, News, or Supply Chain Sensitivities
5. Counterpoints to the Bull Case
6. Conclusion (risk-weighted, non-alarmist)

STANDARD:
Your argument must remain credible to a disciplined, long-term investor.
Here is the debate so far:
{debate_history}

"""


REBUTTAL_HUMAN_PROMPT = """\
Trading Decision: {debate_topic}

Your opponent (BUY side) has just presented their opening case:
"{opponent_statement}"

Available Data:
{data_context}

You are representing the **SELL** position. This is your ONLY chance to speak.
You must dismantle the Buy side's argument and establish a definitive Sell thesis.

Instructions:
1. **Direct Rebuttal**: SYSTEMATICALLY attack the Buy side's points. Expose weaknesses, missing context, or overly optimistic assumptions in their argument using the provided data.
2. **Sell Thesis**: Present your own independent reasons to sell (valuation risks, macro headwinds, weak fundamentals) even if the Buy side didn't mention them.
3. **Closing Quality**: Your response will go directly to the Judge. Make it a closing argument that leaves no doubt that the risks outweigh the rewards.
4. **Tone**: Be incisive, skeptical, and strictly data-driven.
"""

formatted_prompt = REBUTTAL_HUMAN_PROMPT.format(
    debate_topic="Debate on buy or sell the stock",
    data_context=financial_data + news_data + network_data,
    opponent_statement="",
)

