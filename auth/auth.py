# from fastapi import HTTPException
# from jose import jwt
# import requests
# import os
# from dotenv import load_dotenv

# load_dotenv()

# SUPABASE_URL = os.getenv("SUPABASE_URL")
# JWKS_URL = f"{SUPABASE_URL}/auth/v1/.well-known/jwks.json"

# jwks = requests.get(JWKS_URL).json()

# def verify_token(token: str):
#     try:
#         header = jwt.get_unverified_header(token)
#         kid = header["kid"]

#         key = next((k for k in jwks["keys"] if k["kid"] == kid), None)

#         if not key:
#             raise HTTPException(status_code=401, detail="Invalid key")

#         payload = jwt.decode(
#             token,
#             key,
#             algorithms=["ES256"],
#             audience="authenticated"
#         )

#         return payload

#     except Exception:
#         raise HTTPException(status_code=401, detail="Invalid token")



from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
 
 
 
from jose import jwt
import requests
import os
from dotenv import load_dotenv

load_dotenv()
security = HTTPBearer()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_JWT_SECRET = os.getenv("SUPABASE_JWT_SECRET")

def verify_token(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    token = credentials.credentials

    try:
        payload = jwt.decode(
            token,
            SUPABASE_JWT_SECRET,
            algorithms=["HS256", "ES256"]
        )

        return {
            "id": payload.get("sub"),
            "email": payload.get("email"),
            "role": payload.get("role")
        }

    except Exception:
        raise HTTPException(status_code=401, detail="Invalid or expired token")