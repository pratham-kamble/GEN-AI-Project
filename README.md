# AI Recruitment & Candidate Matching Platform

## 1. Project Overview
An AI-powered recruitment platform that helps recruiters screen candidates faster by automatically comparing resumes against a Job Description, scoring and ranking candidates, and generating AI explanations of each candidate's fit — replacing manual resume-by-resume review with a structured, explainable pipeline.

## 2. Problem Statement
Recruiters often receive large volumes of resumes for a single opening. Manually comparing every resume against the Job Description is slow and inconsistent. This system uses NLP/LLM techniques to understand both the JD and resumes semantically, then automates comparison, scoring, and ranking.

## 3. Objectives
- Extract structured information from Job Descriptions and resumes using an LLM
- Match candidates to job requirements using semantic similarity, not just keyword matching
- Produce a transparent, weighted match score per candidate
- Rank candidates and highlight skill gaps
- Generate a human-readable AI explanation of each candidate's fit
- Handle malformed input and failures gracefully, without crashing

## 4. Features
- Upload/create a Job Description (raw text)
- Upload candidate resumes (PDF or DOCX)
- LLM-based structured extraction of job requirements and candidate profiles
- Semantic (embedding-based) skill and requirement matching
- Weighted candidate scoring across 5 categories
- Candidate ranking by total score
- Matching vs. missing skill-gap report per candidate
- LLM-generated natural-language fit explanation per candidate
- Graceful per-candidate failure handling during batch matching

## 5. Technology Stack
- **Backend**: FastAPI, Uvicorn
- **Document processing**: `pdfplumber` (PDF), `python-docx` (DOCX)
- **LLM**: Groq API, model `openai/gpt-oss-20b`
- **Embeddings**: `sentence-transformers` (`all-MiniLM-L6-v2`)
- **Similarity**: `scikit-learn` cosine similarity
- **Validation/schemas**: Pydantic v2
- **Storage**: in-memory Python store (see Known Limitations)

## 6. System Architecture
Recruiter
│
▼
FastAPI Backend
│
├── Document Processor (PDF/DOCX → raw text)
│
├── LLM (Groq: openai/gpt-oss-20b)
│ ├── Job requirement extraction
│ ├── Candidate profile extraction
│ └── Fit explanation generation
│
├── Embedding Model (sentence-transformers)
│ └── Semantic similarity (skills, education, projects)
│
├── Scoring Engine (weighted, 5 categories)
│
├── Ranking Engine
│
├── Skill Gap Analyzer
│
└── In-Memory Store (jobs, candidates, match results)


## 7. Application Workflow
1. Recruiter submits a Job Description → `POST /jobs`
2. LLM extracts required/preferred skills, experience, education, responsibilities
3. Recruiter uploads a resume → `POST /resumes`
4. Document processor extracts raw text; LLM extracts structured candidate profile
5. Recruiter triggers matching → `POST /match`
6. For each candidate: semantic skill matching → weighted scoring → LLM explanation
7. Results are ranked and stored
8. Recruiter views ranked results and skill gaps → `GET /ranking/{job_id}`

## 8. Resume Processing Approach
Uploaded files are written to a temporary file and routed by extension:
- `.pdf` → `pdfplumber`, extracting text page by page
- `.docx` → `python-docx`, extracting non-empty paragraphs

Unsupported extensions, unreadable/corrupted files, and documents with no extractable text each raise a distinct, caught exception rather than crashing the request.

## 9. LLM Usage
The Groq API (`openai/gpt-oss-20b`) is used for three tasks, each with a dedicated prompt:
1. **Job requirement extraction** — raw JD text → structured JSON (required/preferred skills, experience, education, responsibilities)
2. **Candidate profile extraction** — raw resume text → structured JSON (name, skills, experience, education, projects, certifications)
3. **Explanation generation** — score breakdown + matched/missing skills → a 3–5 sentence recruiter-facing explanation

Extraction calls use `temperature=0` for consistency; explanation generation uses `temperature=0.3` for more natural phrasing. All LLM responses are parsed defensively — missing fields default sensibly rather than raising.

