from fastapi import FastAPI, Form, UploadFile, File, Request
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from services.interview import run_interview, conduct_interview
from services.audio_utils import text_to_speech, speech_to_text
from services.report_generation_service import generate_report
import threading
from user_routes import router
from pathlib import Path
from uuid import uuid4
import shutil
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Allow CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8080", "http://127.0.0.1:8080", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)

# Serve the questions audio folder as static files
questions_audio_path = Path(__file__).parent / "static" / "questions"
questions_audio_path.mkdir(parents=True, exist_ok=True)
app.mount("/audio/questions", StaticFiles(directory=str(questions_audio_path)), name="questions_audio")

# In-memory session store (for demo; use DB in production)
sessions = {}

@app.post("/start-interview/")
def start_interview(
    role: str = Form(...),
    experience_level: str = Form(...),
    company_name: str = Form(...),
    company_website: str = Form(...),
    type_of_interview: str = Form(...)
):
    # Run the interview in a separate thread to avoid blocking
    thread = threading.Thread(target=run_interview, args=(role, experience_level, company_name, company_website, type_of_interview))
    thread.start()
    return JSONResponse({"status": "Interview started"})

@app.post("/api/start-session/")
def start_session(
    role: str = Form(...),
    experience_level: str = Form(...),
    company_name: str = Form(...),
    company_website: str = Form(...),
    type_of_interview: str = Form(...)
):
    session_id = str(uuid4())
    interview_info = conduct_interview(role, experience_level, company_name, company_website, type_of_interview)
    # Save session info
    sessions[session_id] = {
        "role": role,
        "experience_level": experience_level,
        "company_name": company_name,
        "company_website": company_website,
        "type_of_interview": type_of_interview,
        "interview_info": interview_info,
        "current_q": 0,
        "answers": [],
    }
    # Generate intro audio
    questions_dir = Path(__file__).parent / "static" / "questions"
    questions_dir.mkdir(parents=True, exist_ok=True)
    intro_audio = str(questions_dir / f"{session_id}_intro.wav")
    text_to_speech(interview_info["introduction"], intro_audio)
    return {"session_id": session_id, "intro_text": interview_info["introduction"], "intro_audio_url": f"/audio/questions/{session_id}_intro.wav"}

@app.get("/api/next-question/")
def next_question(session_id: str):
    session = sessions.get(session_id)
    if not session:
        return JSONResponse({"error": "Invalid session_id"}, status_code=400)
    q_idx = session["current_q"]
    questions = session["interview_info"]["questions_data"].questions
    if q_idx >= len(questions):
        return {"done": True}
    # Generate question audio if not already
    questions_dir = Path(__file__).parent / "static" / "questions"
    q_audio = questions_dir / f"{session_id}_q{q_idx+1}.wav"
    if not q_audio.exists():
        text_to_speech(questions[q_idx], str(q_audio))
    session["current_q"] += 1
    return {
        "done": False,
        "question_text": questions[q_idx],
        "question_audio_url": f"/audio/questions/{session_id}_q{q_idx+1}.wav",
        "question_idx": q_idx+1
    }

@app.post("/api/upload-answer/")
def upload_answer(session_id: str = Form(...), question_idx: int = Form(...), audio: UploadFile = File(...)):
    answers_dir = Path(__file__).parent / "static" / "answers"
    answers_dir.mkdir(parents=True, exist_ok=True)
    audio_path = answers_dir / f"{session_id}_a{question_idx}.wav"
    with audio_path.open("wb") as f:
        shutil.copyfileobj(audio.file, f)
    # Run STT and store transcript
    transcript = ""
    try:
        transcript = speech_to_text(str(audio_path))
    except Exception as e:
        transcript = f"[STT error: {e}]"
    session = sessions.get(session_id)
    if session:
        session["answers"].append({
            "audio_path": str(audio_path),
            "transcript": transcript,
            "question_idx": question_idx
        })
        # Save log after each answer IMMEDIATELY to static/answers/
        log_path = answers_dir / f"{session_id}_interview_log.json"
        log_data = {
            "user_intro": session["answers"][0]["transcript"] if session["answers"] else "",
            "questions": [
                {
                    "question": session["interview_info"]["questions_data"].questions[a["question_idx"]-1] if a["question_idx"] > 0 else "",
                    "expected_answer": session["interview_info"]["questions_data"].answers[a["question_idx"]-1] if a["question_idx"] > 0 and hasattr(session["interview_info"]["questions_data"], "answers") else "",
                    "user_answer": a["transcript"]
                }
                for a in session["answers"] if a["question_idx"] > 0
            ]
        }
        with open(log_path, "w", encoding="utf-8") as f:
            import json
            json.dump(log_data, f, indent=2, ensure_ascii=False)
    return {"status": "uploaded", "audio_url": f"/audio/answers/{session_id}_a{question_idx}.wav", "transcript": transcript, "log_file": str(log_path)}
