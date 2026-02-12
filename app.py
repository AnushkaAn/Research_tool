import json
import re
import io
import os
from fastapi import FastAPI, UploadFile, File, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from groq import Groq
import PyPDF2
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()
templates = Jinja2Templates(directory="templates")
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# ---------------- PDF TEXT EXTRACTION ----------------
def extract_text(file_bytes):
    pdf_reader = PyPDF2.PdfReader(io.BytesIO(file_bytes))
    text = ""
    # Increased limit to capture Q&A where the "Concerns" and "Guidance" usually hide
    for page in pdf_reader.pages:
        t = page.extract_text()
        if t:
            text += t + "\n"
    return text[:25000] 

# ---------------- IMPROVED DIALOGUE FILTER ----------------
def extract_relevant_context(text: str) -> str:
    """
    Captures the flow of the call. We want Management remarks 
    AND Analyst questions to provide context for 'Concerns'.
    """
    lines = text.split("\n")
    # Pattern to identify speakers (e.g., "John Doe:", "Operator:")
    speaker_pattern = re.compile(r"^[A-Z][A-Za-z .\-']{2,40}:")
    
    cleaned_transcript = []
    for line in lines:
        line = line.strip()
        if speaker_pattern.match(line):
            # Exclude operator instructions to save tokens
            if "operator:" in line.lower():
                continue
            cleaned_transcript.append(f"\n{line}")
        else:
            cleaned_transcript.append(line)
            
    return " ".join(cleaned_transcript)

# ---------------- SIMPLE INTELLIGENCE LAYER ----------------
def is_earnings_call(text: str) -> bool:
    keywords = ["revenue", "ebitda", "quarter", "analyst", "guidance", "margin", "fiscal"]
    text = text.lower()
    score = sum(1 for k in keywords if k in text)
    return score >= 3

# ---------------- SAFE JSON PARSE ----------------
def safe_json_parse(output: str):
    try:
        return json.loads(output)
    except:
        match = re.search(r"\{.*\}", output, re.DOTALL)
        if match:
            try:
                return json.loads(match.group())
            except: pass
    return None

# ---------------- ROUTES ----------------
@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/analyze")
async def analyze(file: UploadFile = File(...)):
    content = await file.read()
    document_text = extract_text(content)

    if not is_earnings_call(document_text):
        raise HTTPException(status_code=400, detail="Document does not appear to be a financial transcript.")

    # Process transcript to maintain speaker flow
    processed_context = extract_relevant_context(document_text)

    prompt = f"""
You are a Senior Equity Research Analyst. 

TASK: Summarize the management's perspective versus the underlying business reality.

STRICT JSON STRUCTURE:
{{
"management_tone": "Identify the rhetorical tone (e.g., Optimistic, Resilient, Cautious).",
"confidence_level": "How reliable is the data provided for future modeling?",
"key_positives": ["Point (Quote: '...')"],
"key_concerns": ["Point (Quote: '...')"],
"forward_guidance": "Specific outlook details",
"capacity_utilization_trend": "Trend details",
"new_growth_initiatives": ["Initiative (Quote: '...')"]
}}

GUIDELINES:
- TONE: Even if there are declines, if Management focuses on 'Record TCV' and '$30B milestones', the tone is "Optimistic/Resilient".
- CONCERNS: Be ruthless. If the Consumer segment declined 0.2%, list it as a concern even if Management glosses over it.
- QUOTES: Keep them under 15 words.

Transcript:
{processed_context}
"""

    completion = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.1, # Low temperature for high accuracy
    )

    output = completion.choices[0].message.content
    parsed = safe_json_parse(output)

    if not parsed:
        return JSONResponse(status_code=500, content={"error": "Failed to parse analyst output."})

    # Reliability Fallbacks
    required_keys = ["management_tone", "confidence_level", "key_positives", "key_concerns", "forward_guidance", "capacity_utilization_trend", "new_growth_initiatives"]
    for k in required_keys:
        if k not in parsed or not parsed[k]:
            parsed[k] = [] if "key" in k or "initiatives" in k else "Not mentioned"

    return JSONResponse(content=parsed)