from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Request, status, Header, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.responses import JSONResponse, Response
from fastapi.exceptions import RequestValidationError
from pydantic import BaseModel, EmailStr
from supabase import create_client, Client
from dotenv import load_dotenv
import os
import uvicorn
import logging
from typing import Optional

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("uvicorn")

# Load environment variables
load_dotenv()

url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY")
port: int = int(os.environ.get("PORT", 8000))

if not url or not key:
    raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set in the .env file")

# Initialize Supabase client
supabase: Client = create_client(url, key)

# Request model for auth
class AuthRequest(BaseModel):
    email: EmailStr
    password: str

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info(f"Server running and connected to Supabase on port {port}")
    yield

app = FastAPI(lifespan=lifespan)

# Custom exception handler to return 400 instead of 422 for validation errors
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"error": "Bad Request"},
    )

# --- Middleware Guard (Dependency) ---

security = HTTPBearer()

async def get_current_user(token: HTTPAuthorizationCredentials = Depends(security)):
    try:
        # Verify token with Supabase
        response = supabase.auth.get_user(token.credentials)
        user = response.user

        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired token"
            )
        return user
    except Exception as e:
        logger.error(f"Token verification error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )

# ------------------------------------------

@app.get("/")
async def root():
    return {"message": "Server is running and connected to Supabase"}

@app.get("/public/info")
async def get_public_info():
    return {"message": "Welcome stranger! This info is public."}

@app.get("/protected/profile")
async def get_protected_profile(user = Depends(get_current_user)):
    return {
        "id": user.id,
        "email": user.email,
        "created_at": user.created_at
    }

@app.get("/protected/dashboard")
async def get_protected_dashboard(user = Depends(get_current_user)):
    return {"message": "Welcome to your dashboard!"}

@app.post("/auth/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(user = Depends(get_current_user)):
    try:
        supabase.auth.sign_out()
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    except Exception as e:
        logger.error(f"Logout error: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error during logout")

@app.post("/auth/signup", status_code=status.HTTP_201_CREATED)
async def signup(auth_data: AuthRequest):
    try:
        response = supabase.auth.sign_up({
            "email": auth_data.email,
            "password": auth_data.password
        })
        return response
    except Exception as e:
        logger.error(f"Signup error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/auth/login")
async def login(auth_data: AuthRequest):
    try:
        response = supabase.auth.sign_in_with_password({
            "email": auth_data.email,
            "password": auth_data.password
        })
        return response
    except Exception as e:
        logger.error(f"Login error: {str(e)}")
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={"error": "Invalid login credentials"}
        )

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=port)
