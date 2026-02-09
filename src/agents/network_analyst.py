from langchain_community.document_loaders import WebBaseLoader
import os
from dotenv import load_dotenv
load_dotenv()
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from sec_api import QueryApi
import requests 


os.environ['USER_AGENT'] = 'DD'

def run_network_analysis(ticker: str):
    print(f"Starting Network (SEC) Analysis for {ticker}...")
    
    api_key_sec = os.environ.get("MY_API_KEY")

    final_ticker = f"ticker:{ticker}" 

    def get_filing_url(query):
        query_api = QueryApi(api_key=api_key_sec)
        try:
            filings = query_api.get_filings(query)
            if filings['filings']:
                return filings['filings'][0]['linkToFilingDetails']
            else:
                return None
        except Exception as e:
            print(f"Error fetching filings: {e}")
            return None


    query = {
        "query": f"{final_ticker} AND formType:\"10-K\"",
        "from": "0",
        "size": "1",
        "sort": [{"filedAt": {"order": "desc"}}]
    }

    url_filing = get_filing_url(query)
    
    if not url_filing:
        print(f"Could not find 10-K filing for {ticker}")
        return None

    print(f"URL: {url_filing}")

    headers = {'User-Agent': "dt dhruv.talar@gmail.com"}
    response = requests.get(url_filing, headers=headers)

    # Initialize LLM and Embeddings
    llm = ChatOpenAI(
        model="nvidia/nemotron-nano-12b-v2-vl:free",
        temperature=0,
        api_key=os.environ.get("OPENROUTER_API_KEY"),
        base_url=os.environ.get("OPENAI_API_BASE"),
        max_completion_tokens=1000,
    )

    embeddings = OpenAIEmbeddings(
        model="text-embedding-3-small", 
        api_key=os.environ.get("OPENROUTER_API_KEY"),
        base_url=os.environ.get("OPENAI_API_BASE"),
    )

    loader = WebBaseLoader(web_paths=[url_filing])

    docs = loader.load()
    # print(docs)
    text_splitter = RecursiveCharacterTextSplitter(
        separators=["\n\n", "\n", ".", " "],
        chunk_size=2000,
        chunk_overlap=100,
        add_start_index=True,
    )

    chunks = text_splitter.split_documents(docs)
    vectorstore = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory="./.chroma_db"
    )
    queries="""Item 1A, Risk Factors Risks Related to Our Industry and Markets Risks Related to Our Global Operating Business Risks Related to Demand, Supply, and Manufacturing, Risks Related to Regulatory, Legal, Our Stock and Other Matters
    Item 1. Business Our Markets Sales and Marketing
"""
    retriever = vectorstore.as_retriever(search_type="similarity", search_kwargs={"k": 5})
    relevant_docs = retriever.invoke(queries)
    # print(relevant_docs)
    context=''.join([doc.page_content for doc in relevant_docs])
    # print(context)
    response=llm.invoke(
        f"""
        You are a Senior Equity Research Analyst specializing in technology and semiconductor markets. 

Your task is to synthesize the provided excerpts from the company's SEC 10-K filing into a professional, high-level Summary   for institutional investors.

Structure your analysis into the following four thematic sections:
1. **Industry, Market, and Competitive Headwinds**
2. **Manufacturing, Supply Chain, and Third-Party Dependencies**
3. **Geopolitical, Regulatory, and Global Operations**
4. **Emerging Technologies and Product Innovation Risks**

**Formatting & Style Requirements:**
- **Tone**: Formal, objective, and analytical. Use professional financial terminology.
- **Length**: Aim for a comprehensive narrative of approximately 450 to 500 words.
- **Detail**: Do not just list risks; explain the *potential impact* on financial performance (e.g., margin compression, revenue volatility, or market share erosion).
- **Specificity**: Mention specific risks like export controls, concentration at foundries, and the transition to new architectures (e.g., Blackwell) if present in the text.

**Context:**
{context}

final analysis: 

        """
    )
    analysis = response.content
    filename = f"Network_Analysis_{ticker}.md"
    try:
        with open(filename, "w", encoding="utf-8") as f:
            # Adding a header to the Markdown file
            f.write(f"# SEC 10-K Risk Factor Analysis: {ticker}\n")
            f.write("--- \n\n")
            f.write(analysis)
            
        print(f"\nSuccessfully saved analysis to {filename}")
    except Exception as e:
        print(f"Error saving to file: {e}")




if __name__ == "__main__":
    run_network_analysis("NVDA")      

     
    

