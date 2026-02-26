# services/ai_analysis.py

from supabase import create_client
from utils.extractor import extract_text_from_pdf
from agents.cancer_agent import CancerKnowledgeAgent  # adjust this

import os
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)


async def analyze_and_update(report_id: str, file_path: str, role: str):
    try:
        # 1️⃣ Extract text from report
        text = extract_text_from_pdf(file_path)

        # 2️⃣ Role-based prompt
        if role == "doctor":
            style_prompt = "Provide detailed clinical interpretation with biomarkers and differential diagnosis."
        else:
            style_prompt = "Explain findings in simple language for patient. Be reassuring but factual."

        # 3️⃣ Send to AI Agent
        response = CancerKnowledgeAgent.run(
            f"""
            You are an oncology AI specialist.

            {style_prompt}

            Analyze this medical report:

            {text}

            Provide:
            - Risk Level
            - Key Findings
            - Explanation
            - Recommended Next Steps
            """
        )

        # 4️⃣ Update DB
        supabase.table("reports").update({
            "status": "analyzed",
            "ai_result": response
        }).eq("id", report_id).execute()

    except Exception as e:
        supabase.table("reports").update({
            "status": "failed",
            "ai_result": str(e)
        }).eq("id", report_id).execute()