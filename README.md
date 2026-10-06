# Aegis ATS — Modern AI Resume Screener & Model Context Protocol (MCP) Platform

An enterprise-grade AI Applicant Tracking System (ATS) combining **chunk-aware Sentence Transformer embeddings**, dynamic skill gap extraction, generative recruiter co-pilot intelligence, an async **FastAPI** backend, a **FastMCP** agent server, and a modern **React + Vite** recruiter dashboard.

---

## 🚀 Key Modern Features

1. **Chunked Aspect-Level Embeddings (`all-MiniLM-L6-v2`)**:
   - Eliminates the classic 256-token truncation limitation of basic sentence transformers.
   - Splits resumes and job descriptions into overlapping semantic blocks, running max-pooling bipartite similarity so qualifications deep within page 2 are scored accurately.
   - Graceful fallback to TF-IDF n-gram vectorization when running in resource-constrained or offline environments.

2. **Expanded Technical Taxonomy & Boundary-Safe NLP**:
   - 75+ categorized skills spanning modern Web (React, Next.js, FastAPI), AI/GenAI (RAG, LangChain, Transformers, Qdrant), Cloud (AWS, Kubernetes, Terraform), and Data Engineering (Snowflake, dbt, Spark).
   - Regex word boundary enforcement preventing substring false positives (e.g., distinguishing single-letter `R` from `developer`).

3. **Native Model Context Protocol (MCP 2.x) Server**:
   - Exposes tools to AI assistants (Claude Desktop, Cursor, Antigravity):
     - `screen_resumes_directory`: Batch screens a directory of candidate PDFs.
     - `screen_single_resume`: Deep-dive ATS scoring & section analysis.
     - `extract_skills_from_jd`: Technical skill parser.
     - `sample://resume`: Context resource.
     - `blind_evaluation_prompt`: Bias-free evaluation prompt template.

4. **Async FastAPI REST Backend**:
   - High-performance asynchronous endpoint (`POST /api/screen`) supporting multipart multi-PDF uploads.
   - Pydantic v2 strict schemas with automated Swagger documentation at `/docs`.

5. **Modern Recruiter Dashboard (React 19 + Vite)**:
   - Drag-and-drop resume dropzone with multi-file staging.
   - Preset job descriptions (Senior Full-Stack AI Engineer, ML Engineer, Cloud Platform Lead).
   - Leaderboard cards with ATS score gauges, matched/missing skill badges, and contact details.
   - Interactive Candidate Deep-Dive Modal with AI executive summary, strengths, weaknesses, and interview questions (with 1-click clipboard copy).

---

## 🛠️ Tech Stack

- **Backend**: Python 3.11+, FastAPI, Uvicorn, Pydantic v2, PyMuPDF, spaCy, Sentence-Transformers, Scikit-learn, OpenAI SDK (Groq).
- **Agent / Protocol**: FastMCP (`mcp>=1.0.0` / MCP 2.x specification).
- **Frontend**: React 19, Vite, Lucide Icons, Canvas-Confetti, Vanilla CSS modern design system with glassmorphism and dark mode.
- **Legacy UI**: Streamlit (`app.py`).

---

## 🚦 Getting Started

### 1. Environment Setup
Activate the virtual environment:
```bash
source .venv/bin/activate
pip install -r requirements.txt
```

Set your Groq API key in `.env`:
```env
GROQ_API_KEY=your_groq_api_key_here
```

### 2. Run the Modern Web Dashboard & API

**Terminal 1 — FastAPI Backend**:
```bash
uvicorn backend.main:app --reload --port 8000
```
API Documentation: [http://localhost:8000/docs](http://localhost:8000/docs)

**Terminal 2 — Modern React Dashboard**:
```bash
cd frontend
npm install
npm run dev
```
Web App: [http://localhost:5173](http://localhost:5173)

---

### 3. Connect to Model Context Protocol (MCP)

To use Aegis ATS inside **Claude Desktop**, add this to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "resume-screener": {
      "command": "/Users/ronitnoronha/Downloads/Resume_Screener/.venv/bin/python",
      "args": [
        "/Users/ronitnoronha/Downloads/Resume_Screener/mcp_server.py"
      ]
    }
  }
}
```

Now you can ask Claude:
> *"Use resume-screener to screen all candidate PDFs in my Downloads folder for a Senior Python & Kubernetes role."*

---

### 4. Run the Legacy Streamlit App (Optional)

```bash
streamlit run app.py
```

---

### 5. Running Automated Tests

```bash
.venv/bin/python -m unittest test_suite.py
```
