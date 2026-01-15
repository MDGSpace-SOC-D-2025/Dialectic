# DIALECTIC

An AI-powered system that performs multi-agent market analysis on stock tickers and conducts a simulated debate between "Buy" and "Sell" agents to provide a final trading verdict.

## Features

*   **Multi-Agent Data Gathering**:
    *   **Fundamental Analyst**: Fetches financial metrics and balance sheet data using `ALPHAVANTAGE API`.
    *   **News Analyst**: Aggregates and analyzes recent news sentiment using `yfinance`.
    *   **Network Analyst**: Explores supply chain relationships and sector correlations.
*   **AI-Driven Debate Loop**: Utilizes `LangGraph` to simulate a debate between opposing viewpoints (Bull vs. Bear) based on the gathered data.
*   **Verdict Generation**: A "Judge" agent analyzes the debate history to output a final "Buy" or "Sell" recommendation.
    *   **Web Dashboard**: A `Streamlit` powered interactive UI for visualizing reports and the debate process.

## 📋 Prerequisites

*   Python 3.8+
*   pip

## 🛠️ Installation

1.  **Clone the repository**
    ```bash
    git clone <repository_url>
    cd MDG
    ```

2.  **Install dependencies**
    ```bash
    pip install -r requirment.txt
    ```

3.  **Environment Configuration**
    Create a `.env` file in the root directory and add your API keys. You will need keys for LLM access (e.g., OpenRouter, OpenAI).

    ```env
    OPENROUTER_API_KEY=your_api_key_here
    # Add other necessary keys based on config
    ```
    *(Note: Refer to `configuration/llm_config.py` for supported LLM providers.)*

## 💻 Usage

### 1. Command Line Interface (CLI)

Run the analysis and debate directly from the terminal.

```bash
# Analyze a specific ticker
python main.py --ticker NVDA

```

### 2. Streamlit Web Interface

Launch the interactive dashboard for a more visual experience.

```bash
streamlit run app.py
```
*   Enter a stock ticker in the sidebar.
*   Click **Run Full Analysis** to fetch data.
*   View generated reports in the tabs (Financial, News, Network).
*   Switch to the **Debate loop** tab and click **Start Debate** to watch the agents argue and deliver a verdict.

## 📂 Project Structure

```text
├── app.py                  # Streamlit frontend application
├── main.py                 # Main CLI entry point and workflow orchestrator
├── requirment.txt          # Python dependencies
├── configuration/          # LLM and system configurations
├── src/                    # Source code for agents
│   └── agents/             # Analysis agents (Fundamental, News, Network)
├── nodes/                  # LangGraph nodes (Debaters, Judge, etc.)
├── prompts/                # System prompts for AI agents
├── workflow/               # Debate workflow definition
├── utils.py                # Utility functions
└── *.md                    # Generated analysis reports (Financial, News, etc.)
```


