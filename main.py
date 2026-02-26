 # main.py

from fastapi import FastAPI, Depends, UploadFile, File, HTTPException
from pydantic import BaseModel
from supabase import create_client
from fastapi.middleware.cors import CORSMiddleware
import os
import shutil
from agents.ml_model import predict_cancer
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
#-----------------------------
# ML MODEL
#------------------------------
class CancerInput(BaseModel):
    Diagnosis_Age: float
    Mutation_Count: float
    Number_of_Samples_Per_Patient: float
    TMB_nonsynonymous: float
    Sex: str

# -------------------------------
# REQUEST SCHEMA
# -------------------------------

class AskRequests(BaseModel):
    query: str
    vision_score: float | None = None

# -------------------------------
# CHAT ENDPOINT (SECURE)
# -------------------------------

@app.post("/chat")
def chat_with_ai(data: AskRequests, user=Depends(verify_token)):
    try:
        # Run Supervisor (handles RAG or Agent Team routing)
        response = SupervisorAgent.run(
            query=data.query,
            vision_score=data.vision_score
        )

        # Store chat history
        supabase.table("chat_history").insert({
            "user_id": user["id"],
            "user_message": data.query,
            "ai_response": str(response)
        }).execute()

        return {
            "response": response,
            "disclaimer": "This system provides AI-assisted risk analysis and is not a substitute for professional medical diagnosis."
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# -------------------------------
# FILE UPLOAD ENDPOINT
# -------------------------------

UPLOAD_DIR = "uploads"


@app.post("/upload")
async def upload_report(file: UploadFile = File(...), user=Depends(verify_token)):
    try:
        # Ensure upload directory exists
        if not os.path.exists(UPLOAD_DIR):
            os.makedirs(UPLOAD_DIR)

        # Secure file name
        file_path = os.path.join(
            UPLOAD_DIR,
            f"{user['id']}_{file.filename}"
        )

        # Save file locally
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # Store reference in Supabase
        supabase.table("reports").insert({
            "user_id": user["id"],
            "file_path": file_path
        }).execute()

        return {
            "message": "File uploaded successfully",
            "path": file_path
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    


@app.post("/predict")
def predict(data: CancerInput):

    formatted_data = {
        "Diagnosis Age": data.Diagnosis_Age,
        "Mutation Count": data.Mutation_Count,
        "Number of Samples Per Patient": data.Number_of_Samples_Per_Patient,
        "TMB (nonsynonymous)": data.TMB_nonsynonymous,
        "Sex": data.Sex
    }

    result = predict_cancer(formatted_data)
    return result