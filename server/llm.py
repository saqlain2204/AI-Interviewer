from langchain_groq import ChatGroq
import os
from dotenv import load_dotenv
load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

def get_text_model():
    return ChatGroq(model="llama-3.1-8b-instant", temperature=0, api_key=GROQ_API_KEY)
