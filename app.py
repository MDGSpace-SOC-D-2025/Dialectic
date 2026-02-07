import streamlit as st
import asyncio
import os
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))
from main import run_agents_parallel
from workflow.debate_workflow import DebateWorkflow

st.set_page_config(
    page_title="Financial Debate Analyst",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS for stylish design
st.markdown("""
    <style>
    /* Main container styling */
    .main {
        padding-top: 2rem;
        background: linear-gradient(135deg, #e8f5e9 0%, #a5d6a7 100%);
        background-attachment: fixed;
        background-color: #f0f4f8;
    }
    
    /* Header styling */
    h1 {
        color: #28a745;  /* Changed from #1f77b4 to green */
        font-weight: 600;
        margin-bottom: 1.5rem;
        text-align: center;
    }
    
    /* Sidebar styling */
    .css-1d391kg {
        background-color: green;
    }
    
    /* Input field styling */
    .stTextInput > div > div > input {
        background-color: #ffffff;
        border: 2px solid #e0e0e0;
        border-radius: 8px;
        padding: 0.5rem;
        font-size: 1rem;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: #28a745;  /* Changed from #1f77b4 to green */
        box-shadow: 0 0 0 3px rgba(40, 167, 69, 0.1);  /* Changed to green */
    }
    
    /* Button styling */
    .stButton > button {
        width: 100%;
        background: linear-gradient(90deg, #28a745 0%, #34ce57 100%);  /* Changed to green gradient */
        color: white;
        font-weight: 600;
        padding: 0.75rem 1.5rem;
        border-radius: 8px;
        border: none;
        transition: all 0.3s ease;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    .stButton > button:hover {
        background: linear-gradient(90deg, #34ce57 0%, #28a745 100%);  /* Changed to green gradient */
        box-shadow: 0 4px 8px rgba(0,0,0,0.15);
        transform: translateY(-1px);
    }
    
    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: #e8f5e9;  /* Changed to light green background */
        padding: 0.5rem;
        border-radius: 8px;
    }
    
    .stTabs [data-baseweb="tab"] {
        background-color: #e8f5e9;  /* Changed from #d0e1f9 to light green */
        border-radius: 6px;
        padding: 0.75rem 1.5rem;
        font-weight: 500;
        color: #666;
        border: 1px solid #e0e0e0;
    }
    
    .stTabs [aria-selected="true"] {
        background-color: #28a745;  /* Changed from #1f77b4 to green */
        color: white;
        border-color: #28a745;  /* Changed to green */
    }
    
    /* Content area styling */
    .stMarkdown {
        line-height: 1.8;
        color: #333;
    }
    
    .stMarkdown h2 {
        color: #28a745;  /* Changed from #1f77b4 to green */
        border-bottom: 2px solid #e0e0e0;
        padding-bottom: 0.5rem;
        margin-top: 2rem;
    }
    
    .stMarkdown h3 {
        color: #34ce57;  /* Changed from #2c8fd1 to lighter green */
        margin-top: 1.5rem;
    }
    
    .stMarkdown strong {
        color: #28a745;  /* Changed from #1f77b4 to green */
        font-weight: 600;
    }
    
    /* Info boxes */
    .stInfo {
        background-color: #d4edda;  /* Changed from #e8f4f8 to light green */
        border-left: 4px solid #28a745;  /* Changed from #1f77b4 to green */
        padding: 1rem;
        border-radius: 4px;
    }
    
    /* Debate section styling */
    .debate-container {
        background: linear-gradient(135deg, #e8f5e9 0%, #a5d6a7 100%);  /* Changed to green gradient */
        padding: 2rem;
        border-radius: 12px;
        margin: 1rem 0;
    }
    
    /* Chat message styling */
    .stChatMessage {
        padding: 1rem;
        margin: 1rem 0;
        border-radius: 8px;
        background-color: #ffffff;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    
    /* Success/Error messages */
    .stSuccess {
        background-color: #d4edda;
        border-left: 4px solid #28a745;
    }
    
    .stError {
        background-color: #f8d7da;
        border-left: 4px solid #dc3545;
    }
    
    /* Spinner styling */
    .stSpinner > div {
        border-top-color: green;  /* Changed from #1f77b4 to green */
    }
    
    /* Code blocks */
    code {
        background-color: #f4f4f4;
        padding: 0.2rem 0.4rem;
        border-radius: 4px;
        font-size: 0.9em;
    }
    </style>
""", unsafe_allow_html=True)

# Header
# Header
st.markdown("<h1 style='text-align: left; color: green; margin-bottom: 2rem;'>🏦 FINANCIAL ANALYSIS & DEBATE SYSTEM</h1>", unsafe_allow_html=True)
# Sidebar Configuration
with st.sidebar:
    st.markdown("### ⚙️ ANALYSIS SETUP")
    st.markdown("---")
    
    ticker = st.text_input(
        "**Enter Stock Ticker**",
        
        placeholder="e.g., NVDA, AAPL, MSFT",
        help="Enter a valid stock ticker symbol"
    ).upper()
    
    st.markdown("---")
    
    if st.button("🚀 Run Full Analysis", type="primary", use_container_width=True):
        if ticker and len(ticker) > 0:
            with st.spinner(f"🔄 Running comprehensive analysis for **{ticker}**...\n\nThis may take a few moments."):
                try:
                    asyncio.run(run_agents_parallel(ticker))
                    st.success(f"✅ Analysis complete for **{ticker}**!")
                    st.balloons()
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
        else:
            st.warning("⚠️ Please enter a valid ticker symbol.")
    
    st.markdown("---")
    
    
    # Check if analysis files exist
    financial_exists = os.path.exists("Financial_Analysis.md")
    news_exists = os.path.exists("News_Analysis.md")
    network_exists = os.path.exists("Network_Analysis.md")
    
    
# Main Content Area
st.markdown(f"## 📈 ANALYSIS RESULT: **{ticker}**")


# Tabs for different analyses
tab1, tab2, tab3 = st.tabs([
    "💰 Financial Analysis",
    "📰 News Analysis", 
    "🌐 Network Analysis"
])

def read_markdown_file(filename):
    """Read markdown file with error handling"""
    try:
        if os.path.exists(filename):
            with open(filename, "r", encoding="utf-8") as f:
                content = f.read()
                return content if content.strip() else None
    except Exception as e:
        st.error(f"Error reading {filename}: {str(e)}")
    return None

# Financial Analysis Tab
with tab1:
    st.markdown("### 💰 Financial Data Analysis")
    content = read_markdown_file("Financial_Analysis.md")
    if content:
        st.markdown(content)
    else:
        st.info("📋 No financial analysis available. Please run the analysis first.")

# News Analysis Tab
with tab2:
    st.markdown("### 📰 News Data Analysis")
    content = read_markdown_file("News_Analysis.md")
    if content:
        st.markdown(content)
    else:
        st.info("📋 No news analysis available. Please run the analysis first.")

# Network Analysis Tab
with tab3:
    st.markdown("### 🌐 Network & Supply Chain Analysis")
    content = read_markdown_file("Network_Analysis.md")
    if content:
        st.markdown(content)
    else:
        st.info("📋 No network analysis available. Please run the analysis first.")

# Debate Section
st.markdown("---")
st.markdown("## Debate Loop")

# Check if all required data exists
financial_data = read_markdown_file("Financial_Analysis.md") or ""
news_data = read_markdown_file("News_Analysis.md") or ""
network_analysis = read_markdown_file("Network_Analysis.md") or ""

if not all([financial_data, news_data, network_analysis]):
    st.warning("⚠️ Please run the full analysis first before starting the debate.")
else:
    st.info("✅ All analysis data is ready. You can start the debate.")
    
    col1, col2 = st.columns([1, 3])
    
    with col1:
        debate_button = st.button("🎬 Start Debate", type="primary", use_container_width=True)
    
    with col2:
        st.markdown(f"**Debate Topic:** Should we buy **{ticker}** shares?")
    
    if debate_button:
        topic = f"Should we buy {ticker} shares?"
        
        with st.spinner(" Running debate analysis... This may take a moment."):
            try:
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
                result = asyncio.run(workflow.run(initial_state))
                
                # Display debate messages
                messages = result.get("messages", [])
                
                if messages:
                    st.markdown("### 💬 Debate Transcript")
                    st.markdown("---")
                    
                    for idx, msg in enumerate(messages):
                        role = msg.get("role", "unknown")
                        content = msg.get("content", "")
                        
                        # Style based on role
                        if role == "buy":
                            role_label = "🟢 BUY Side"
                            avatar = "🟢"
                        elif role == "sell":
                            role_label = "🔴 SELL Side"
                            avatar = "🔴"
                        elif role == "judge" or role == "moderator":
                            role_label = "⚖️ Judge"
                            avatar = "⚖️"
                        else:
                            role_label = role.title()
                            avatar = "💬"
                        
                        with st.container():
                            st.markdown(f"**{role_label}**")
                            st.markdown(content)
                            st.markdown("---")
                    
                    # Display final verdict
                    final_msg = messages[-1]["content"] if messages else ""
                    st.markdown("### 🏆 Final Verdict")
                    
                    if "WINNER: BUY" in final_msg or "BUY" in final_msg.upper():
                        st.success("**VERDICT: BUY** - The analysis suggests this is a buy opportunity.")
                    elif "WINNER: SELL" in final_msg or "SELL" in final_msg.upper():
                        st.error(" **VERDICT: SELL** - The analysis suggests avoiding this stock.")
                    else:
                        st.warning("⚖️ **VERDICT: NEUTRAL** - The analysis is inconclusive.")
                else:
                    st.warning("No debate messages were generated.")
                    
            except Exception as e:
                st.error(f"❌ Error during debate: {str(e)}")
                st.exception(e)