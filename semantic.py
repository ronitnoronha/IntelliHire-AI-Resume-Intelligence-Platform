import re
from functools import lru_cache

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


@lru_cache(maxsize=1)
def _load_embedding_model():
    """Load the local embedding model without making unexpected network calls."""
    try:
        from sentence_transformers import SentenceTransformer

        return SentenceTransformer("all-MiniLM-L6-v2", local_files_only=True)
    except Exception:  # noqa: BLE001
        try:
            from sentence_transformers import SentenceTransformer

            return SentenceTransformer("all-MiniLM-L6-v2")
        except Exception:  # noqa: BLE001
            return None


def chunk_text(text, max_words=90, overlap=20):
    """
    Split long text into overlapping chunks to prevent embedding truncation
    beyond transformer token limits (e.g. 256 tokens for MiniLM).
    """
    if not text or not text.strip():
        return []

    # Split on double-newlines/bullet lines first if available
    lines = [
        p.strip() for p in re.split(r"\n{2,}|\n(?=[•\-\*\d\.\)])", text) if p.strip()
    ]
    if not lines:
        lines = [text.strip()]

    chunks = []
    current_words = []

    for line in lines:
        words = line.split()
        if not words:
            continue

        if len(current_words) + len(words) <= max_words:
            current_words.extend(words)
        else:
            if current_words:
                chunks.append(" ".join(current_words))
            # Handle lines longer than max_words by slicing
            if len(words) > max_words:
                for i in range(0, len(words), max_words - overlap):
                    sub = words[i : i + max_words]
                    if sub:
                        chunks.append(" ".join(sub))
                current_words = []
            else:
                # Retain overlap words
                overlap_words = (
                    current_words[-overlap:]
                    if len(current_words) >= overlap
                    else current_words
                )
                current_words = overlap_words + words

    if current_words:
        chunks.append(" ".join(current_words))

    return chunks if chunks else [text[:500]]


def _lexical_similarity(job_description, resume):
    """Offline fallback used when the embedding model is not cached."""
    if not job_description or not resume:
        return 0.0
    vectorizer = TfidfVectorizer(stop_words="english", ngram_range=(1, 2))
    try:
        vectors = vectorizer.fit_transform([job_description, resume])
        sim = float(cosine_similarity(vectors[0], vectors[1])[0][0] * 100)
        return float(np.clip(sim, 0.0, 100.0))
    except Exception:  # noqa: BLE001
        return 0.0


def semantic_similarity(job_description, resume):
    """
    Compute hybrid global + chunked aspect semantic similarity between
    the job description and the resume to eliminate token truncation.
    """
    if not job_description or not resume:
        return 0.0

    model = _load_embedding_model()

    if model is None:
        return _lexical_similarity(job_description, resume)

    try:
        jd_chunks = chunk_text(job_description, max_words=80, overlap=15)
        resume_chunks = chunk_text(resume, max_words=90, overlap=20)

        # Global document embeddings (first slice)
        jd_doc_emb = model.encode(job_description[:1000])
        resume_doc_emb = model.encode(resume[:1000])
        global_sim = float(
            cosine_similarity([jd_doc_emb], [resume_doc_emb])[0][0] * 100
        )

        # Chunk-level aspect matching
        if jd_chunks and resume_chunks:
            jd_embs = model.encode(jd_chunks)
            res_embs = model.encode(resume_chunks)
            sim_matrix = cosine_similarity(jd_embs, res_embs)
            # Max match for each JD requirement across all resume sections
            best_chunk_matches = np.max(sim_matrix, axis=1)
            chunk_sim = float(np.mean(best_chunk_matches) * 100)
            # Weighted combination: 55% chunk-level coverage + 45% holistic
            combined = (0.55 * chunk_sim) + (0.45 * global_sim)
        else:
            combined = global_sim

        return round(float(np.clip(combined, 0.0, 100.0)), 2)
    except Exception:  # noqa: BLE001
        return _lexical_similarity(job_description, resume)
