# agents/cancer_agent.py

from agno.agent import Agent
from agno.models.groq import Groq
def explain_cancer_topic(query: str):
    return f"""
    Analyze the user input about the symptoms and provide a medically accurate explanation
      about the following cancer-related topic:
    {query}

    Include:
    - Definition
    - Causes
    - Early symptoms
    - Screening methods
    - Prevention
    """

CancerKnowledgeAgent = Agent(
    name="CancerKnowledgeAgent",
    description="Provides structured educational explanations about cancer topics.",
    model=Groq(id="qwen/qwen3-32b"),
    tools=[explain_cancer_topic]
)