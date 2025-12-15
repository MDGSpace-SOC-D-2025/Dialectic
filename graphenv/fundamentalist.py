from dotenv import load_dotenv
import os
from langgraph.graph import StateGraph, END
from typing import TypedDict, Annotated, Sequence
from langchain_core.messages import BaseMessage, SystemMessage, HumanMessage, ToolMessage
from operator import add as add_messages
from langchain_openai import ChatOpenAI
from langchain_openai import OpenAIEmbeddings
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter 
from langchain_chroma import Chroma                                 
from langchain_core.tools import tool
import requests
from bs4 import BeautifulSoup
from datetime import datetime

load_dotenv()

llm = ChatOpenAI(
    model="openai/gpt-5.2-chat",
    temperature=0,
    api_key=os.environ.get("OPENROUTER_API_KEY"),
    base_url=os.environ.get("OPENAI_API_BASE"),
    max_tokens=300
)

embeddings = OpenAIEmbeddings(
    model="openai/text-embedding-3-small",
    api_key=os.environ.get("OPENROUTER_API_KEY"),
    base_url=os.environ.get("OPENAI_API_BASE"),
)

pdf_path = "Stock_Market_Performance_2024.pdf"

# Safety measure for debugging
if not os.path.exists(pdf_path):
    raise FileNotFoundError(f"PDF file not found: {pdf_path}")

pdf_loader = PyPDFLoader(pdf_path)

try:
    pages = pdf_loader.load()
    print(f"PDF has been loaded and has {len(pages)} pages")
except Exception as e:
    print(f"Error loading PDF: {e}")
    raise

# Chunking Process
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=200
)

pages_split = text_splitter.split_documents(pages)

persist_directory = r"C:\Aryan\LangGraph_Book\LangGraphCourse\Agents"
collection_name = "stock_market"

if not os.path.exists(persist_directory):
    os.makedirs(persist_directory)

try:
    vectorstore = Chroma.from_documents(
        documents=pages_split,
        embedding=embeddings,
        persist_directory=persist_directory,
        collection_name=collection_name
    )
    print(f"Created ChromaDB vector store!")
except Exception as e:
    print(f"Error setting up ChromaDB: {str(e)}")
    raise

retriever = vectorstore.as_retriever(
    search_type="similarity",
    search_kwargs={"k": 5}
)

# Original retriever tool for PDF
@tool
def retriever_tool(query: str) -> str:
    """
    This tool searches and returns the information from the Stock Market Performance 2024 document.
    Use this for historical data and analysis from the PDF.
    """
    docs = retriever.invoke(query)

    if not docs:
        return "I found no relevant information in the Stock Market Performance 2024 document."
    
    results = []
    for i, doc in enumerate(docs):
        results.append(f"Document {i+1}:\n{doc.page_content}")
    
    return "\n\n".join(results)

# NEW: Web scraping tool for real-time NSE data
@tool
def fetch_nse_data(url: str) -> str:
    """
    Fetches real-time data from NSE India website or any stock market URL.
    Provide the full URL of the page you want to scrape.
    Example: https://www.nseindia.com/market-data/live-equity-market
    """
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
        }
        
        # Create session for NSE (they require cookies)
        session = requests.Session()
        session.headers.update(headers)
        
        # First request to get cookies
        session.get('https://www.nseindia.com', timeout=10)
        
        # Now fetch the actual URL
        response = session.get(url, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Extract text content
        text_content = soup.get_text(separator='\n', strip=True)
        
        # Limit content size
        if len(text_content) > 5000:
            text_content = text_content[:5000] + "...(content truncated)"
        
        return f"Data fetched from {url} at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}:\n\n{text_content}"
    
    except requests.RequestException as e:
        return f"Error fetching data from {url}: {str(e)}. Please check the URL and try again."
    except Exception as e:
        return f"Unexpected error: {str(e)}"

# NEW: API-based tool for NSE data (alternative approach)
@tool
def fetch_nse_api_data(symbol: str) -> str:
    """
    Fetches real-time stock data from NSE India API for a specific stock symbol.
    Example symbols: RELIANCE, TCS, INFY, HDFCBANK
    """
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'application/json',
            'Accept-Language': 'en-US,en;q=0.5',
        }
        
        session = requests.Session()
        session.headers.update(headers)
        
        # Get cookies
        session.get('https://www.nseindia.com', timeout=10)
        
        # Fetch stock quote
        api_url = f'https://www.nseindia.com/api/quote-equity?symbol={symbol.upper()}'
        response = session.get(api_url, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        
        # Format the response
        if 'priceInfo' in data:
            price_info = data['priceInfo']
            result = f"""
Real-time data for {symbol} (as of {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}):
- Last Price: ₹{price_info.get('lastPrice', 'N/A')}
- Change: ₹{price_info.get('change', 'N/A')} ({price_info.get('pChange', 'N/A')}%)
- Open: ₹{price_info.get('open', 'N/A')}
- High: ₹{price_info.get('intraDayHighLow', {}).get('max', 'N/A')}
- Low: ₹{price_info.get('intraDayHighLow', {}).get('min', 'N/A')}
- Previous Close: ₹{price_info.get('previousClose', 'N/A')}
- Volume: {data.get('securityWiseDP', {}).get('quantityTraded', 'N/A')}
"""
            return result
        else:
            return f"Could not fetch data for {symbol}. Please check the symbol name."
    
    except Exception as e:
        return f"Error fetching NSE API data for {symbol}: {str(e)}"

# Update tools list
tools = [retriever_tool, fetch_nse_data, fetch_nse_api_data]

llm = llm.bind_tools(tools)

class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], add_messages]

