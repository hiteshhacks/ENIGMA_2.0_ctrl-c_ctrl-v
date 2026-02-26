from fastapi import HTTPException
from jose import jwt
import requests
import os
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
JWKS_URL = f"{SUPABASE_URL}/auth/v1/.well-known/jwks.json"

jwks = requests.get(JWKS_URL).json()

def verify_token(token: str):
    try:
        header = jwt.get_unverified_header(token)
        kid = header["kid"]

        key = next((k for k in jwks["keys"] if k["kid"] == kid), None)

        if not key:
            raise HTTPException(status_code=401, detail="Invalid key")

        payload = jwt.decode(
            token,
            key,
            algorithms=["ES256"],
            audience="authenticated"
        )

        return payload

    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token")