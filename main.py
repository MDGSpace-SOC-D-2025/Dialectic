import asyncio
import os
import sys
from pathlib import Path
from dotenv import load_dotenv
load_dotenv()
# Add project root to Python path
project_root = Path(__file__).parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from workflow.debate_workflow import DebateWorkflow

from src.agents.updated_fundamentalist import run_fundamental_analysis
from src.agents.news_analyst import run_news_analysis
from src.agents.network_analyst import run_network_analysis



def validate_env():
    required_var = "OPENROUTER_API_KEY"
    if not os.environ.get(required_var):
        raise EnvironmentError(f"Missing environment variable: {required_var}")
async def run_agents_parallel(ticker: str):
    """Runs the three data gathering agents in parallel."""
    print(f"\n Starting Parallel Data Gathering for {ticker}...\n")
    
    # Run synchronous functions in parallel threads
    loop = asyncio.get_running_loop()
    
    
    tasks = [
        loop.run_in_executor(None, run_fundamental_analysis, ticker),
        loop.run_in_executor(None, run_news_analysis, ticker),
        loop.run_in_executor(None, run_network_analysis, ticker)
    ]
    
   
    await asyncio.gather(*tasks)
    print(f"\n Data Gathering Complete for {ticker}!\n")

async def main():
    
    validate_env()
    
    user_ticker = None
    
    if not user_ticker:
        try:
            
            print("\n No ticker argument provided.")
            user_input = input("Enter a ticker symbol to analyze : ").strip().upper()
            if user_input:
                user_ticker = user_input
        except EOFError:
            pass

   
    if user_ticker:
        await run_agents_parallel(user_ticker)
    else:
        print("No ticker provided. Please provide a ticker to run analysis.")
        return
    
    
    debate_topic = f"Should we buy shares of {user_ticker}?"
    
    print(f" Debate Topic: {debate_topic}")

    #  Load Data from Markdown Files
    financial_data = ""
    news_data = ""
    network_analysis = ""
    

    try:
        with open(f"Financial_Analysis_{user_ticker}.md", "r", encoding="utf-8") as f:
            financial_data = f.read()
    except FileNotFoundError:
        print(f"WARNING: Financial_Analysis_{user_ticker}.md not found.")

    try:
        with open(f"News_Analysis_{user_ticker}.md", "r", encoding="utf-8") as f:
            news_data = f.read()
    except FileNotFoundError:
        print(f"WARNING: News_Analysis_{user_ticker}.md not found.")

    try:
        with open(f"Network_Analysis_{user_ticker}.md", "r", encoding="utf-8") as f:
            network_analysis = f.read()
    except FileNotFoundError:
        print(f"WARNING: Network_Analysis_{user_ticker}.md not found.")

    

    #  Initialize Workflow
    workflow = DebateWorkflow()

    initial_state = {
        "debate_topic": debate_topic,
        "messages": [],
        "current_speaker": "buy_debater_node",
        "turn_count": 0,
        "max_turns": 2,
        "financial_data": financial_data,
        "news_data": news_data,
        "network_analysis": network_analysis,
    }

    # Run Debate
    print("Starting trading debate workflow...")    
    try:
        workflow_result = await workflow.run(initial_state)
        
        # Check if we have messages
        if not workflow_result.get("messages"):
            print("ERROR: No messages in workflow result. Workflow may have failed.")
            # raise ValueError("Workflow completed but produced no messages")
        else:
            final_message = workflow_result["messages"][-1]["content"]
            
            if "WINNER: BUY" in final_message:
                print("  TRADING VERDICT")
                print("  %s" % final_message.replace("WINNER: BUY", "🏆 WINNER: BUY"))
            elif "WINNER: SELL" in final_message:
                print("  TRADING VERDICT")
                print("  %s" % final_message.replace("WINNER: SELL", "🏆 WINNER: SELL"))
            else:
                print("  %s" % final_message)
            
            print("Workflow completed successfully | Status: SUCCESS")
        
    except Exception as e:
        print(f"ERROR: Workflow failed: {str(e)}")
        raise

if __name__ == "__main__":
    asyncio.run(main())