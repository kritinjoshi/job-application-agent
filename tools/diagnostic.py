import os
import sys
import time
from dotenv import load_dotenv

def run_diagnostic():
    # 1. Setup
    # Move up one level from 'tools/' to project root
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    load_dotenv(os.path.join(base_dir, '.env'))
    sys.path.append(base_dir)
    
    from src.discovery.engine import JobFinder
    from src.integrations.google.sheets.spreadsheet import SheetsManager
    from src.integrations.google.docs.document import DocsManager
    from src.integrations.google.docs.docx_editor import DocxEditor
    from src.agents.crew import ResumeCrew
    
    # 2. Resourcing
    # Using the SAFE project-internal path confirmed by antigravity
    base_resume_path = os.path.join(base_dir, 'data', 'base_resume.docx')
    if not os.path.exists(base_resume_path):
        print(f"FAILED: Base resume not found at {base_resume_path}")
        return

    # 3. Initialize Architectures
    sheets = SheetsManager()
    docs = DocsManager()
    crew = ResumeCrew()
    finder = JobFinder(crew_agent=crew)
    
    print("\n--- DIAGNOSTIC: FINDING 1 HIGH-FIDELITY JOB ---")
    jobs = finder.find_jobs(pages=1)
    
    if not jobs:
        print("No jobs found for diagnostic!")
        return
        
    job = jobs[0]
    full_job_desc = finder.fetch_job_description(job['link'])
    job['description'] = full_job_desc
    
    print(f"\n--- DIAGNOSTIC: PROCESSING '{job['title']}' AT '{job['company']}' ---")
    print(f"Targeting Row: Next Available (Expected Row 12 after cleanup)")
    
    try:
        # 4. Extract Bullets (The part that failed this morning)
        raw_bullets = DocxEditor.extract_bullets(base_resume_path)
        print(f"SUCCESS: Extracted {len(raw_bullets)} bullets from base_resume.docx")
        
        # 5. Unified API Call (The 'Executive Strategist' Persona)
        assets = crew.generate_unified_job_assets(job['title'], job['company'], job['description'], raw_bullets)
        
        # 6. Metadata Verification
        metadata = assets.get("metadata", {})
        salary = metadata.get('salary', 'Not disclosed')
        seniority = metadata.get('seniority', 'Not disclosed')
        match_score = metadata.get('match_score', 'N/A')
        
        print(f"Diagnostic Salary: {salary}")
        print(f"Diagnostic Seniority: {seniority}")
        print(f"Diagnostic Match Score: {match_score}")
        
        # 7. Document Lifecycle
        safe_company = "".join([c for c in job['company'] if c.isalnum()])
        
        # Resume
        tailored_map = assets.get("resume_edits", [])
        resume_path = os.path.join(base_dir, 'data', f'DIAGNOSTIC_Resume_{safe_company}.docx')
        DocxEditor.apply_edits(base_resume_path, resume_path, tailored_map)
        doc_resume_url = docs.create_resume_doc_from_file(f"DIAGNOSTIC Resume | {job['company']}", resume_path, "resumes")
        
        # Cover Letter
        cl_text = assets.get("cover_letter")
        cl_path = os.path.join(base_dir, 'data', f'DIAGNOSTIC_CL_{safe_company}.docx')
        DocxEditor.create_cover_letter_docx(cl_text, cl_path)
        doc_cl_url = docs.create_resume_doc_from_file(f"DIAGNOSTIC CL | {job['company']}", cl_path, "cover_letters")
        
        # 8. Sheet Append
        from main import extract_logistics
        logistics = extract_logistics(full_job_desc, job.get('location', 'San Francisco'))
        
        sheets.append_job_row(
            job['title'], job['company'], job['link'], 
            doc_resume_url, doc_cl_url, 
            salary, seniority, match_score, logistics
        )
        
        print(f"\n[DIAGNOSTIC SUCCESS]: Entry added to spreadsheet.")
        print(f"Please check Row 12 in the Master Tracker.")
        
    except Exception as e:
        print(f"DIAGNOSTIC FAILED: {e}")

if __name__ == "__main__":
    run_diagnostic()
