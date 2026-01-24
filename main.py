import asyncio
import os
import sys
import logging
import argparse
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# Add project root to Python path
project_root = Path(__file__).parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from workflow.debate_workflow import DebateWorkflow


# Import the agent functions
from src.agents.updated_fundamentalist import run_fundamental_analysis
from src.agents.news_analyst import run_news_analysis
from src.agents.network_analyst import run_network_analysis

def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    )
    logging.getLogger("httpx").setLevel(logging.WARNING)

def validate_env():
    required_var = "OPENROUTER_API_KEY"
    if not os.environ.get(required_var):
        raise EnvironmentError(f"Missing environment variable: {required_var}")
async def run_agents_parallel(ticker: str):
    """Runs the three data gathering agents in parallel."""
    logger = logging.getLogger("main")
    logger.info(f"\n Starting Parallel Data Gathering for {ticker}...\n")
    
    # Run synchronous functions in parallel threads
    loop = asyncio.get_running_loop()
    
    
    tasks = [
        loop.run_in_executor(None, run_fundamental_analysis, ticker),
        loop.run_in_executor(None, run_news_analysis, ticker),
        loop.run_in_executor(None, run_network_analysis, ticker)
    ]
    
   
    await asyncio.gather(*tasks)
    logger.info(f"\n Data Gathering Complete for {ticker}!\n")

async def main():
    setup_logging()
    logger = logging.getLogger("main")
    
    parser = argparse.ArgumentParser(description='Trading Debate Workflow - Buy vs Sell Analysis') #This section allows you to pass information to the script directly from your terminal.
    parser.add_argument('--topic', type=str, required=False, help='Trading decision topic (e.g., "Should we buy/sell AAPL stock?")')
    parser.add_argument("--ticker", type=str, help="Ticker symbol to analyze and debate (e.g., NVDA). If provided, will run data gathering.")
    
    args = parser.parse_args()
    
    validate_env()
    
    user_ticker = args.ticker
    
    if not user_ticker:
        try:
            
            print("\n No ticker argument provided (usage: python main.py --ticker NVDA)")
            user_input = input("Enter a ticker symbol to analyze : ").strip().upper()
            if user_input:
                user_ticker = user_input
        except EOFError:
            pass

   
    if user_ticker:
        # If ticker is provided, run agents first
        await run_agents_parallel(user_ticker)
        # We don't set debate_topic yet, we'll infer it from the files or use default
    else:
         logger.info("No ticker provided. Using existing local analysis files if available.")
    #  Determine Topic
    debate_topic = args.topic
    if not debate_topic:
        if user_ticker:
            debate_topic = f"Should we buy {user_ticker}?"
        else:
            debate_topic = "General Market Debate"
            logger.warning(f" Could not infer topic. Using default: {debate_topic}")

    logger.info(f" Debate Topic: {debate_topic}")

    #  Load Data from Markdown Files
    financial_data = ""
    news_data = ""
    network_analysis = ""
    

    try:
        with open("Financial_Analysis.md", "r", encoding="utf-8") as f:
            financial_data = f.read()
    except FileNotFoundError:
        logger.warning(" Financial_Analysis.md not found.")

    try:
        with open("News_Analysis.md", "r", encoding="utf-8") as f:
            news_data = f.read()
    except FileNotFoundError:
        logger.warning(" News_Analysis.md not found.")

    try:
        with open("Network_Analysis.md", "r", encoding="utf-8") as f:
            network_analysis = f.read()
    except FileNotFoundError:
        logger.warning(" Network_Analysis.md not found.")

    

    #  Initialize Config & Workflow
    workflow = DebateWorkflow()

    initial_state = {
        "debate_topic": debate_topic,
        "messages": [],
        "current_speaker": "buy_debater_node",
        "turn_count": 0,
        "max_turns": 8,
        "financial_data": financial_data,
        "news_data": news_data,
        "network_analysis": network_analysis,
    }

    # Run Debate
    logger.info("Starting trading debate workflow...")
    logger.info(f"Trading Decision: {debate_topic}")
    
    try:
        workflow_result = await workflow.run(initial_state)
        
        # Check if we have messages
        if not workflow_result.get("messages"):
            logger.error("No messages in workflow result. Workflow may have failed.")
            # raise ValueError("Workflow completed but produced no messages")
        else:
            final_message = workflow_result["messages"][-1]["content"]
            logger.info("\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
            if "WINNER: BUY" in final_message:
                logger.info("  TRADING VERDICT")
                logger.info("  %s", final_message.replace("WINNER: BUY", "🏆 WINNER: BUY"))
            elif "WINNER: SELL" in final_message:
                logger.info("  TRADING VERDICT")
                logger.info("  %s", final_message.replace("WINNER: SELL", "🏆 WINNER: SELL"))
            else:
                logger.info("  %s", final_message)
            logger.info("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n")
            logger.info("Workflow completed successfully | Status: SUCCESS")
        
    except Exception as e:
        logger.error("Workflow failed: %s", str(e), exc_info=True)
        raise

if __name__ == "__main__":
    asyncio.run(main())