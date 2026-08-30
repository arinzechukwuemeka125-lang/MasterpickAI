from fastapi import FastAPI
from pydantic import BaseModel
import os
from supabase import create_client

app = FastAPI(title="MasterpickAI")

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY) if SUPABASE_URL and SUPABASE_KEY else None

class PickRequest(BaseModel):
    user_id: str
    matches: list

@app.get("/")
def home():
    return {"status": "MasterpickAI API is LIVE!", "version": "1.0"}

@app.get("/health")
def health():
    return {"ok": True}

@app.post("/predict")
def predict(req: PickRequest):
    return {"user_id": req.user_id, "picks": req.matches[:3], "confidence": 0.85}