## 10. Embedding Approach
Candidate skills, job skills, education strings, and project descriptions are embedded using `sentence-transformers/all-MiniLM-L6-v2`. Similarity is computed via cosine similarity (`scikit-learn`). This lets the system recognize that e.g. "Developed REST APIs using Python, FastAPI and Django" satisfies a requirement for "Python backend development experience", without requiring exact keyword overlap.

## 11. Matching Methodology
For each required/preferred skill, the system embeds it and every candidate skill, then takes the highest cosine similarity score. A skill counts as "matched" if that best score is ≥ **0.55** (tunable). This threshold-based approach is applied consistently to required skills, preferred skills, education requirements, and project relevance to job responsibilities.

## 12. Scoring Methodology
Total score out of 100, split into 5 weighted categories:

| Category | Weight | Basis |
|---|---|---|
| Required Skills | 40% | % of required skills semantically matched |
| Experience | 25% | candidate years ÷ required years (capped at 100%) |
| Projects | 20% | avg. semantic relevance of projects to job responsibilities |
| Education | 10% | semantic similarity to stated education requirements |
| Additional (Preferred) Skills | 5% | % of preferred skills semantically matched |

Each category's score is computed independently and summed — see `app/services/scoring.py`, where each category is its own function for transparency and testability.

## 13. API Documentation
Interactive docs available at `/docs` (Swagger UI) once the server is running.

| Endpoint | Method | Description |
|---|---|---|
| `/jobs` | POST | Create a job from title + raw JD text; returns extracted requirements |
| `/resumes` | POST | Upload a resume file (PDF/DOCX); returns extracted candidate profile |
| `/candidates` | GET | List all stored candidates |
| `/candidates/{id}` | GET | Get a single candidate's profile |
| `/match` | POST | Score all (or specified) candidates against a job; returns ranked results + any per-candidate failures |
| `/ranking/{job_id}` | GET | Retrieve the stored ranking + skill gap report for a job |

## 14. Installation
```bash
git clone <your-repo-url>
cd recruitment-platform
pip install -r requirements.txt
```

## 15. Environment Variables
Copy `.env.example` to `.env` and fill in:
GROQ_API_KEY=your_groq_api_key_here
GROQ_MODEL=openai/gpt-oss-20b
EMBEDDING_MODEL=all-MiniLM-L6-v2


## 16. Running Instructions
```bash
uvicorn app.main:app --reload
```
Then open `http://127.0.0.1:8000/docs`.

> Note: `--reload` restarts the process (and clears in-memory data) on every file save — omit it when running a full test sequence.

## 17. Testing
Manual test scenarios covered (via `/docs`):
- Valid PDF and DOCX resumes
- Invalid/unsupported file format
- Empty document
- Corrupted document
- Missing Job Description text
- Candidate with high skill match vs. low skill match
- Semantically similar but differently worded skills (e.g. "REST API development" vs. "built REST APIs with FastAPI")
- Multiple candidates matched against one job
- No candidates available to match
- Non-existent job/candidate IDs

## 18. Error Handling
Custom exceptions (`app/utils/exceptions.py`) map to clean HTTP responses via global handlers in `app/main.py`:
- `DocumentProcessingError` (corrupted file, unsupported format, empty document, LLM/embedding failure) → 422
- `NotFoundError` (unknown job/candidate ID) → 404
- `InvalidInputError` (empty text, no valid candidates) → 400

During batch matching, a failure on one candidate is caught and reported in a `failed` list rather than aborting the whole request — other candidates still get scored and ranked.

## 19. Known Limitations
- Storage is in-memory only; all data is lost on server restart
- Single JD-to-resume(s) matching only; no persistent multi-job history beyond the current session
- Skill-match threshold (0.55) is a fixed heuristic, not calibrated against a labeled dataset
- No authentication/authorization layer
- No frontend UI; interaction is via Swagger docs or direct API calls

## 20. Future Improvements
- Persistent storage (PostgreSQL or SQLite)
- A lightweight frontend (React or Streamlit) for recruiters
- Configurable/learned skill-match threshold
- Support for more resume formats (e.g. `.txt`, scanned PDFs via OCR)
- Batch resume upload (multiple files in one request)
- Authentication for multi-recruiter use