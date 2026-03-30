# 🚀 Future Improvement: Semantic Sniper (v2.1)

This document serves as the implementation-ready blueprint for transitioning the Job Discovery & Ranking engine to a semantic embedding model.

## 🧠 Core Finding: Quota-Free Semantic Matching
- **Model**: `text-embedding-004` (Gemini Embedding 1).
- **Quota**: **30,000 Requests/Day** in the free tier—effectively "infinite" for our daily 7:00 AM PST run.
- **Benefit**: We can rank 500+ jobs mathematically without hitting the Gemini 2.5 Flash "Quota Wall," which has significantly tighter limits.

---

## 🏗️ Technical Blueprint

### 1. Vectorization Layer (`src/agents/crew.py`)
Add a highly efficient `get_embedding(text)` method to the `ResumeCrew` class to generate numerical vector representations.

### 2. Semantic Ranker (`src/intelligence/ranker.py`)
Implement a **Hybrid Ranking Engine**:
1.  **Semantic Score**: Calculate the **Cosine Similarity** between the `base_resume` vector and the `job_snippet` vector.
2.  **Logic Score**: Maintain the existing **Top-Tier + Seniority Heuristics**.
3.  **Unified Score**: `(Heuristic_Score * 0.3) + (Semantic_Similarity * 0.7)`. This ensures that a "Staff TPM" role at "Roblox" is mathematically undeniable.

### 3. Native Integration (`main.py`)
Transition the "Elite 10 Selection" from an AI Batch call to a high-speed mathematical sort:
```python
# Future Logic Swap:
# elite_targets = finder.rank_top_10_with_ai(elite_top_20)
elite_targets = finder.rank_jobs_semantically(elite_top_20, resume_text)
```

---

## 🛠️ Implementation Steps (When Ready)
1.  **Pip Dependencies**: `numpy`, `scikit-learn` (for `cosine_similarity`).
2.  **API Class**: Build the `embedContent` POST request in `crew.py`.
3.  **Discovery Layer**: Refactor the search sorting to handle multi-stage ranking (Heuristic -> Semantic -> Final Elite).

**Current Status**: 🟦 **DRAFT** | Ready for execution upon request.
