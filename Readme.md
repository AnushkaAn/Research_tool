# 📊 Earnings Call Analyzer
### AI-Powered Financial Research Portal Slice

This specialized research tool is designed for equity analysts to transform unstructured corporate earnings transcripts into structured, actionable insights. It focuses on identifying the gap between management's rhetorical optimism and the objective business headwinds found in financial data.

---

## 🚀 Live Demo
**Access the tool here:** [Insert your Deployment Link Here]

---

## 🛠️ Features
* **Intelligent Ingestion:** Automatically detects if a PDF is a valid financial transcript before processing to prevent resource waste.
* **Context-Aware Filtering:** Extracts dialogue while maintaining the flow between Management remarks and Analyst Q&A, ensuring critical "concerns" aren't filtered out.
* **Strategic Analysis (Option B):** * **Tone vs. Reality:** Distinguishes between executive sentiment and underlying data.
    * **Evidence-Based:** Every positive and concern is backed by a direct transcript quote.
    * **Guidance Mapping:** Specifically targets forward-looking statements regarding Revenue, Capex, and Margins.

---

## 🧠 Technical Judgment Calls
The following logic was implemented to ensure analyst-grade output:

### 1. Handling Management Tone
**The Challenge:** Management almost always sounds optimistic, even during poor quarters.
**The Solution:** The LLM is instructed to identify the rhetorical tone (e.g., "Resilient") while simultaneously being "ruthless" in the **Key Concerns** section. This allows the analyst to see the management's "vibe" vs. the "cold facts" side-by-side.

### 2. Preventing Hallucinations
**The Challenge:** LLMs can sometimes "invent" financial metrics.
**The Solution:** - Used a strict `temperature=0.1` to keep the model deterministic.
- Enforced a rule where every insight must include a quote of 15 words or less.
- Implemented a "Reliability Layer" in Python that replaces missing data with "Not mentioned" instead of allowing the model to guess.

### 3. Capturing the "Hidden" Concerns
**The Challenge:** Concerns are rarely in the prepared speeches.
**The Solution:** I expanded the text extraction to include the **Analyst Q&A session**. This is where analysts force management to discuss segment declines, supply chain issues, and macro headwinds.

### 4. Handling Vague Guidance
**The Challenge:** Management often provides qualitative outlooks rather than hard numbers.
**The Solution:** The tool is prompted to prioritize specific metrics (Revenue, Margin, Capex) but fall back to a "Strategic Outlook" summary if numbers are absent, ensuring the analyst still understands the company's trajectory.

### 5. Speaker Identification Reliability
**The Challenge:** PDF text extraction often merges different speakers into a wall of text.
**The Solution:** Implemented a Regex-based dialogue filter that identifies speaker patterns (e.g., `Name: Text`). This allows the system to distinguish between an Analyst's question and a CEO's answer, preventing "cross-talk" hallucination.

---

## 📸 Sample Output
![Analysis Result Example](output_screenshot.png) 
*(Note: Upload your screenshot to the GitHub repo and name it 'output_screenshot.png' for this to appear)*

---

## 💻 Local Setup & Installation

### 1. Clone the repository
```bash
git clone [https://github.com/YOUR_USERNAME/research-portal-slice.git](https://github.com/YOUR_USERNAME/research-portal-slice.git)
cd research-portal-slice
```

### 2. Setup Environment
Create a .env file in the root directory:
```bash
GROQ_API_KEY=your_actual_groq_api_key_here
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```
### 4. Run the Application
```bash
uvicorn app:app --reload
```