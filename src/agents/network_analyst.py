import os
from typing import  TypedDict
from dotenv import load_dotenv
load_dotenv()
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

from langchain_chroma import Chroma
from langgraph.graph import StateGraph, END, START
from sec_api import QueryApi
import pandas as pd
import requests

os.environ['USER_AGENT'] = 'DD'

def run_network_analysis(ticker: str):
    print(f"Starting Network (SEC) Analysis for {ticker}...")
    
    api_key_sec = os.environ.get("MY_API_KEY")

    final_ticker = f"ticker:{ticker}" 

    def get_filing_url(query):
        query_api = QueryApi(api_key=api_key_sec)
        try:
            filings = query_api.get_filings(query)
            if filings['filings']:
                return filings['filings'][0]['linkToFilingDetails']
            else:
                return None
        except Exception as e:
            print(f"Error fetching filings: {e}")
            return None


    query = {
        "query": f"{final_ticker} AND formType:\"10-K\"",
        "from": "0",
        "size": "1",
        "sort": [{"filedAt": {"order": "desc"}}]
    }

    url_filing = get_filing_url(query)
    
    if not url_filing:
        print(f"Could not find 10-K filing for {ticker}")
        return None

    print(f"URL: {url_filing}")

    headers = {'User-Agent': "dt dhruv.talar@gmail.com"}
    response = requests.get(url_filing, headers=headers)

    # Initialize LLM and Embeddings
    llm = ChatOpenAI(
        model="mistralai/devstral-2512:free",
        temperature=0,
        api_key=os.environ.get("OPENROUTER_API_KEY"),
        base_url=os.environ.get("OPENAI_API_BASE"),
        max_completion_tokens=1000,
    )

    embeddings = OpenAIEmbeddings(
        model="text-embedding-3-small", 
        api_key=os.environ.get("OPENROUTER_API_KEY"),
        base_url=os.environ.get("OPENAI_API_BASE"),
    )

    class GraphState(TypedDict):
        technical_summary: str
        supply_chain_summary: str
        competitor_summary: str
        final_report: str


