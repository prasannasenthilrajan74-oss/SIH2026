import math
import numpy as np
from sqlalchemy.orm import Session
from backend.app.models.models import Work

# Attempt to load sentence-transformers, fall back to TF-IDF
try:
    from sentence_transformers import SentenceTransformer
    model_name = "all-MiniLM-L6-v2"
    sentence_model = SentenceTransformer(model_name)
    HAS_TRANSFORMERS = True
    print("sentence-transformers loaded successfully.")
except Exception as e:
    HAS_TRANSFORMERS = False
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity
    print(f"sentence-transformers not available ({e}). Falling back to TF-IDF vectorizer.")

def haversine_distance(lat1, lon1, lat2, lon2):
    """Calculate the great-circle distance between two points in km."""
    if lat1 is None or lon1 is None or lat2 is None or lon2 is None:
        return 999.0 # Very far
    
    R = 6371.0  # Radius of Earth in kilometers
    d_lat = math.radians(lat2 - lat1)
    d_lon = math.radians(lon2 - lon1)
    
    a = (math.sin(d_lat / 2) ** 2 + 
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(d_lon / 2) ** 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c

def calculate_text_similarities(query_desc: str, corpus: list[str]) -> list[float]:
    if not corpus:
        return []
        
    if HAS_TRANSFORMERS:
        try:
            query_emb = sentence_model.encode([query_desc], convert_to_numpy=True)
            corpus_embs = sentence_model.encode(corpus, convert_to_numpy=True)
            
            # Cosine similarity
            dot_product = np.dot(query_emb, corpus_embs.T)
            norm_query = np.linalg.norm(query_emb)
            norm_corpus = np.linalg.norm(corpus_embs, axis=1)
            similarities = dot_product / (norm_query * norm_corpus)
            return list(similarities[0])
        except Exception as e:
            print(f"Transformers encoding failed, falling back to TF-IDF: {e}")
            
    # TF-IDF Fallback
    vectorizer = TfidfVectorizer().fit_transform([query_desc] + corpus)
    vectors = vectorizer.toarray()
    query_vector = vectors[0:1]
    corpus_vectors = vectors[1:]
    similarities = cosine_similarity(query_vector, corpus_vectors)
    return list(similarities[0])

def find_duplicate_works(db: Session, target_work: Work, threshold: float = 0.65, candidate_pool: list[Work] = None) -> list[dict]:
    # Narrow candidate list by district and category
    if candidate_pool is not None:
        candidates = [
            c for c in candidate_pool
            if c.id != target_work.id and c.district_code == target_work.district_code and c.category == target_work.category
        ]
    else:
        candidates = db.query(Work).filter(
            Work.id != target_work.id,
            Work.district_code == target_work.district_code,
            Work.category == target_work.category
        ).all()

    if not candidates:
        return []

    descriptions = [c.description for c in candidates]
    text_sims = calculate_text_similarities(target_work.description, descriptions)
    
    duplicates = []
    for idx, cand in enumerate(candidates):
        text_sim = text_sims[idx]
        
        # Calculate spatial distance
        dist_km = haversine_distance(
            target_work.latitude, target_work.longitude,
            cand.latitude, cand.longitude
        )
        
        # Geodistance score: decays exponentially. 1.0 at 0km, 0.5 at 2km, near 0 at 10km.
        geo_score = math.exp(-0.35 * dist_km) if dist_km is not None else 0.0

        # Cost similarity: 1 - relative difference in sanctioned amount
        amt_diff = abs(target_work.sanctioned_amount - cand.sanctioned_amount)
        max_amt = max(target_work.sanctioned_amount, cand.sanctioned_amount)
        cost_sim = 1.0 - (amt_diff / max_amt) if max_amt > 0 else 1.0

        # Temporal similarity: Check overlap in recommend / sanction dates
        time_sim = 0.8
        if target_work.sanction_date and cand.sanction_date:
            days_diff = abs((target_work.sanction_date - cand.sanction_date).days)
            time_sim = math.exp(-0.005 * days_diff) # Decays over a few months

        # Combined duplicate score (weighted average)
        # Weight details: Text=45%, Location=25%, Cost=20%, Time=10%
        duplicate_prob = (0.45 * text_sim) + (0.25 * geo_score) + (0.20 * cost_sim) + (0.10 * time_sim)
        duplicate_prob = min(1.0, max(0.0, duplicate_prob))

        if duplicate_prob >= threshold:
            duplicates.append({
                "work_id": cand.id,
                "description": cand.description,
                "district": cand.district.name if cand.district else cand.district_code,
                "distance_km": round(dist_km, 2) if dist_km < 999 else None,
                "sanctioned_amount": cand.sanctioned_amount,
                "text_similarity": round(float(text_sim), 2),
                "cost_similarity": round(float(cost_sim), 2),
                "duplicate_probability": round(float(duplicate_prob * 100), 1),
                "mp_name": cand.mp_name,
                "status": cand.status,
                "agency": cand.implementing_agency.name if cand.implementing_agency else None
            })

    # Sort by probability descending
    duplicates.sort(key=lambda x: x["duplicate_probability"], reverse=True)
    return duplicates
