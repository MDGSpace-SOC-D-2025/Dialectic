# DIALECTIC

An AI-powered system that performs multi-agent market analysis on stock tickers and conducts a simulated debate between "Buy" and "Sell" agents to provide a final verdict.

## Features

*   **Multi-Agent Data Gathering**:
    *   **Fundamental Analyst**: Fetches financial metrics and balance sheet data using `ALPHAVANTAGE API`.
    *   **News Analyst**: Aggregates and analyzes recent news sentiment using `yfinance`.
    *   **Network Analyst**: Explores supply chain relationships, sector correlations, and manufacturer relationships.  
*   **Debate Loop**: Utilizes `LangGraph` to simulate a debate between opposing viewpoints (Bull vs. Bear) based on the gathered data.
*   **Verdict Generation**: A "Judge" agent analyzes the debate history to output a final "Buy" or "Sell" recommendation.
    *   **Dashboard**: A `Streamlit` powered interactive UI for visualizing reports and the debate process.
    
## Multi-Agent System Architecture Flowchart
![Multi-Agent System Architecture Flowchart](workflow_.png)

## 📋 Prerequisites

*   Python 3.8+
*   pip

## 🛠️ Installation

1.  **Clone the repository**
    ```bash
    git clone https://github.com/MDGSpace-SOC-D-2025/Dialectic.git
    ```

2.  **Install dependencies**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Environment Configuration**
    Create a `.env` file in the root directory and add your API keys. You will need keys for LLM access (e.g., OpenRouter, OpenAI).

    ```env
    OPENROUTER_API_KEY=your_api_key_here
    OPENAI_API_BASE= "https://openrouter.ai/api/v1"

    MY_API_KEY = your_api_key_here (sec api key)
    ALPHA_VANTAGE_API_KEY = your_api_key_here
    ```

## 💻 Usage

### Streamlit Web Interface

Launch the interactive dashboard for a more visual experience.

```bash
streamlit run app.py
```
*   Enter a stock ticker in the sidebar.
*   Click **Run Full Analysis** to fetch data.
*   View generated reports in the tabs (Financial, News, Network).
*   Switch to the **Debate loop** tab and click **Start Debate** to watch the agents argue and deliver a verdict.

## Project Structure

```text
├── app.py                  # Streamlit frontend application
├── main.py                 # Main CLI entry point and workflow orchestrator
├── requirements.txt        # Python dependencies
├── configuration/          # LLM and system configurations
├── src/                    # Source code for agents
│   └── agents/             # Analysis agents (Fundamental, News, Network)
├── nodes/                  # LangGraph nodes (Debaters, Judge, etc.)
├── prompts/                # System prompts for AI agents
├── workflow/               # Debate workflow orchestration
├── utils.py                # Utility functions
├── chroma_db_*/            # Vector store persistence directories
└── *.md                    # Generated analysis reports (Financial, News, etc.)
```


