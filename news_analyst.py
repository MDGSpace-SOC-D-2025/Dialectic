import os
import operator
from typing import Annotated, List, TypedDict
from dotenv import load_dotenv
load_dotenv()
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import WebBaseLoader
from langgraph.graph import StateGraph, END, START
import yfinance as yf

os.environ['USER_AGENT'] = 'DD'

#user input
company_name=""


search = yf.Search(company_name, news_count=3)

for news_item in search.news:
    print(f"Title: {news_item['title']}")
    print(f"Link: {news_item['link']}\n")


link1, link2, link3 = [item['link'] for item in search.news]



# Initialize LLM and Embeddings
llm = ChatOpenAI(
    
    model="mistralai/devstral-2512:free",
    temperature=0,
    api_key=os.environ.get("OPENROUTER_API_KEY"),
    base_url=os.environ.get("OPENAI_API_BASE"),
    max_completion_tokens=1000,
)

embeddings = OpenAIEmbeddings(
    model="text-embedding-3-small", # Using a standard model for stability
    api_key=os.environ.get("OPENROUTER_API_KEY"),
    base_url=os.environ.get("OPENAI_API_BASE"),
)


class GraphState(TypedDict):
    
    summaries: Annotated[List[str], operator.add]
    final_report: str


# --- Node Functions ---

def process_link1(state: GraphState):
    loader = WebBaseLoader(
        web_path=[link1],
    )
    docs = loader.load()
    splits = RecursiveCharacterTextSplitter(chunk_size=1200, chunk_overlap=100).split_documents(docs)
    
    context_text = "".join([d.page_content for d in splits])
    
    res = llm.invoke(f"Context: {context_text}\n\nSummarize the news article in 100 words.")
    return {"summaries": [f"--- {company_name} news---\n{res.content}"]}

def process_link2(state: GraphState):
    loader = WebBaseLoader(
        web_path=[link2],
    )
    docs = loader.load()
    splits = RecursiveCharacterTextSplitter(chunk_size=1200, chunk_overlap=100).split_documents(docs)
    
    context_text = "".join([d.page_content for d in splits])
    
    res = llm.invoke(f"Context: {context_text}\n\nSummarize the news article in 100 words.")
    return {"summaries": [f"--- {company_name} news---\n{res.content}"]}
def process_link3(state: GraphState):
    loader = WebBaseLoader(
        web_path=[link3],
    )
    docs = loader.load()
    splits = RecursiveCharacterTextSplitter(chunk_size=1200, chunk_overlap=100).split_documents(docs)
    
    context_text = "".join([d.page_content for d in splits])
    
    res = llm.invoke(f"Context: {context_text}\n\nSummarize the news article in 100 words.")
    return {"summaries": [f"--- {company_name} news---\n{res.content}"]}

def final_aggregator(state: GraphState):
    # Combine the 3 summaries collected in state["summaries"]
    combined_context = "\n\n".join(state["summaries"])
    
    prompt = f"""
    You are a professional financial advisor. Based on the following news, 
    write a comprehensive 300-word investment summary for a person who wants 
    to buy or sell shares of {company_name}. 
    Focus on market position, growth drivers, and potential risks.
    In potential risks consider macroeconomic, geopolitical and manufacturing factors as well.
    
    News Data:
    {combined_context}
    """
    
    res = llm.invoke(prompt)
    return {"final_report": res.content}

# --- Build the Graph ---

workflow = StateGraph(GraphState)

# # 1. Register Nodes
workflow.add_node("link1", process_link1)
workflow.add_node("link2", process_link2)
workflow.add_node("link3", process_link3)
workflow.add_node("aggregator", final_aggregator)

# 2. Add Edges from START to multiple nodes (This enables Parallelism)
workflow.add_edge(START, "link1")
workflow.add_edge(START, "link2")
workflow.add_edge(START, "link3")

# 3. Connect all nodes to END
workflow.add_edge("link1", "aggregator")
workflow.add_edge("link2", "aggregator")
workflow.add_edge("link3", "aggregator")
workflow.add_edge("aggregator", END)
# 4. Compile
app = workflow.compile()




# --- Run ---
if __name__ == "__main__":
    print(f" Processing {company_name} news links in parallel...")
    results = app.invoke({"summaries": []})
    
    # Print ONLY the final report
    print("\n" + "="*60)
    print(f"{company_name.upper()} ANALYSIS")
    print("="*60)
    print(results["final_report"]) # Access the specific aggregator output
    print("="*60)
        
        
        
        