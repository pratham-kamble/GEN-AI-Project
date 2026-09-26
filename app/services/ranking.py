from typing import List
from app.models.candidate import MatchResult


def rank_candidates(results: List[MatchResult]) -> List[MatchResult]:
    """Sort candidates by total score, descending — highest match first."""
    return sorted(results, key=lambda r: r.score.total_score, reverse=True)