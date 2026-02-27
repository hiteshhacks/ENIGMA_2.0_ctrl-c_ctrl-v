# routes/upload.py

import os
import shutil
from pathlib import Path
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, BackgroundTasks
from supabase import create_client
from dotenv import load_dotenv

from services.ai_analysis import analyze_and_update
from auth.auth import verify_token  # your existing auth

load_dotenv()

router = APIRouter()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

UPLOAD_DIR = "uploads"
MAX_FILE_SIZE = 10 * 1024 * 1024
ALLOWED_TYPES = ["application/pdf", "image/jpeg", "image/png"]


@router.post("/upload")
async def upload_report(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    user: dict = Depends(verify_token)
):
    try:
        # Validate file type
        if file.content_type not in ALLOWED_TYPES:
            raise HTTPException(status_code=400, detail="Invalid file type")

        # Validate size
        file.file.seek(0, 2)
        size = file.file.tell()
        file.file.seek(0)

        if size > MAX_FILE_SIZE:
            raise HTTPException(status_code=400, detail="File too large")

        # Create folder
        Path(UPLOAD_DIR).mkdir(exist_ok=True)

        safe_name = file.filename.replace(" ", "_")
        file_path = os.path.join(UPLOAD_DIR, f"{user['id']}_{safe_name}")

        # Save file
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        if user["id"] == "mock_test_id_123":
            # Testing mock response without inserting into database
            return {
                "message": "Report uploaded successfully. (Mock Response)",
                "report_id": 999,
                "status": "analyzed",
                "summary": "This is a dummy AI summary generated in mock testing mode. MOCK_ABNORMALITIES_DETECTED.",
                "abnormalMarkers": ["Elevated dummy marker X"]
            }

        # Insert DB record
        report = supabase.table("reports").insert({
            "user_id": user["id"],
            "role": user["role"],  # patient or doctor
            "file_path": file_path,
            "status": "processing"
        }).execute()

        report_id = report.data[0]["id"]

        # 🔥 Run AI in background
        background_tasks.add_task(
            analyze_and_update,
            report_id,
            file_path,
            user["role"]
        )

        return {
            "message": "Report uploaded. AI analysis started.",
            "report_id": report_id,
            "status": "processing"
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))