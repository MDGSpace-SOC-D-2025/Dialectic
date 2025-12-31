import operator
from typing import Annotated, TypedDict
from langgraph.graph import StateGraph, START, END
from langchain_openai import ChatOpenAI
import requests
import pandas as pd
import os
from dotenv import load_dotenv
load_dotenv()
ticker="" # Enter your ticker here
API_KEY=os.environ.get("ALPHA_VANTAGE_API_KEY")

# Helper function to convert API strings to numbers safely
def clean(val):
        try:
            return float(val) if val and val != "None" else 0.0
        except ValueError:
            return 0.0


url1 = f'https://www.alphavantage.co/query?function=INCOME_STATEMENT&symbol={ticker}&apikey={API_KEY}'
r1 = requests.get(url1)
data1 = r1.json()

if "quarterlyReports" in data1 and len(data1["quarterlyReports"]) > 0:
    # Get the most recent quarter
    q = data1["quarterlyReports"][0]

    # Extract raw values
    revenue = clean(q.get('totalRevenue'))
    currency = q.get('reportedCurrency')
    gross_profit = clean(q.get('grossProfit'))
    op_income = clean(q.get('operatingIncome'))
    net_income = clean(q.get('netIncome'))
    rnd = clean(q.get('researchAndDevelopment'))
    ebitda = clean(q.get('ebitda'))
    tax = clean(q.get('incomeTaxExpense'))

    # Build the dictionary with your specific variables
    # (Margins are calculated as: (Value / Revenue) * 100)
    formatted_data = {
        "Fiscal Date Ending": q.get('fiscalDateEnding'),
        "Currency": currency,
        "Gross Profit Margin": f"{(gross_profit / revenue * 100):.2f}%" if revenue else "N/A",
        "Operating Margin": f"{(op_income / revenue * 100):.2f}%" if revenue else "N/A",
        "Net Profit Margin": f"{(net_income / revenue * 100):.2f}%" if revenue else "N/A",
        "Research and Development": f"{rnd:,.0f}",
        "EBITDA": f"{ebitda:,.0f}",
        "Income Tax Expenses": f"{tax:,.0f}",
    }

    # Convert to DataFrame and Transpose for vertical format
    df_result = pd.DataFrame([formatted_data]).T
    df_result.columns = ['Recent Quarterly Data']
    
    # print(df_result)



url2 = f'https://www.alphavantage.co/query?function=BALANCE_SHEET&symbol={ticker}&apikey={API_KEY}'
r2 = requests.get(url2)
data2 = r2.json()
if "annualReports" in data2 and len(data2["annualReports"]) > 0:
    # Get the most recent annual report
    a = data2["annualReports"][0]

    # Extract and format key balance sheet items
    total_current_assets = clean(a.get('totalCurrentAssets'))
    currency = a.get('reportedCurrency')
    total_liabilities = clean(a.get('totalLiabilities'))
    total_shareholder_equity = clean(a.get('totalShareholderEquity'))
    current_liabilities = clean(a.get('totalCurrentLiabilities'))
    cash_and_equivalents = clean(a.get('cashAndCashEquivalentsAtCarryingValue'))
    goodwill = clean(a.get('goodwill'))
    total_assets=clean(a.get('totalAssets'))
    short_debt=clean(a.get('shortTermDebt'))
    long_debt=clean(a.get('longTermDebt'))
    retained_earnings=clean(a.get('retainedEarnings'))
    
    formatted_balance_sheet = {
        "Fiscal Date Ending": a.get('fiscalDateEnding'),
        "Currency": currency,
        "Total Current Assets": f"{total_current_assets:,.0f}",
        "Total Assets": f"{total_assets:,.0f}",
        "Total Liabilities": f"{total_liabilities:,.0f}",
        "Total Shareholder Equity": f"{total_shareholder_equity:,.0f}",
        "Current Liabilities": f"{current_liabilities:,.0f}",
        "Goodwill": f"{goodwill:,.0f}",
        "Total Debt": f"{(short_debt + long_debt):,.0f}",
        "Retained Earnings": f"{retained_earnings:,.0f}",   
        "current ratio": f"{(total_current_assets / current_liabilities):.2f}" if current_liabilities else "N/A",
        "debt to equity ratio": f"{((short_debt + long_debt) / total_shareholder_equity):.2f}" if total_shareholder_equity else "N/A",
         }
    # Convert to DataFrame and Transpose for vertical format
    df_balance_sheet = pd.DataFrame([formatted_balance_sheet]).T #balance sheet
    df_balance_sheet.columns = ['Most Recent Annual Data']
    
    
