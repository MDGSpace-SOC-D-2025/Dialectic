from sec_api import QueryApi
from langchain_community.document_loaders import WebBaseLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from typing import TypedDict, List, Annotated
import operator
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
import os
from dotenv import load_dotenv
load_dotenv()
from langgraph.graph import StateGraph, END, START
api_key = os.getenv("MY_API_KEY")

queryApi = QueryApi(api_key)

company_name = "" #Specify the company ticker here, e.g., "AAPL" for Apple Inc.

query = {
  "query": f"ticker:{company_name} AND formType:\"10-K\"",
  "from": "0",
  "size": "1",
  "sort": [{ "filedAt": { "order": "desc" } }]
}

result = queryApi.get_filings(query)

# 1. Access the first filing in the 'filings' list
if result['filings']:
    filing = result['filings'][0]
    
    # 2. Extract specific links into variables
    link_html = filing.get('linkToFilingDetails')
    link_pdf  = filing.get('linkToPdf')
    link_json = filing.get('linkToFilingData') # Usually the XBRL JSON
    
    # 3. Print them to verify
    print(f"HTML Link: {link_html}")
    
else:
    print("No filings found for this query.")
    exit()

llm = ChatOpenAI(
    model="mistralai/devstral-2512:free",
    temperature=0,
    api_key=os.environ.get("OPENROUTER_API_KEY"),
    base_url=os.environ.get("OPENAI_API_BASE"),
    max_completion_tokens=2000,
)

embeddings = OpenAIEmbeddings(
    model="text-embedding-3-small", # Using a standard model for stability
    api_key=os.environ.get("OPENROUTER_API_KEY"),
    base_url=os.environ.get("OPENAI_API_BASE"),
)
    
class GraphState(TypedDict):
    
    # It tells LangGraph to APPEND to the list rather than REPLACING it.
    summaries: Annotated[List[str], operator.add]

def process_10_K(state: GraphState):
    loader = WebBaseLoader(
        web_path=[link_html]
    ) 
    docs = loader.load()
    splits = RecursiveCharacterTextSplitter(chunk_size=2000, chunk_overlap=100).split_documents(docs)
    vectorstore = Chroma.from_documents(documents=splits, embedding=embeddings)
    
    context = vectorstore.similarity_search( """- Item 1 (Business): For manufacturing locations and raw material sources.
- Item 1A (Risk Factors): For specific supply chain disruptions and geographic dependencies.
- Item 2 (Properties): For physical locations of plants and warehouses.
- Item 7 (MD&A): For recent supply chain costs and logistics updates""",k=5)
    context_text = "".join([d.page_content for d in context])
    
    
    res = llm.invoke(f"""
                     Please provide the output in the following structured format according to the content found in the 10-K filing of Context: {context_text}.
    DESCRIBE THE FOLLOWING POINTS IN DETAIL AND IN PARAGRAPHS AND 250 WORDS FOR EACH PARAGRAPH:
    1. SUPPLY CHAIN MAPPING:
    - Key Raw Materials: List materials mentioned and identify if they are "single-sourced" or "sole-sourced."
    - Manufacturing Hubs: Identify the primary countries/regions where manufacturing occurs.
    - Logistics & Distribution: Identify critical ports, third-party logistics (3PL) providers, or transportation dependencies mentioned.

    2. GEOPOLITICAL & COUNTRY RISK:
     - For each country identified as a major source/hub, describe:
     - Political Status: Mention government stability, trade tensions (e.g., US-China), or regulatory shifts cited.
     - Economic Status: Mention inflation, currency volatility, or labor costs impacting the company in that region.

    3. RISK FACTOR CLASSIFICATION:
    - Identify and quote specific risks related to:
     - Environmental/Natural Disaster risks (e.g., climate change impact on plants).
     - Cybersecurity/IT risks in the supply chain.
     - Regulatory/Compliance risks (e.g., Uyghur Forced Labor Prevention Act, tariffs).
     - Commodity Price Volatility (e.g., fluctuations in energy or metal costs).

    4. SYNTHESIS & MITIGATION:
    - Does the company mention "dual-sourcing," "nearshoring," or "inventory stockpiling" as a defense strategy?""")

   
    
    
    return {"summaries": [f"--- {company_name} Analysis ---\n{res.content}"]}
    

workflow = StateGraph(GraphState)    
workflow.add_node("process_10_K", process_10_K)
workflow.add_edge(START, "process_10_K")
workflow.add_edge("process_10_K", END)
app= workflow.compile()

if __name__ == "__main__":
    print("Extractind and analyzing 10-K filing...\n")
    results = app.invoke({"summaries": []})
    
    for s in results["summaries"]:
        print(s)
        print("\n")