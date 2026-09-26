import uuid
from fastapi import APIRouter
from pydantic import BaseModel

from app.services.extraction import extract_job_requirements
from app.db.storage import store
from app.utils.exceptions import InvalidInputError

router = APIRouter(tags=["jobs"])


class CreateJobRequest(BaseModel):
    title: str
    raw_text: str


@router.post("/jobs")
def create_job(payload: CreateJobRequest):
    if not payload.raw_text.strip():
        raise InvalidInputError("Job description text cannot be empty.")

    job_requirements = extract_job_requirements(payload.title, payload.raw_text)
    job_id = str(uuid.uuid4())
    store.add_job(job_id, job_requirements)

    return {"job_id": job_id, "job": job_requirements}