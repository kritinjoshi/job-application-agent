import os
import sys

# Add project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.intelligence.ranker import LocalRanker
from src.integrations.google.docs.docx_editor import DocxEditor

def test_engine():
    # 1. Load Resume
    base_dir = os.path.join(os.path.dirname(__file__), '..')
    resume_path = os.path.join(base_dir, 'data', 'base_resume.docx')
    if not os.path.exists(resume_path):
        print(f"Error: Resume not found at {resume_path}")
        return
        
    resume_text = " ".join(DocxEditor.extract_bullets(resume_path))
    print(f"Loaded Resume ({len(resume_text)} chars)")
    
    # 2. Setup Ranker
    ranker = LocalRanker(resume_text=resume_text)
    
    # 3. Define Test Cases
    tests = [
        {
            "name": "High Match (AI Infra TPM)",
            "title": "Principal Technical Program Manager, AI Infrastructure",
            "snippet": "Lead TPU and GPU hardware acceleration projects. Deep ML infrastructure experience required at Meta or Google scale. XFN leadership."
        },
        {
            "name": "Mid Match (Generic Manager)",
            "title": "Operations Manager",
            "snippet": "Manage day to day operations for a logistics team. Focus on people management and roadmap planning."
        },
        {
            "name": "Low Match (Frontend Dev)",
            "title": "Junior Frontend Web Developer",
            "snippet": "Build UI components using React, CSS, and HTML. No management experience needed. Entry level role."
        }
    ]
    
    print("\n--- Semantic Scoring Results ---")
    for t in tests:
        score = ranker.calculate_score(t['title'], t['snippet'], location="San Francisco", jd_full=t['snippet'])
        print(f"[{t['name']}] Score: {score}")
        
    print("\nDone.")

if __name__ == "__main__":
    test_engine()