# Graceful end interview endpoint
@app.post("/api/end-interview/")
def end_interview(session_id: str = Form(...)):
    session = sessions.get(session_id)
    if not session:
        return JSONResponse({"error": "Invalid session_id"}, status_code=400)
    answers_dir = Path(__file__).parent / "static" / "answers"
    answers_dir.mkdir(parents=True, exist_ok=True)
    log_path = answers_dir / f"{session_id}_interview_log.json"
    log_data = {
        "user_intro": session["answers"][0]["transcript"] if session["answers"] else "",
        "questions": [
            {
                "question": session["interview_info"]["questions_data"].questions[a["question_idx"]-1] if a["question_idx"] > 0 else "",
                "expected_answer": session["interview_info"]["questions_data"].answers[a["question_idx"]-1] if a["question_idx"] > 0 and hasattr(session["interview_info"]["questions_data"], "answers") else "",
                "user_answer": a["transcript"]
            }
            for a in session["answers"] if a["question_idx"] > 0
        ]
    }
    with open(log_path, "w", encoding="utf-8") as f:
        import json
        json.dump(log_data, f, indent=2, ensure_ascii=False)
    # Optionally, remove session from memory
    sessions.pop(session_id, None)
    return {"status": "interview ended", "log_file": str(log_path)}

@app.get("/api/thank-you-audio/")
def thank_you_audio(session_id: str):
    questions_dir = Path(__file__).parent / "static" / "questions"
    thank_you_audio = questions_dir / f"{session_id}_thank_you.wav"
    if not thank_you_audio.exists():
        from services.audio_utils import text_to_speech
        text_to_speech("Thank you for participating in the interview. We will keep you updated. Goodbye!", str(thank_you_audio))
    return {"thank_you_audio_url": f"/audio/questions/{session_id}_thank_you.wav"}

@app.post("/api/save-log/")
def save_log(session_id: str = Form(...), user_intro: str = Form(...), questions: str = Form(...)):
    # questions is expected to be a JSON stringified list of dicts
    import json
    log_data = {
        "user_intro": user_intro,
        "questions": json.loads(questions)
    }
    log_path = Path(__file__).parent / "static" / f"{session_id}_interview_log.json"
    with open(log_path, "w", encoding="utf-8") as f:
        json.dump(log_data, f, indent=2, ensure_ascii=False)
    return {"status": "log saved", "log_file": str(log_path)}

@app.post("/api/generate-report/")
def generate_report_api(session_id: str = Form(...)):
    import json
    # Load the interview log for this session
    log_path = Path(__file__).parent / "static" / "answers" / f"{session_id}_interview_log.json"
    if not log_path.exists():
        return JSONResponse({"error": "Log not found for session."}, status_code=404)
    with open(log_path, "r", encoding="utf-8") as f:
        log_data = json.load(f)
    # Generate PDF report
    pdf_path = Path(__file__).parent / "static" / "answers" / f"{session_id}_report.pdf"
    generate_report(log_data, pdf_path)
    return FileResponse(str(pdf_path), media_type="application/pdf", filename=f"interview_report_{session_id}.pdf")

# Serve answers audio as well
answers_audio_path = Path(__file__).parent / "static" / "answers"
answers_audio_path.mkdir(parents=True, exist_ok=True)
app.mount("/audio/answers", StaticFiles(directory=str(answers_audio_path)), name="answers_audio")