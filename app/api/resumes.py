import uuid
import shutil
import tempfile
import os

from fastapi import APIRouter, UploadFile, File

from app.services.document_processor import extract_text
from app.services.extraction import extract_candidate_profile
from app.db.storage import store
from app.utils.exceptions import InvalidInputError

router = APIRouter(tags=["resumes"])


@router.post("/resumes")
async def upload_resume(file: UploadFile = File(...)):
    if not file.filename:
        raise InvalidInputError("No file provided.")

    suffix = os.path.splitext(file.filename)[1].lower()

    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        shutil.copyfileobj(file.file, tmp)
        tmp_path = tmp.name

    try:
        raw_text = extract_text(tmp_path)
        candidate_id = str(uuid.uuid4())
        candidate = extract_candidate_profile(candidate_id, raw_text)
        store.add_candidate(candidate)
        return {"candidate_id": candidate_id, "candidate": candidate}
    finally:
        os.remove(tmp_path)