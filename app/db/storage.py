from typing import Dict, List, Optional

from app.models.job import JobRequirements
from app.models.candidate import CandidateProfile, MatchResult


class InMemoryStore:
    def __init__(self):
        self.jobs: Dict[str, JobRequirements] = {}
        self.candidates: Dict[str, CandidateProfile] = {}
        self.match_results: Dict[str, List[MatchResult]] = {}  # job_id -> results

    # Jobs
    def add_job(self, job_id: str, job: JobRequirements) -> None:
        self.jobs[job_id] = job

    def get_job(self, job_id: str) -> Optional[JobRequirements]:
        return self.jobs.get(job_id)

    # Candidates
    def add_candidate(self, candidate: CandidateProfile) -> None:
        self.candidates[candidate.candidate_id] = candidate

    def get_candidate(self, candidate_id: str) -> Optional[CandidateProfile]:
        return self.candidates.get(candidate_id)

    def list_candidates(self) -> List[CandidateProfile]:
        return list(self.candidates.values())

    # Match results
    def save_match_results(self, job_id: str, results: List[MatchResult]) -> None:
        self.match_results[job_id] = results

    def get_match_results(self, job_id: str) -> List[MatchResult]:
        return self.match_results.get(job_id, [])

    # Single shared instance used across the app
store = InMemoryStore()


