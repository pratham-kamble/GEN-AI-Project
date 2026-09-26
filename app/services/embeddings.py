from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

from app.config import settings

_model = None


def get_model() -> SentenceTransformer:
    """Lazy-load the embedding model once, reuse across calls."""
    global _model
    if _model is None:
        _model = SentenceTransformer(settings.embedding_model)
    return _model


def embed_text(text: str) -> np.ndarray:
    model = get_model()
    return model.encode(text, convert_to_numpy=True)


def embed_texts(texts: list[str]) -> np.ndarray:
    model = get_model()
    return model.encode(texts, convert_to_numpy=True)


def semantic_similarity(text_a: str, text_b: str) -> float:
    """Cosine similarity between two pieces of text, 0.0 to 1.0."""
    vec_a = embed_text(text_a).reshape(1, -1)
    vec_b = embed_text(text_b).reshape(1, -1)
    sim = cosine_similarity(vec_a, vec_b)[0][0]
    return float(max(0.0, min(1.0, sim)))


def skill_semantic_match(candidate_skills: list[str], required_skills: list[str], threshold: float = 0.55):
    """
    For each required skill, find the best-matching candidate skill via embeddings.
    Returns (matching_required_skills, missing_required_skills).
    """
    if not required_skills:
        return [], []
    if not candidate_skills:
        return [], list(required_skills)

    candidate_vecs = embed_texts(candidate_skills)
    required_vecs = embed_texts(required_skills)

    sims = cosine_similarity(required_vecs, candidate_vecs)

    matching, missing = [], []
    for i, skill in enumerate(required_skills):
        best_score = sims[i].max()
        if best_score >= threshold:
            matching.append(skill)
        else:
            missing.append(skill)

    return matching, missing