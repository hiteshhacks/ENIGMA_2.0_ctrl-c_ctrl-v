# agents/supervisor.py
from agno.models.groq import Groq
from agno.agent import Agent
from agno.team.team import Team
from agents.web_agent import WebSearchAgent
from agents.cancer_agent import CancerKnowledgeAgent
from rag.retrival import is_diagnostic_query, analyze_cancer_case
from dotenv import load_dotenv
import os 
load_dotenv()
Groq.api_key=os.getenv("GROQ_API_KEY")


# SupervisorAgent = Team(
#     members=[WebSearchAgent, CancerKnowledgeAgent],
#     model=Groq(id="qwen/qwen3-32b"),
#     name="SupervisorAgent",
#     markdown=True,
#     show_members_responses=True,
#     instructions="""
#     When a user asks a cancer-related question:
#     1. First, use the WebSearchAgent to search for the latest information on the topic.
#     2. Then, use the CancerKnowledgeAgent to provide a structured educational explanation about the topic, incorporating any relevant information found by the WebSearchAgent.
#     3. Combine both outputs into a comprehensive response that is medically accurate and informative for the user.


#     """
#     )

# SupervisorAgent .print_response("What are early symptoms of blood cancer?", markdown=True)


class SupervisorAgent:
    """
    Supervisor Agent routes queries between:
    1. Diagnostic RAG pipeline
    2. Web + Knowledge multi-agent team
    """

    def __init__(self):

        # 🌍 General + Web Knowledge Team
        self.team = Team(
            members=[WebSearchAgent, CancerKnowledgeAgent],
            model=Groq(id="qwen/qwen3-32b"),
            name="SupervisorAgent",
            markdown=True,
            show_members_responses=False,
            instructions="""
            When a user asks a general cancer-related question:
            1. Use WebSearchAgent for latest medical updates.
            2. Use CancerKnowledgeAgent for structured educational explanation.
            3. Combine both into a medically accurate and user-friendly response.
            """
        )

    def run(self, query: str, vision_score=None):
        """
        Main routing logic
        """

        # 🔬 If diagnostic-style query → Use RAG pipeline
        if is_diagnostic_query(query):
            return analyze_cancer_case(query, vision_score)

        # 🌍 Otherwise → Use Agno Team (Web + Knowledge)
        response = self.team.run(query)

        # Clean return handling
        if hasattr(response, "content"):
            return response.content

        return str(response)


# Singleton instance (recommended for FastAPI)
supervisor = SupervisorAgent()