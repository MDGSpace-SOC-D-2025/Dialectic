import os
import operator
from typing import Annotated, List, TypedDict

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_community.document_loaders import WebBaseLoader
import bs4
# Note: You need START and END from langgraph.graph
from langgraph.graph import StateGraph, END, START

load_dotenv()

# --- Configuration ---
os.environ['USER_AGENT'] = 'DD'

# Initialize LLM and Embeddings
llm = ChatOpenAI(
    model="mistralai/devstral-2512:free",
    temperature=0,
    api_key=os.environ.get("OPENROUTER_API_KEY"),
    base_url=os.environ.get("OPENAI_API_BASE"),
    max_completion_tokens=500,
)

embeddings = OpenAIEmbeddings(
    model="text-embedding-3-small", # Using a standard model for stability
    api_key=os.environ.get("OPENROUTER_API_KEY"),
    base_url=os.environ.get("OPENAI_API_BASE"),
)

company_name="meesho"
company_id="ML13"
# --- LangGraph State ---
class GraphState(TypedDict):
    
    # It tells LangGraph to APPEND to the list rather than REPLACING it.
    summaries: Annotated[List[str], operator.add]


# --- Node Functions ---

def process_tata_steel(state: GraphState):
    loader = WebBaseLoader(
        web_path=f"https://www.moneycontrol.com/markets/financials/quarterly-results/{company_name}-{company_id}/#results",
        bs_kwargs={"parse_only": bs4.SoupStrainer(class_=("web_mc_container__cNDvS"))},
    )
    docs = loader.load()
    splits = RecursiveCharacterTextSplitter(chunk_size=1200, chunk_overlap=100).split_documents(docs)
    vectorstore = Chroma.from_documents(documents=splits, embedding=embeddings)
    
    context = vectorstore.similarity_search("Company Name Price MCap", k=3)
    context_text = "".join([d.page_content for d in context])
    
    res = llm.invoke(f"Context: {context_text}\n\nSummarize peer comparison with respect to {company_name} in 100 words.")
    return {"summaries": [f"--- {company_name} PEERS ---\n{res.content}"]}

def process_meesho_cashflow(state: GraphState):
    loader = WebBaseLoader(
        web_path=f"https://www.moneycontrol.com/financials/{company_name}/cash-flowVI/{company_id}#{company_id}",
        bs_kwargs={"parse_only": bs4.SoupStrainer(class_=("mctable1"))},
    )
    docs = loader.load()
    splits = RecursiveCharacterTextSplitter(chunk_size=1200, chunk_overlap=100).split_documents(docs)
    vectorstore = Chroma.from_documents(documents=splits, embedding=embeddings)
    
    context = vectorstore.similarity_search("CASH FLOW OF MEESHO", k=3)
    context_text = "".join([d.page_content for d in context])
    
    res = llm.invoke(f"Context: {context_text}\n\nSummarize cash flow with respect to an investor or trader in 100 words.")
    return {"summaries": [f"--- {company_name} CASH FLOW ---\n{res.content}"]}




def process_meesho_pl(state: GraphState):
    loader = WebBaseLoader(
        web_path=f"https://www.moneycontrol.com/financials/{company_name}/profit-lossVI/{company_id}#{company_id}",
        bs_kwargs={"parse_only": bs4.SoupStrainer(class_=("mctable1"))},
    )
    docs = loader.load()
    splits = RecursiveCharacterTextSplitter(chunk_size=1200, chunk_overlap=100).split_documents(docs)
    vectorstore = Chroma.from_documents(documents=splits, embedding=embeddings)
    
    context = vectorstore.similarity_search(f"PROFIT AND LOSS ACCOUNT OF {company_name}", k=3)
    context_text = "".join([d.page_content for d in context])
    
    res = llm.invoke(f"Context: {context_text}\n\nSummarize P&L with respect to an investor who wants to invest in 50 words.")
    return {"summaries": [f"--- {company_name} P&L ---\n{res.content}"]}

def process_tata_stocks(state:GraphState):
    loader = WebBaseLoader(
        web_path=f"https://www.moneycontrol.com/financials/{company_name}/balance-sheetVI/{company_id}#{company_id}",
        bs_kwargs={"parse_only": bs4.SoupStrainer(class_=("tab-content"))},
    )
    docs = loader.load()
    splits = RecursiveCharacterTextSplitter(chunk_size=1200, chunk_overlap=100).split_documents(docs)
    vectorstore = Chroma.from_documents(documents=splits, embedding=embeddings)
    
    context = vectorstore.similarity_search("Cash BalanceFinancial RunwayHigh / IncreasingTrade PayablesPower over suppliersHigh (Relative to Receivables)Total DebtFinancial RiskLow / ZeroCurrent AssetsShort-term Strength$> 1.5 \times$ LiabilitiesEquity CapitalSkin in the gameStable or Increasing", k=3)
    context_text = "".join([d.page_content for d in context])
    
    res = llm.invoke(f"Context: {context_text}\n\nSummarize the given data with respect to an investor in 100 words.")
    return {"summaries": [f"Stock data \n{res.content}"]}



# --- Build the Graph ---

workflow = StateGraph(GraphState)

# # 1. Register Nodes
workflow.add_node("tata_node", process_tata_steel)
workflow.add_node("meesho_cf_node", process_meesho_cashflow)
workflow.add_node("meesho_pl_node", process_meesho_pl)
workflow.add_node("tata_stocks",process_tata_stocks)
# 2. Add Edges from START to multiple nodes (This enables Parallelism)
workflow.add_edge(START, "tata_node")
workflow.add_edge(START, "meesho_cf_node")
workflow.add_edge(START, "meesho_pl_node")
workflow.add_edge(START,"tata_stocks")
# 3. Connect all nodes to END
workflow.add_edge("tata_node", END)
workflow.add_edge("meesho_cf_node", END)
workflow.add_edge("meesho_pl_node", END)
workflow.add_edge("tata_stocks",END)
# 4. Compile
app = workflow.compile()




# --- Run ---
if __name__ == "__main__":
    print("🚀 Running parallel nodes...")
    results = app.invoke({"summaries": []})
    
    for s in results["summaries"]:
        print(s)
        print("\n")
        
        
        
        