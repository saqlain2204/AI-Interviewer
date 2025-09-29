from fastapi import APIRouter, HTTPException, Form
from fastapi.responses import JSONResponse
from services.interview_models import UserPreferences
from services.interview import run_interview
import threading

router = APIRouter()

@router.post("/user_preferences", response_model=UserPreferences)
def set_user_preferences(preferences: UserPreferences):
    try:
        return preferences
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/start-interview/")
def start_interview(
    role: str = Form(...),
    experience_level: str = Form(...),
    company_name: str = Form(...),
    company_website: str = Form(...),
    type_of_interview: str = Form(...)
):
    thread = threading.Thread(target=run_interview, args=(role, experience_level, company_name, company_website, type_of_interview))
    thread.start()
    return JSONResponse({"status": "Interview started"})