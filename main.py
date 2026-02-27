 # main.py

from fastapi import FastAPI, Depends, UploadFile, File, HTTPException
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from supabase import create_client
from fastapi.middleware.cors import CORSMiddleware
import os
from pathlib import Path
import shutil
from agents.ml_model import predict_cancer
from agents.supervisor import supervisor
from auth.auth import verify_token
from routes.uploads import router as upload_router
from agents.medgemma import run_medgemma_inference
from dotenv import load_dotenv
load_dotenv()

# -------------------------------
# ENV VARIABLES
# -------------------------------

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

supabase = create_client(SUPABASE_URL,SUPABASE_KEY,SUPABASE_SERVICE_ROLE_KEY)


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

 
app.include_router(upload_router)
app.mount("/images", StaticFiles(directory="images"), name="images")
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
    image_url: str | None = None

# -------------------------------
# CHAT ENDPOINT (SECURE)
# -------------------------------

@app.post("/chat")
def chat_with_ai(data: AskRequests, user=Depends(verify_token)):
    try:
        # Integrate MedGemma if image is provided, OR just run the query through it as a secondary check
        if data.image_url or "medgemma" in data.query.lower():
            # If specifically asked or image provided, use MedGemma primarily
            medgemma_insights = run_medgemma_inference(data.query, data.image_url)
            rag_insights = str(supervisor.run(query=data.query, vision_score=data.vision_score))
            
            if "Error" in medgemma_insights or "could not be loaded" in medgemma_insights:
                # If MedGemma fails, just return the RAG/Supervisor response cleanly
                response = rag_insights
            else:
                response = f"**MedGemma Image Analysis:**\n{medgemma_insights}\n\n---\n**RAG Clinical Context:**\n{rag_insights}"
        else:
             # Run Supervisor (handles RAG or Agent Team routing)
             response = supervisor.run(
                 query=data.query,
                 vision_score=data.vision_score
             )

        # Store chat history if real user
        if user["id"] != "mock_test_id_123":
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


class LoginSchema(BaseModel):
    email: str
    password: str


@app.post("/login")
def login(data: LoginSchema):
    try:
        response = supabase.auth.sign_in_with_password({
            "email": data.email,
            "password": data.password
        })
        return {
            "access_token": response.session.access_token
        }
    except Exception as e:
        raise HTTPException(status_code=401, detail="Invalid email or password")