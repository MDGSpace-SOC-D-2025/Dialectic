import os
from typing import TypedDict
import praw
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, START, END


class State(TypedDict):
    company: str
    raw_data: str
    final_report: str

#Reddit Fetcher
def fetch_reddit_data(company: str):
    # Setup your PRAW client here
    reddit = praw.Reddit(
        client_id="<YOUR_CLIENT_ID>", 
        client_secret="<YOUR_SECRET>", 
        user_agent="finance_agent"
    )
    # Search across broad financial communities
    subs = reddit.subreddit("stocks+investing+wallstreetbets+pennystocks")
    posts = []
    # Fetch top 10 relevant posts from the past month
    for post in subs.search(company, limit=15, time_filter="month"):
        posts.append(f"Title: {post.title}\nText: {post.selftext[:400]}")
    
    return "\n---\n".join(posts) if posts else "No recent data found."

# Nodes
def researcher_node(state: State):
    """Gathers raw data from Reddit"""
    data = fetch_reddit_data(state["company"])
    return {"raw_data": data}

def analyst_node(state: State):
    """Turns raw data into a clean, professional paragraph"""
    llm = ChatOpenAI(
    
    model="mistralai/devstral-2512:free",
    temperature=0,
    api_key=os.environ.get("OPENROUTER_API_KEY"),
    base_url=os.environ.get("OPENAI_API_BASE"),
    max_completion_tokens=1000,
     )    
    prompt = (
        f"""You are a financial analyst. Based on the following Reddit discussions about {state['company']}, 
        write a 1-2 paragraph of 150 words each. Focus on common themes, investor concerns, and what the community 
        is excited about. Do not use bullet points or sentiment scores; provide a narrative summary.Based on the following DATA.\n\n"
        DATA:\n{state['raw_data']}"""
    )
    
    response = llm.invoke(prompt)
    return {"final_report": response.content}

#  Building the Graph 
builder = StateGraph(State)
builder.add_node("researcher", researcher_node)
builder.add_node("analyst", analyst_node)

builder.add_edge(START, "researcher")
builder.add_edge("researcher", "analyst")
builder.add_edge("analyst", END)

graph = builder.compile()

#  Run the graph
result = graph.invoke({"company": "NVIDIA"})
print("\n FINAL FINANCIAL REPORT \n")
print(result["final_report"])