url3 = f'https://www.alphavantage.co/query?function=CASH_FLOW&symbol={ticker}&apikey={API_KEY}'
r3 = requests.get(url3)
data3 = r3.json()

if "quarterlyReports" in data3 and len(data3["quarterlyReports"]) > 0:
    # Get the most recent quarter
    q = data3["quarterlyReports"][0]

    net_income = clean(q.get('netIncome'))
    currency = q.get('reportedCurrency')
    operating_cashflow = clean(q.get('operatingCashflow'))
    capital_expenditures = clean(q.get('capitalExpenditures'))
    dividend_payout = clean(q.get('dividendPayout'))
    cash_from_financing=clean(q.get('cashflowFromFinancing'))

    formatted_cash_flow = {
        "Fiscal Date Ending": q.get('fiscalDateEnding'),
        "Net Income": f"{net_income:,.0f}",
        "Currency": currency,
        "Operating Cashflow": f"{operating_cashflow:,.0f}",
        "free cash flow": f"{(operating_cashflow - capital_expenditures):,.0f}",
        "Capital Expenditures": f"{capital_expenditures:,.0f}",
        "Dividend Sustainability": f"{(dividend_payout/(operating_cashflow - capital_expenditures))*100:.2f}",
        "cash From Financing": f"{cash_from_financing:,.0f}",
    }

    # Convert
    df_cash_flow = pd.DataFrame([formatted_cash_flow]).T
    df_cash_flow.columns = ['Recent Quarterly Data']

    # print(df_cash_flow)


url4 = f'https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={ticker}&apikey={API_KEY}'
r4 = requests.get(url4)
data4 = r4.json()

if "Global Quote" in data4:
    g = data4["Global Quote"]
    formatted_global_quote = {
        "Symbol": g.get('01. symbol'),
        "High": g.get('03. high'),
        "Low": g.get('04. low'),
        "Price": g.get('05. price'),
        "Volume": g.get('06. volume'),
        "Latest Trading Day": g.get('07. latest trading day'),
        "Previous Close": g.get('08. previous close'),
        "Change Percent": g.get('10. change percent'),
    }

    df_global_quote = pd.DataFrame([formatted_global_quote]).T
    df_global_quote.columns = ['Current Stock Data']

    # print(df_global_quote)

url5 = f'https://www.alphavantage.co/query?function=RSI&symbol={ticker}&interval=weekly&time_period=10&series_type=open&apikey={API_KEY}'
r5 = requests.get(url5)
data5 = r5.json()

# Access the technical analysis section
if "Technical Analysis: RSI" in data5:
    rsi_data = data5["Technical Analysis: RSI"]
    
    # Create a DataFrame
    df = pd.DataFrame.from_dict(rsi_data, orient='index')
    df.index = pd.to_datetime(df.index)
    
    #  Sort by date (newest first)
    df = df.sort_index(ascending=False)
    df_rsi_data = df.head(5)  # Get the most recent 5 entries
    
    
url6 = f'https://www.alphavantage.co/query?function=FEDERAL_FUNDS_RATE&interval=daily&apikey={API_KEY}'
federal_funds_data = requests.get(url6).json()["data"][0]
# print(federal_funds_data)    


class GraphState(TypedDict):
    ticker: str
    dataframes: dict  # Stores your original DFs (df_result, df_balance_sheet, etc.)
    summaries: Annotated[list, operator.add] 

