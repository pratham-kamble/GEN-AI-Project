from fastapi import APIRouter
from pydantic import BaseModel

from app.db.storage import store
from app.services.scoring import calculate_match_score
from app.services.explanation import generate_explanation
from app.services.skill_gap import build_skill_gap_report
from app.services.ranking import rank_candidates
from app.models.candidate import MatchResult
from app.utils.exceptions import NotFoundError, InvalidInputError

router = APIRouter(tags=["candidates"])


@router.get("/candidates")
def list_candidates():
    return store.list_candidates()


@router.get("/candidates/{candidate_id}")
def get_candidate(candidate_id: str):
    candidate = store.get_candidate(candidate_id)
    if not candidate:
        raise NotFoundError(f"Candidate '{candidate_id}' not found.")
    return candidate


class MatchRequest(BaseModel):
    job_id: str
    candidate_ids: list[str] | None = None  # None = match all stored candidates


@router.post("/match")
def match_candidates(payload: MatchRequest):
    job = store.get_job(payload.job_id)
    if not job:
        raise NotFoundError(f"Job '{payload.job_id}' not found.")

    candidates = (
        [store.get_candidate(cid) for cid in payload.candidate_ids]
        if payload.candidate_ids
        else store.list_candidates()
    )
    candidates = [c for c in candidates if c is not None]

    if not candidates:
        raise InvalidInputError("No valid candidates found to match.")

    results = []
    failed = []
    for candidate in candidates:
        try:
            score, matching_skills, missing_skills = calculate_match_score(candidate, job)
            explanation = generate_explanation(
                candidate.name, job.title, score, matching_skills, missing_skills
            )
            results.append(
                MatchResult(
                    candidate_id=candidate.candidate_id,
                    candidate_name=candidate.name,
                    score=score,
                    matching_skills=matching_skills,
                    missing_skills=missing_skills,
                    explanation=explanation,
                )
            )
        except Exception as e:
            failed.append({"candidate_id": candidate.candidate_id, "error": str(e)})

    if not results:
        raise InvalidInputError(f"All candidates failed to process. Errors: {failed}")

    ranked = rank_candidates(results)
    store.save_match_results(payload.job_id, ranked)
    return {"results": ranked, "failed": failed}


@router.get("/ranking/{job_id}")
def get_ranking(job_id: str):
    results = store.get_match_results(job_id)
    if not results:
        raise NotFoundError(f"No match results found for job '{job_id}'. Run /match first.")
    return [
        {
            "rank": i + 1,
            "candidate_id": r.candidate_id,
            "candidate_name": r.candidate_name,
            "total_score": r.score.total_score,
            "skill_gap": build_skill_gap_report(r.matching_skills, r.missing_skills),
        }
        for i, r in enumerate(results)
    ]