import os
import operator
from typing import Annotated, List, TypedDict
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import WebBaseLoader
from langgraph.graph import StateGraph, END, START
import yfinance as yf
import pandas as pd

load_dotenv()
os.environ['USER_AGENT'] = 'DD'

def run_news_analysis(ticker: str):
    print(f"Starting News Analysis for {ticker}...")

    search = yf.Search(ticker, news_count=3)
    
    if not search.news:
        print(f"No news found for {ticker}")
        return None


    links = [item['link'] for item in search.news]
    # Ensure we have at least 3 links or handle fewer
    link1 = links[0] if len(links) > 0 else None
    link2 = links[1] if len(links) > 1 else None
    link3 = links[2] if len(links) > 2 else None


    # Initialize LLM and Embeddings
    llm = ChatOpenAI(
        
        model="nvidia/nemotron-nano-12b-v2-vl:free",
        temperature=0,
        api_key=os.environ.get("OPENROUTER_API_KEY"),
        base_url=os.environ.get("OPENAI_API_BASE"),
        max_completion_tokens=1000,
    )


    class GraphState(TypedDict):
        
        summaries: Annotated[List[str], operator.add]
        final_report: str


    #  Node Functions 

    def process_link1(state: GraphState):
        if not link1: return {"summaries": []}
        loader = WebBaseLoader(
            web_path=[link1],
        )
        docs = loader.load()
        splits = RecursiveCharacterTextSplitter(chunk_size=1200, chunk_overlap=100).split_documents(docs)
        
        context_text = "".join([d.page_content for d in splits])
        
        res = llm.invoke(f"Context: {context_text}\n\nSummarize the news article in 100 words.")
        return {"summaries": [f"--- {ticker} news---\n{res.content}"]}

    def process_link2(state: GraphState):
        if not link2: return {"summaries": []}
        loader = WebBaseLoader(
            web_path=[link2],
        )
        docs = loader.load()
        splits = RecursiveCharacterTextSplitter(chunk_size=1200, chunk_overlap=100).split_documents(docs)
        
        context_text = "".join([d.page_content for d in splits])
        
        res = llm.invoke(f"Context: {context_text}\n\nSummarize the news article in 100 words.")
        return {"summaries": [f"--- {ticker} news---\n{res.content}"]}
    def process_link3(state: GraphState):
        if not link3: return {"summaries": []}
        loader = WebBaseLoader(
            web_path=[link3],
        )
        docs = loader.load()
        splits = RecursiveCharacterTextSplitter(chunk_size=1200, chunk_overlap=100).split_documents(docs)
        
        context_text = "".join([d.page_content for d in splits])
        
        res = llm.invoke(f"Context: {context_text}\n\nSummarize the news article in 100 words.")
        return {"summaries": [f"--- {ticker} news---\n{res.content}"]}

    def final_aggregator(state: GraphState):
        # Combine the 3 summaries collected in state["summaries"]
        combined_context = "\n\n".join(state["summaries"])
        
        prompt = f"""
        You are a professional financial advisor. Based on the following news, 
        write a comprehensive 400-word investment summary for a person who wants 
        to buy or sell shares of {ticker}. 
        Focus on market position, growth drivers, and potential risks.
        In potential risks consider macroeconomic, geopolitical and manufacturing factors as well.
        
        News Data:
        {combined_context}
        """
        
        res = llm.invoke(prompt)
        return {"final_report": res.content}

    def analyze_sentiment(state: GraphState):
        """Provides a final Buy/Sell score based on the aggregated report."""
        # We take the last summary which is the aggregated report from the aggregator node
        combined_context = state["final_report"]
        
        prompt = f"""
        Role: You are a Senior Equity Research Analyst specializing in Fundamental Analysis and Market Sentiment.
        Task: Provide a final investment sentiment for {ticker} by synthesizing the provided news report with fundamental principles.
    
        Rules for Analysis:
        1. SECTOR LENS: Identify the sector (Bank, Tech, Industrial, etc.).
           - If Tech news mentions "AI," "Infrastructure," or "R&D": Evaluate if the news suggests a sustainable competitive advantage (Moat).
           - If Bank news mentions "Rates," "Deposits," or "Regulations": Evaluate impact on Net Interest Margin or Capital Adequacy.
        
        2. NEWS-BASED FUNDAMENTALS: Extract any mentioned financial figures (margins, revenue growth, or guidance). 
           - If news mentions a margin higher than 11%, treat it as a strength compared to the S&P 500 average.
           - If financial data is absent, analyze the "Narrative Quality" (e.g., is the news about growth or cost-cutting?).
    
        3. SPECULATIVE VS. REALIZED: Distinguish between "announced plans" (speculative) and "quarterly results" (realized). Weighted realized data more heavily.
    
        4. GEOPOLITICAL & MACRO: Explicitly evaluate how the news mentions geopolitical risks (supply chains, trade wars) or manufacturing constraints.
    
        Provided News Report:
        {combined_context}
    
        Format your response exactly as follows:
        --- NEWS-DRIVEN INVESTMENT ANALYSIS ---
        - FINAL SCORE: [0=Strong Sell to 10=Strong Buy, based on news impact on fundamentals]
        - SECTOR IDENTIFIED: [Sector Name]
        - MARKET SENTIMENT: [Bullish/Bearish/Neutral based on the news tone]
        - KEY STRENGTHS (from news): [Bullet points]
        - KEY RISKS (macro/geopolitical/manufacturing): [Bullet points]
        - JUSTIFICATION: [2-3 sentences explaining how the recent news reinforces or weakens the company's long-term fundamental thesis.]
        """
        
        res = llm.invoke(prompt)
        return {"summaries": [f"\n--- FINAL RECOMMENDATION ---\n{res.content}"]}
    #  Build the Parallel Graph

    #  Build the Graph 

    workflow = StateGraph(GraphState)

    # Register Nodes
    if link1: workflow.add_node("link1", process_link1)
    if link2: workflow.add_node("link2", process_link2)
    if link3: workflow.add_node("link3", process_link3)
    workflow.add_node("aggregator", final_aggregator)
    workflow.add_node("sentiment_analysis", analyze_sentiment)

    # Add Edges from START to multiple nodes 
    if link1: workflow.add_edge(START, "link1")
    if link2: workflow.add_edge(START, "link2")
    if link3: workflow.add_edge(START, "link3")


    #  Connect all nodes to END
    if link1: workflow.add_edge("link1", "aggregator")
    if link2: workflow.add_edge("link2", "aggregator")
    if link3: workflow.add_edge("link3", "aggregator")

    # workflow.add_edge("aggregator", "sentiment_analysis")
    workflow.add_edge("aggregator", END)
    # Compile
    app = workflow.compile()



    results = app.invoke({"final_report": []})
       
    filename = "News_Analysis.md"

    final_report_content = results["final_report"] 
    # final_recommendation = results["summaries"][-1]

    markdown_content = f"""# News Analysis Report: {ticker}

{final_report_content}

"""
    # Write to the file
    with open(filename, "w", encoding="utf-8") as f:
        f.write(markdown_content)

    print(f"\nAnalysis successfully saved to {filename}")
    return filename

if __name__ == "__main__":
    run_news_analysis("NVDA")