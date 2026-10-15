import os
import certifi
import requests
from dotenv import load_dotenv

from langchain_openai import ChatOpenAI
from langchain.tools import tool
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain import hub
from langchain.agents import create_react_agent, AgentExecutor

# ================================
# LOAD ENV VARIABLES
# ================================

os.environ["SSL_CERT_FILE"] = certifi.where()
load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
WEATHERSTACK_API_KEY = os.getenv("WEATHERSTACK_API_KEY")

search_tool = TavilySearchResults(max_results=2)


@tool
def get_weather_data(city: str) -> str:
    """
    Fetch current weather information for a city.
    """

    url = (
        f"https://api.weatherstack.com/current?"
        f"access_key={WEATHERSTACK_API_KEY}&query={city}"
    )

    response = requests.get(url)

    data = response.json()

    if "current" not in data:
        return f"Could not fetch weather data for {city}"

    return (
        f"City: {city}\n"
        f"Temperature: {data['current']['temperature']} degree C\n"
        f"Weather: {data['current']['weather_descriptions'][0]}\n"
        f"Humidity: {data['current']['humidity']}%"
    )


# =============================
# LLM
# =============================

llm = ChatOpenAI(
    model="gpt-3.5-turbo",
    temperature=0,
    api_key=OPENAI_API_KEY
)


# ==============================
# PROMPT
# ==============================

prompt = hub.pull("hwchase17/react")

# ===========================
# Tools
# ===========================

tools = [search_tool, get_weather_data]

# ==================================
# CREATE AGENT
# ==================================

agent = create_react_agent(
    llm=llm,
    tools=tools,
    prompt=prompt
)


# ==================================
# AGENT EXECUTOR
# ==================================

agent_executor = AgentExecutor(
    agent=agent,
    tools=tools,
    verbose=True
)

# ====================================
# RUN
# ====================================

response = agent_executor.invoke({
    "input": (
        " Tell me the capital of Australia and its current weather?"
    )
})

print(response["output"])
