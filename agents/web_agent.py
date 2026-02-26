# agents/web_agent.py
from agno.agent import Agent
from agno.models.groq import Groq
from agno.tools.duckduckgo import DuckDuckGoTools

 

WebSearchAgent = Agent(
    name="WebSearchAgent",
    model=Groq(id="qwen/qwen3-32b"),
    description="Searches the web for latest medical and cancer-related information.",
    tools=[DuckDuckGoTools()]
)