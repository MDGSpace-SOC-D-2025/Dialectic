import streamlit as st
import asyncio
import os
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# Import backend logic 
from main import run_agents_parallel
from workflow.debate_workflow import DebateWorkflow

st.set_page_config(
    page_title="Financial Debate Analyst",
    page_icon="🏦",
    layout="wide",
)





st.title("🏦 Financial Analysis & Debate System")

# Sidebar for controls
with st.sidebar:
    st.header("Configuration")
    ticker = st.text_input("Enter Stock Ticker (e.g., NVDA):", value="NVDA").upper()

    if st.button("Run Full Analysis"):
        if ticker:
            with st.spinner(f"Running financial, news, and network analysis for {ticker}..."):
                # Run the async function
                asyncio.run(run_agents_parallel(ticker))
            st.success("Analysis Complete!")
        else:
            st.warning("Please enter a ticker.")

# Main Display Area
st.header(f"Analysis Results: {ticker}")

# Tabs for different analysis reports
tab1, tab2, tab3, tab4 = st.tabs(["Financial data", "News data", "Network data", "Debate loop"])

def read_markdown_file(filename):
    try:
        if os.path.exists(filename):
            with open(filename, "r", encoding="utf-8") as f:
                return f.read()
    except Exception:
        return None
    return None

with tab1:
    content = read_markdown_file("Financial_Analysis.md")
    if content:
        st.markdown(content)
    else:
        st.info("No Financial Analysis found. Run analysis to generate.")

with tab2:
    content = read_markdown_file("News_Analysis.md")
    if content:
        st.markdown(content)
    else:
        st.info("No News Analysis found. Run analysis to generate.")

with tab3:
    content = read_markdown_file("Network_Analysis.md")
    if content:
        st.markdown(content)
    else:
        st.info("No Network Analysis found. Run analysis to generate.")

with tab4:
    st.subheader(" Debate")
    
    if st.button("Start Debate"):
        
        topic = f"Should we buy {ticker} shares?"
        
        st.write(f"**Topic:** {topic}")
        
        
        financial_data = read_markdown_file("Financial_Analysis.md") or ""
        news_data = read_markdown_file("News_Analysis.md") or ""
        network_analysis = read_markdown_file("Network_Analysis.md") or ""
        

        initial_state = {
            "debate_topic": topic,
            "messages": [],
            "current_speaker": "buy_debater_node",
            "turn_count": 0,
            "max_turns": 8,
            "financial_data": financial_data,
            "news_data": news_data,
            "network_analysis": network_analysis,
        }

        workflow = DebateWorkflow()
        
        with st.spinner("Debating..."):
            try:
                # Run the workflow
                result = asyncio.run(workflow.run(initial_state))
                
                # Display messages
                messages = result.get("messages", [])

                for msg in messages:
                    role = msg.get("role", "unknown")
                    content = msg.get("content", "")
                    
                    with st.chat_message(role):
                        st.markdown(content)
                
                if messages:
                    final_msg = messages[-1]["content"]
                    if "WINNER: BUY" in final_msg:
                        st.success("🏆 Verdict: BUY")
                    elif "WINNER: SELL" in final_msg:
                        st.error("🏆 Verdict: SELL")
                    else:
                        st.warning("Verdict: Undecided/Neutral")
                        
            except Exception as e:
                st.error(f"Error during debate: {str(e)}")
