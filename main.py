 # main.py

from fastapi import FastAPI, Depends, UploadFile, File
from pydantic import BaseModel
from supabase import create_client
from fastapi.middleware.cors import CORSMiddleware
import os
import shutil

from agents.supervisor import SupervisorAgent
from auth.auth import verify_token


# -------------------------------
# ENV VARIABLES
# -------------------------------

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)


# -------------------------------
# FASTAPI INIT
# -------------------------------

app = FastAPI(title="AI Early Cancer Detection API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Change in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# -------------------------------
# REQUEST SCHEMA
# -------------------------------

class AskRequests(BaseModel):
    query: str


# -------------------------------
# CHAT ENDPOINT (SECURE)
# -------------------------------

@app.post("/chat")
def chat_with_ai(data: AskRequests, user=Depends(verify_token)):

    response = SupervisorAgent.run(data.query)

    supabase.table("chat_history").insert({
        "user_id": user["id"],
        "user_message": data.query,
        "ai_response": str(response)
    }).execute()

    return {
        "response": response,
        "disclaimer": "This system provides AI-assisted risk analysis and is not a substitute for professional medical diagnosis."
    }


# -------------------------------
# FILE UPLOAD ENDPOINT
# -------------------------------

UPLOAD_DIR = "uploads"

@app.post("/upload")
async def upload_report(file: UploadFile = File(...), user=Depends(verify_token)):

    if not os.path.exists(UPLOAD_DIR):
        os.makedirs(UPLOAD_DIR)

    file_path = f"{UPLOAD_DIR}/{user['id']}_{file.filename}"

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    supabase.table("reports").insert({
        "user_id": user["id"],
        "file_path": file_path
    }).execute()

    return {
        "message": "File uploaded successfully",
        "path": file_path
    }