# main.py

from fastapi import FastAPI
from pydantic import BaseModel
from agents.supervisor import SupervisorAgent

app = FastAPI()
class AskRequests(BaseModel):
    query: str
@app.post("/ask")
def ask_cancer_agent(data: AskRequests):

    response = SupervisorAgent.run(data.query)
    return {"response": response}