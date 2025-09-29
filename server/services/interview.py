import json
from services.hr_services.questions import generate_hr_questions
from services.core_cs_services.questions import generate_core_cs_questions
from services.hr_services.prompts import generate_hr_introduction_prompt
from services.core_cs_services.prompts import generate_core_cs_introduction_prompt

def conduct_interview(role, experience_level, company_name, company_website, type_of_interview):
    if type_of_interview == 'hr':
        introduction = generate_hr_introduction_prompt(company_name, role)
        questions_data = generate_hr_questions(experience_level, role, company_name, company_website)
    elif type_of_interview == 'core_cs':
        introduction = generate_core_cs_introduction_prompt(company_name, role)
        questions_data = generate_core_cs_questions(experience_level, role, company_name, company_website)
    else:
        raise ValueError("Invalid type_of_interview. Should be 'hr' or 'core_cs'.")

    return {
        "introduction": introduction,
        "questions_data": questions_data
    }

def run_interview(role, experience_level, company_name, company_website, type_of_interview):
    import threading
    import time
    from pathlib import Path
    import sounddevice as sd
    import soundfile as sf
    import numpy as np
    from services.audio_utils import text_to_speech, speech_to_text

    # Helper to play audio (cross-platform)
    import platform
    import subprocess
    import os
    def play_audio(file_path):
        if platform.system() == "Windows":
            try:
                os.startfile(str(file_path))
            except Exception as e:
                print(f"[ERROR] Could not play audio with os.startfile: {e}")
        else:
            subprocess.run(["aplay", str(file_path)])

    # Helper to record audio
    def record_audio(output_path):
        input("Press Enter to start recording...")
        print("[INFO] Recording... Press Enter again to stop.")
        recording = []

        def callback(indata, frames, time, status):
            if status:
                print(status)
            recording.append(indata.copy())

        samplerate = 44100
        channels = 1
        stream = sd.InputStream(samplerate=samplerate, channels=channels, callback=callback)
        stream.start()

        input()  # wait for Enter to stop
        print("[INFO] Stopping recording...")
        stream.stop()
        stream.close()

        recording_array = np.concatenate(recording, axis=0)
        sf.write(output_path, recording_array, samplerate)
        print(f"[INFO] Saved recording to {output_path}")

    # Conduct interview
    interview_info = conduct_interview(role, experience_level, company_name, company_website, type_of_interview)

    # Ensure folders exist
    questions_dir = Path(__file__).parent / "questions"
    answers_dir = Path(__file__).parent / "answers"
    questions_dir.mkdir(exist_ok=True)
    answers_dir.mkdir(exist_ok=True)

    # --- Interviewer intro ---
    intro_audio = str(questions_dir / "intro.wav")
    tts_thread = threading.Thread(target=text_to_speech, args=(interview_info["introduction"], intro_audio))
    tts_thread.start()
    tts_thread.join()
    print("[INFO] Playing interviewer introduction...")
    play_audio(intro_audio)
    time.sleep(1)

    # --- User intro ---
    user_intro_audio_path = str(answers_dir / "user_intro.wav")
    print("[INFO] Record your introduction:")
    record_audio(user_intro_audio_path)

    stt_thread = threading.Thread(target=speech_to_text, args=(user_intro_audio_path,))
    stt_thread.start()
    stt_thread.join()
    user_intro_text = speech_to_text(user_intro_audio_path)
    print(f"[INFO] Transcribed user introduction: {user_intro_text}")
    time.sleep(1)

    # --- Questions and Answers ---
    questions_obj = interview_info["questions_data"]
    questions = questions_obj.questions
    expected_answers = questions_obj.answers
    question_types = questions_obj.questions_type
    interview_log = []

    for idx, (q, qtype, expected) in enumerate(zip(questions, question_types, expected_answers)):
        # Generate & play question audio
        question_audio = str(questions_dir / f"question_{idx+1}.wav")
        tts_thread = threading.Thread(target=text_to_speech, args=(q, question_audio))
        tts_thread.start()
        tts_thread.join()
        print(f"[INFO] Playing Q{idx+1} audio...")
        play_audio(question_audio)
        time.sleep(1)

        # Record user answer
        user_audio_path = str(answers_dir / f"answer_{idx+1}.wav")
        print(f"[INFO] Record your answer for Q{idx+1}:")
        record_audio(user_audio_path)

        # Transcribe user answer
        stt_thread = threading.Thread(target=speech_to_text, args=(user_audio_path,))
        stt_thread.start()
        stt_thread.join()
        user_answer = speech_to_text(user_audio_path)
        print(f"[INFO] Transcribed answer: {user_answer}")

        interview_log.append({
            "question": q,
            "question_type": qtype,
            "expected_answer": expected,
            "user_answer": user_answer
        })
        time.sleep(1)

    print("[INFO] Interview complete.")

    # Save full log
    interview_data = {
        "user_intro": user_intro_text,
        "questions": interview_log
    }
    with open("interview_log.json", "w", encoding="utf-8") as f:
        import json
        json.dump(interview_data, f, indent=2, ensure_ascii=False)

    print("[INFO] Interview data saved to interview_log.json")
    
    # Thank you statement with TTS
    thank_you_text = "Thank you for participating in the interview. We will keep you updated about the next steps. Best of luck! Goodbye!"
    thank_you_audio = str((Path(__file__).parent / "questions" / "thank_you.wav"))
    tts_thread = threading.Thread(target=text_to_speech, args=(thank_you_text, thank_you_audio))
    tts_thread.start()
    tts_thread.join()
    print("[INFO] Playing thank you message...")
    try:
        play_audio(thank_you_audio)
    except Exception as e:
        print(f"[ERROR] Could not play thank you audio: {e}")