# 2. Define your LLM
llm = ChatOpenAI(
    model="mistralai/devstral-2512:free",
    temperature=0,
    api_key=os.environ.get("OPENROUTER_API_KEY"),
    base_url=os.environ.get("OPENAI_API_BASE"),
    max_completion_tokens=2000,
)
    
# 3. Define the Nodes
def analyze_income(state: GraphState):
    df = state["dataframes"]["income"]
    res = llm.invoke(f"Context: {df}\nSummarize this income statement in detail 100 words for a person who wants to invest.")
    return {"summaries": [f"INCOME ANALYSIS: {res.content}"]}

def analyze_balance(state: GraphState):
    df = state["dataframes"]["balance"]
    res = llm.invoke(f"Context: {df}\nSummarize this balance sheet in detail 120 words for a person who wants to invest.")
    return {"summaries": [f"BALANCE SHEET ANALYSIS: {res.content}"]}

def analyze_cash(state: GraphState):
    df = state["dataframes"]["cash"]
    res = llm.invoke(f"Context: {df}\nSummarize this cash flow statement in paragraph of detail 100 words for a person who wants to invest.")
    return {"summaries": [f"CASH FLOW ANALYSIS: {res.content}"]}

def analyze_global_quote(state: GraphState):
    df = state["dataframes"]["global_quote"]
    res = llm.invoke(f"Context: {df}\nSummarize this global quote in paragraph of detail 30 words for a person who wants to invest.")
    return {"summaries": [f"GLOBAL QUOTE ANALYSIS: {res.content}"]}

def analyze_rsi(state: GraphState):
    df = state["dataframes"]["rsi"]
    res = llm.invoke(f"Context: {df}\nSummarize this RSI trend in paragraph of detail 20 words for a person who wants to invest.")
    return {"summaries": [f" {res.content}"]}
def analyze_fed_rate(state: GraphState):
    data = state["dataframes"]["fed_rate"]
    res = llm.invoke(f"Context: {data}\nSummarize this federal funds rate in paragraph of detail 20 words for a person who wants to invest.")
    return {"summaries": [f" {res.content}"]}
def aggregator(state: GraphState):
    """Combines all parallel results into one final report."""
    final_report = "\n\n".join(state["summaries"])
    return {"summaries": [final_report]}

# 4. Build the Parallel Graph
workflow = StateGraph(GraphState)

 # Add nodes
workflow.add_node("income_node", analyze_income)
workflow.add_node("balance_node", analyze_balance)
workflow.add_node("cash_node", analyze_cash)
workflow.add_node("global_quote_node", analyze_global_quote)
workflow.add_node("rsi_node", analyze_rsi)
workflow.add_node("fed_rate_node", analyze_fed_rate)
workflow.add_node("aggregator", aggregator)

# Define Parallel Edges
workflow.add_edge(START, "income_node")
workflow.add_edge(START, "balance_node")
workflow.add_edge(START, "cash_node")
workflow.add_edge(START, "global_quote_node")
workflow.add_edge(START, "rsi_node")
workflow.add_edge(START, "fed_rate_node")

# The aggregator will only run once ALL THREE parallel nodes finish
workflow.add_edge("income_node", "aggregator")
workflow.add_edge("balance_node", "aggregator")
workflow.add_edge("cash_node", "aggregator")
workflow.add_edge("global_quote_node", "aggregator")
workflow.add_edge("rsi_node", "aggregator")
workflow.add_edge("fed_rate_node", "aggregator")

workflow.add_edge("aggregator", END)

# 5. Execute
app = workflow.compile()
inputs = {
    "ticker": f"{ticker}",
    "dataframes": {
        "income": df_result, 
        "balance": df_balance_sheet, 
        "cash": df_cash_flow
        ,"global_quote":df_global_quote,
        "rsi":df_rsi_data,
        "fed_rate":federal_funds_data
    },
    "summaries": []
}
print("Processing financial analysis in parallel...")
results = app.invoke(inputs)
print("\nFINAL REPORT:\n")
for s in results["summaries"]:
    print(s)
