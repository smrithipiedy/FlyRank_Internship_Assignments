from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from pydantic import BaseModel, EmailStr
from supabase import create_client, Client
from dotenv import load_dotenv
import os
import uvicorn
import logging

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

@app.get("/")
async def root():
    return {"message": "Server is running and connected to Supabase"}

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
        # Requirement: return 401 with { "error": "Invalid login credentials" }
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={"error": "Invalid login credentials"}
        )

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=port)