#   Node Functions 

    def analyze_technical(state: GraphState):
        """Analyzes Technical Risks & Product Segments"""
        # Load and split text specifically for this query (simulated retrieval)
        try:
           text_splitter = RecursiveCharacterTextSplitter(chunk_size=2000, chunk_overlap=200)
           splits = text_splitter.split_text(response.text)
           # Use a local persistence directory to avoid connection errors
           vectorstore = Chroma.from_texts(texts=splits, embedding=embeddings, collection_name="technical_summary", persist_directory="./chroma_db_tech")
           retriever = vectorstore.as_retriever(search_kwargs={"k": 2}) # Get top 2 chunks
           
           relevant_docs = retriever.invoke("What are the key products and technical risks?")
           context = "\n\n".join([doc.page_content for doc in relevant_docs])
           
           res = llm.invoke(f"Context: {context}\n\nSummarize the key product segments and technical risks in 150 words.")
           return {"technical_summary": res.content}
        except Exception as e:
            print(f"Error in technical analysis: {e}")
            return {"technical_summary": "Error analyzing technical risks."}

    def analyze_supply_chain(state: GraphState):
        """Analyzes Supply Chain & Dependency Risks"""
        try:
            text_splitter = RecursiveCharacterTextSplitter(chunk_size=2000, chunk_overlap=200)
            splits = text_splitter.split_text(response.text)
            vectorstore = Chroma.from_texts(texts=splits, embedding=embeddings, collection_name="supply_chain_summary", persist_directory="./chroma_db_supply")
            retriever = vectorstore.as_retriever(search_kwargs={"k": 2})
            
            relevant_docs = retriever.invoke("Who are the suppliers, customers, and what are the supply chain risks?")
            context = "\n\n".join([doc.page_content for doc in relevant_docs])
            
            res = llm.invoke(f"Context: {context}\n\nSummarize the major customers, suppliers, and supply chain dependencies in 150 words.")
            return {"supply_chain_summary": res.content}
        except Exception as e:
             print(f"Error in supply chain analysis: {e}")
             return {"supply_chain_summary": "Error analyzing supply chain."}

    def analyze_competition(state: GraphState):
        """Analyzes Competitors & Market Position"""
        try: 
            text_splitter = RecursiveCharacterTextSplitter(chunk_size=2000, chunk_overlap=200)
            splits = text_splitter.split_text(response.text)
            vectorstore = Chroma.from_texts(texts=splits, embedding=embeddings, collection_name="competitor_summary", persist_directory="./chroma_db_comp")
            retriever = vectorstore.as_retriever(search_kwargs={"k": 2})
            
            relevant_docs = retriever.invoke("Who are the competitors and what is the market position?")
            context = "\n\n".join([doc.page_content for doc in relevant_docs])
            
            res = llm.invoke(f"Context: {context}\n\nSummarize the key competitors and market risks in 150 words.")
            return {"competitor_summary": res.content}
        except Exception as e:
                print(f"Error in competitor analysis: {e}")
                return {"competitor_summary": "Error analyzing competition."}


    def final_aggregator(state: GraphState):
        """Synthesizes all summaries into a final report."""
        tech = state.get("technical_summary", "No data")
        supply = state.get("supply_chain_summary", "No data")
        comp = state.get("competitor_summary", "No data")
        
        prompt = f"""
        Role: Supply Chain & Network Analyst.
        Task: Synthesize the 10-K analysis for {ticker}.
    
        Segments:
        1. Product & Technical Risks:
        {tech}
    
        2. Supply Chain & Dependencies:
        {supply}
    
        3. Competition & Market:
        {comp}
        
        Output: A structured 400-word Strategic Network Risk Report.
        Format your response exactly as follows:
        --- NETWORK & RISK ANALYSIS ---
        - FINAL RISK COMPOSITE: [Low/Medium/High based on dependencies and competition]
        - MOAT STATUS: [Wide/Narrow/None]
        - KEY SUPPLIER RISKS: [Bullet points]
        - KEY CUSTOMER CONCENTRATION: [Bullet points]
        - COMPETITIVE THREATS: [Bullet points]
        - JUSTIFICATION: [Summary of the network stability]
        """
        
        res = llm.invoke(prompt)
        return {"final_report": res.content}


    #Build the Graph

    workflow = StateGraph(GraphState)

    workflow.add_node("technical", analyze_technical)
    workflow.add_node("supply_chain", analyze_supply_chain)
    workflow.add_node("competition", analyze_competition)
    workflow.add_node("aggregator", final_aggregator)

    workflow.add_edge(START, "technical")
    workflow.add_edge(START, "supply_chain")
    workflow.add_edge(START, "competition")

    workflow.add_edge("technical", "aggregator")
    workflow.add_edge("supply_chain", "aggregator")
    workflow.add_edge("competition", "aggregator")

    workflow.add_edge("aggregator", END)

    # Compile
    app = workflow.compile()


    inputs = {"technical_summary": "", "supply_chain_summary": "", "competitor_summary": ""}
    # if __name__ == "__main__":
    #     print(f"Analysing 10-K for {ticker}...")
    results = app.invoke(inputs)
        
        # print("\n" + "="*60)
        # print(f"NETWORK ANALYSIS REPORT: {ticker}")
        # print("="*60)
        # print(results["final_report"])

     # --- SAVING TO MARKDOWN FILE ---

    # Create a filename based on the ticker
    filename = "Network_Analysis.md"
    
    final_report_content = results["final_report"] 

    markdown_content = f"""# Network Analysis Report: {ticker}
**Date of Analysis:** {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}

## 1. Automated Component Summaries
{final_report_content}

"""

    # Write to the file
    with open(filename, "w", encoding="utf-8") as f:
        f.write(markdown_content)

    print(f"\n✅ Analysis successfully saved to {filename}")
    return filename

if __name__ == "__main__":
    run_network_analysis("NVDA")