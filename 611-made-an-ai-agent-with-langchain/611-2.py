import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv

from langchain_community.tools import Tool, DuckDuckGoSearchResults
from langchain.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from langchain.chains import LLMChain
from langchain.agents import initialize_agent, AgentType

load_dotenv()

# ----------------------------
# DuckDuckGo Search Tool
# ----------------------------
ddg_search = DuckDuckGoSearchResults()

# ----------------------------
# Web Fetcher Tool
# ----------------------------
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:90.0) Gecko/20100101 Firefox/90.0"
}

def parse_html(content) -> str:
    soup = BeautifulSoup(content, "html.parser")
    return soup.get_text()

def fetch_web_page(url: str) -> str:
    response = requests.get(url, headers=HEADERS, timeout=10)
    response.raise_for_status()
    return parse_html(response.content)

web_fetch_tool = Tool.from_function(
    func=fetch_web_page,
    name="WebFetcher",
    description="Fetches the content of a web page given a URL",
)

# ----------------------------
# Summarizer Tool
# ----------------------------
prompt_template = "Summarize the following content:\n\n{content}"

llm = ChatOpenAI(
    model="gpt-3.5-turbo",
    temperature=0
)

llm_chain = LLMChain(
    llm=llm,
    prompt=PromptTemplate.from_template(prompt_template)
)

summarize_tool = Tool.from_function(
    func=llm_chain.run,
    name="Summarizer",
    description="Summarizes a web page content",
)

# ----------------------------
# Initialize Agent (FIXED PART)
# ----------------------------
tools = [
    ddg_search,
    web_fetch_tool,
    summarize_tool
]

agent_executor = initialize_agent(
    tools=tools,
    llm=llm,
    agent=AgentType.OPENAI_FUNCTIONS,  # ⭐ สำคัญมาก
    verbose=True
)

# ----------------------------
# Run the Agent
# ----------------------------
prompt = "Weather in Bangkok today"

agent_executor.invoke({"input": prompt})
