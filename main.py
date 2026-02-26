 # main.py

from fastapi import FastAPI, Depends, UploadFile, File, HTTPException
from pydantic import BaseModel
from supabase import create_client
from fastapi.middleware.cors import CORSMiddleware
import os
from pathlib import Path
import shutil
from agents.ml_model import predict_cancer
from agents.supervisor import SupervisorAgent
from auth.auth import verify_token
from routes.uploads import router as upload_router

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


app.include_router(upload_router)
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
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB limit
ALLOWED_TYPES = ["application/pdf", "image/jpeg", "image/png"]


@app.post("/upload")
async def upload_report(
    file: UploadFile = File(...),
    user: dict = Depends(verify_token)
):
    try:
        # 1️⃣ Validate file type
        if file.content_type not in ALLOWED_TYPES:
            raise HTTPException(
                status_code=400,
                detail="Only PDF, JPG, and PNG files are allowed."
            )

        # 2️⃣ Validate file size
        file.file.seek(0, 2)  # Move to end of file
        file_size = file.file.tell()
        file.file.seek(0)  # Reset pointer

        if file_size > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=400,
                detail="File size exceeds 5MB limit."
            )

        # 3️⃣ Ensure upload directory exists
        Path(UPLOAD_DIR).mkdir(parents=True, exist_ok=True)

        # 4️⃣ Secure filename (remove spaces & risky chars)
        safe_filename = file.filename.replace(" ", "_")
        file_path = os.path.join(
            UPLOAD_DIR,
            f"{user['id']}_{safe_filename}"
        )

        # 5️⃣ Save file locally
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # 6️⃣ Save reference in Supabase
        supabase.table("reports").insert({
            "user_id": user["id"],
            "file_path": file_path,
            "file_type": file.content_type,
            "file_size": file_size
        }).execute()

        return {
            "message": "File uploaded successfully",
            "file_name": safe_filename,
            "file_size_kb": round(file_size / 1024, 2)
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


class LoginSchema(BaseModel):
    email: str
    password: str


@app.post("/login")
def login(data: LoginSchema):
    response = supabase.auth.sign_in_with_password({
        "email": data.email,
        "password": data.password
    })

    return {
        "access_token": response.session.access_token
    }