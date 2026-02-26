# agents/supervisor.py
from agno.models.groq import Groq
from agno.agent import Agent
from agno.team.team import Team
from agents.web_agent import WebSearchAgent
from agents.cancer_agent import CancerKnowledgeAgent

from dotenv import load_dotenv
import os 
load_dotenv()
Groq.api_key=os.getenv("GROQ_API_KEY")


SupervisorAgent = Team(
    members=[WebSearchAgent, CancerKnowledgeAgent],
    model=Groq(id="qwen/qwen3-32b"),
    name="SupervisorAgent",
    markdown=True,
    show_members_responses=True,
    instructions="""
    When a user asks a cancer-related question:
    1. First, use the WebSearchAgent to search for the latest information on the topic.
    2. Then, use the CancerKnowledgeAgent to provide a structured educational explanation about the topic, incorporating any relevant information found by the WebSearchAgent.
    3. Combine both outputs into a comprehensive response that is medically accurate and informative for the user.


    """
    )

SupervisorAgent .print_response("What are early symptoms of blood cancer?", markdown=True)