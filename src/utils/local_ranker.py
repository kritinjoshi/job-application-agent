import re
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

class SemanticRanker:
    """
    Advanced statistical engine using TF-IDF and Cosine Similarity.
    Allows for deep 'text vs text' semantic evaluation without API costs.
    """
    def __init__(self, resume_text):
        self.resume_text = resume_text
        self.vectorizer = TfidfVectorizer(stop_words='english')
        # Pre-fit on resume to establish vocabulary
        self.resume_vector = self.vectorizer.fit_transform([resume_text])

    def get_match_score(self, job_description):
        """
        Calculates the 0-1.0 cosine similarity between the resume and JD.
        """
        if not job_description or len(job_description) < 50:
            return 0.0
            
        try:
            # Transform JD using the existing vocabulary from the resume
            jd_vector = self.vectorizer.transform([job_description])
            similarity = cosine_similarity(self.resume_vector, jd_vector)[0][0]
            return float(similarity)
        except Exception as e:
            print(f"[SemanticRanker] Error calculating similarity: {e}")
            return 0.0

class LocalRanker:
    """
    Zero-cost local semantic scorer for high-fidelity job filtering.
    Uses a weighted keyword overlap (TF-IDF Lite) and Hybrid Seniority matching.
    Can be upgraded to 'Semantic Mode' if a resume_text is provided.
    """
    
    # Elite Keywords derived from Mrunal's Meta L6/L7 Profile
    ELITE_KEYWORDS = {
        # Core TPM & Leadership (High Weight: 5)
        'technical program manager': 5, 'tpm': 5, 'strategic planning': 5, 'portfolio': 5,
        'cross-functional': 5, 'xfn': 5, 'roadmap': 4, 'stakeholder': 4,
        
        # AI/ML/Data (High Weight: 5)
        'ai': 5, 'machine learning': 5, 'ml': 5, 'data platform': 5, 'analytics': 5,
        'annotation': 5, 'dataset': 5, 'model training': 5, 'fine tuning': 5,
        
        # Product/Domain (Medium Weight: 3)
        'ar/vr': 3, 'metaverse': 3, 'hardware': 3, 'reality labs': 3, 'quest': 3,
        'payments': 3, 'paypal': 3, 'fintech': 3, 'infrastructure': 3, 'cloud': 3,
        
        # Profile Match (Mrunal Specific)
        'meta': 10,
        
        # Seniority Signals (Weighted per the Hybrid Rubric)
        'staff': 15, 'principal': 15, 'director': 20, 'head of': 20, 'vp': 20, 'lead': 5, 'senior': 2
    }

    TOP_TIER_COMPANIES = [
        "OpenAI", "Anthropic", "NVIDIA", "Groq", "Cohere", "Perplexity",
        "Meta", "Microsoft", "Google", "Apple", "Netflix", "Amazon",
        "Roblox", "Tesla", "SpaceX", "Stripe", "Rippling", "Databricks", "Snowflake",
        "Uber", "Airbnb", "Palantir", "DoorDash"
    ]

    def __init__(self, resume_text=None):
        self.semantic_engine = SemanticRanker(resume_text) if resume_text else None

    def calculate_score(self, title, snippet, location="", jd_full="", days_old=0, company=""):
        """
        Calculates a statistical match score (0-100) for a job prospect.
        Hybrid Mode: Uses 75% Semantic weighting if JD/Resume available, 
        else falls back to 100% Heuristic logic.
        
        Refinement: 
        - +15 point boost for Top Tier Firms.
        - -1 point penalty for every 5 days since posting (Recency Prioritization).
        """
        title_lower = title.lower()
        snippet_lower = snippet.lower()
        text = f"{title_lower} {snippet_lower} {location.lower()}"
        
        heuristic_raw = 0
        
        # 1. Keyword Overlap (The 'Boost' logic)
        for kw, weight in self.ELITE_KEYWORDS.items():
            if kw in text:
                heuristic_raw += weight
                
        # 2. Seniority Multipliers
        seniority_boost = 1.0
        if any(x in title_lower for x in ['staff', 'principal', 'l7', 'l6', 'director', 'vp', 'head of', 'lead']):
            seniority_boost = 1.8 # Increased multiplier for elite roles
        elif 'senior' in title_lower:
            if any(x in text for x in ['$2', '$3', '200k', '300k', '400k']):
                seniority_boost = 1.4
            else:
                seniority_boost = 1.0

        # --- TIER 1.5: SEMANTIC UPGRADE ---
        if self.semantic_engine and (jd_full or snippet):
            semantic_raw = self.semantic_engine.get_match_score(jd_full or snippet)
            semantic_scaled = semantic_raw * 100
            final_score = (semantic_scaled * 0.75) + (min(heuristic_raw, 25) * seniority_boost)
        else:
            final_score = heuristic_raw * seniority_boost

        # --- TIER 1.6: ELITE OVERRIDES ---
        # A. Top Tier Firm sniper boost
        if any(tt.lower() in company.lower() for tt in self.TOP_TIER_COMPANIES):
            final_score += 15
            
        # B. Duration penalty (Recency Prioritization)
        # -1 point for every 5 days (0.2 points per day)
        duration_penalty = days_old * 0.2
        final_score -= duration_penalty

        # Normalize to a 0-100 scale (capped)
        normalized = min(max(int(final_score), 0), 100)
        
        return normalized

    @staticmethod
    def evaluate_level(title, snippet=""):
        """
        Local version of our Hybrid Seniority Rubric.
        """
        title = title.lower()
        snippet = snippet.lower()
        text = f"{title} {snippet}"
        
        if any(x in title for x in ['director', 'vp', 'head of', 'l8']): return "L8"
        if any(x in title for x in ['principal', 'senior staff', 'l7']): return "L7"
        if any(x in title for x in ['staff', 'manager', 'l6']): return "L6"
        
        if 'senior' in title:
            if any(x in text for x in ['$2', '$3', '200k', '300k', '400k']):
                return "L6" # High-pay upgrade
            return "L5"
            
        return "L5/L6"

    @staticmethod
    def standardize_status(raw_text):
        """
        Map LinkedIn raw snippet strings to canonical job statuses.
        """
        if not raw_text or raw_text == "Standard":
            return "Standard"
            
        raw_text = raw_text.lower()
        
        if any(x in raw_text for x in ['actively recruiting', 'actively hiring', 'hiring now']):
            return "Actively Hiring"
        if any(x in raw_text for x in ['early applicant', 'be an early applicant']):
            return "Early Applicant"
        if any(x in raw_text for x in ['viewed', 'reposted']):
            return "Standard"
        if any(x in raw_text for x in ['directly from employer', 'hiring team']):
            return "Direct Apply"
            
        return "Standard"
