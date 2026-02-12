import requests
from pypdf import PdfReader
import json

OLLAMA_URL = "http://localhost:11434/api/generate"

def extract_text_from_pdf(file_path):
    reader = PdfReader(file_path)
    text = ""
    for page in reader.pages:
        text += page.extract_text() + "\n"
    return text[:10000]  # limit size

def analyze_transcript(text):

    with open("prompt.txt", "r", encoding="utf-8") as f:
        system_prompt = f.read()

    full_prompt = system_prompt + "\n\nTRANSCRIPT:\n" + text

    response = requests.post(
        OLLAMA_URL,
        json={
            "model": "llama3",
            "prompt": full_prompt,
            "stream": False
        }
    )

    result = response.json()["response"]

    try:
        return json.loads(result)
    except:
        return {"raw_output": result}
