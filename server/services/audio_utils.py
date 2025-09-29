import os
from pathlib import Path
from groq import Groq

client = Groq()

def text_to_speech(text: str, output_path: str = None, voice: str = "Arista-PlayAI", model: str = "playai-tts"):
    if output_path is None:
        output_path = str(Path(__file__).parent / "speech.wav")
    response = client.audio.speech.create(
        model=model,
        voice=voice,
        response_format="wav",
        input=text,
    )
    response.write_to_file(output_path)
    return output_path

def speech_to_text(audio_path: str, model: str = "whisper-large-v3-turbo", prompt: str = "") -> str:
    with open(audio_path, "rb") as file:
        transcription = client.audio.transcriptions.create(
            file=(audio_path, file.read()),
            model=model,
            prompt=prompt,
            response_format="verbose_json",
        )
    return transcription.text