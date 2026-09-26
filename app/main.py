from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.utils.exceptions import (
    DocumentProcessingError,
    NotFoundError,
    InvalidInputError,
)
from app.api import jobs, resumes, candidates

app = FastAPI(title="AI Recruitment & Candidate Matching Platform")

app.include_router(jobs.router)
app.include_router(resumes.router)
app.include_router(candidates.router)


@app.exception_handler(DocumentProcessingError)
async def document_processing_handler(request: Request, exc: DocumentProcessingError):
    return JSONResponse(status_code=422, content={"error": str(exc)})


@app.exception_handler(NotFoundError)
async def not_found_handler(request: Request, exc: NotFoundError):
    return JSONResponse(status_code=404, content={"error": str(exc)})


@app.exception_handler(InvalidInputError)
async def invalid_input_handler(request: Request, exc: InvalidInputError):
    return JSONResponse(status_code=400, content={"error": str(exc)})


@app.get("/")
def root():
    return {"status": "ok", "message": "AI Recruitment & Candidate Matching Platform API"}