def should_continue(state: AgentState):
    """Check if the last message contains tool calls."""
    result = state['messages'][-1]
    return hasattr(result, 'tool_calls') and len(result.tool_calls) > 0

system_prompt = """
You are an intelligent AI assistant who answers questions about Stock Market Performance.

You have access to THREE tools:
1. retriever_tool - For historical data from the Stock Market Performance 2024 PDF document
2. fetch_nse_data - For scraping real-time data from NSE India web pages (provide full URL)
3. fetch_nse_api_data - For fetching real-time stock quotes from NSE API (provide stock symbol)

Use the appropriate tool based on the user's question:
- For historical analysis or PDF-based queries: use retriever_tool
- For current market data from a specific NSE webpage: use fetch_nse_data
- For real-time stock quotes: use fetch_nse_api_data

You can make multiple tool calls if needed. Always cite your sources and specify if data is real-time or historical.
"""

tools_dict = {our_tool.name: our_tool for our_tool in tools}

def call_llm(state: AgentState) -> AgentState:
    """Function to call the LLM with the current state."""
    messages = list(state['messages'])
    messages = [SystemMessage(content=system_prompt)] + messages
    message = llm.invoke(messages)
    return {'messages': [message]}

def take_action(state: AgentState) -> AgentState:
    """Execute tool calls from the LLM's response."""
    tool_calls = state['messages'][-1].tool_calls
    results = []
    
    for t in tool_calls:
        print(f"Calling Tool: {t['name']} with args: {t['args']}")
        
        if t['name'] not in tools_dict:
            print(f"\nTool: {t['name']} does not exist.")
            result = "Incorrect Tool Name. Available tools: retriever_tool, fetch_nse_data, fetch_nse_api_data"
        else:
            # Handle different argument structures
            if t['name'] == 'retriever_tool':
                result = tools_dict[t['name']].invoke(t['args'].get('query', ''))
            elif t['name'] == 'fetch_nse_data':
                result = tools_dict[t['name']].invoke(t['args'].get('url', ''))
            elif t['name'] == 'fetch_nse_api_data':
                result = tools_dict[t['name']].invoke(t['args'].get('symbol', ''))
            
            print(f"Result length: {len(str(result))}")
        
        results.append(ToolMessage(tool_call_id=t['id'], name=t['name'], content=str(result)))

    print("Tools Execution Complete. Back to the model!")
    return {'messages': results}

graph = StateGraph(AgentState)
graph.add_node("llm", call_llm)
graph.add_node("action_agent", take_action)

graph.add_conditional_edges(
    "llm",
    should_continue,
    {True: "action_agent", False: END}
)
graph.add_edge("action_agent", "llm")
graph.set_entry_point("llm")

rag_agent = graph.compile()

def running_agent():
    print("\n=== HYBRID RAG AGENT (PDF + Real-time Web Data) ===")
    print("Example queries:")
    print("- What is the current price of RELIANCE?")
    print("- Fetch data from https://www.nseindia.com/market-data/live-equity-market")
    print("- Compare historical performance from PDF with current TCS stock price")
    
    while True:
        user_input = input("\nWhat is your question: ")
        if user_input.lower() in ['exit', 'quit']:
            break
            
        messages = [HumanMessage(content=user_input)]
        result = rag_agent.invoke({"messages": messages})
        
        print("\n=== ANSWER ===")
        print(result['messages'][-1].content)

if __name__ == "__main__":
    running_agent()