import os
import sys
import time
import subprocess
from dotenv import load_dotenv

base_dir = os.path.dirname(__file__)
load_dotenv(os.path.join(base_dir, '.env'))

from src.discovery.engine import JobFinder
from src.integrations.google.sheets.spreadsheet import SheetsManager
from src.integrations.google.docs.document import DocsManager
from src.integrations.google.docs.docx_editor import DocxEditor
from src.agents.crew import ResumeCrew
from src.intelligence.ranker import LocalRanker

def trigger_mac_message():
    import datetime
    
    recipients_raw = os.environ.get('MSG_RECIPIENTS')
    if not recipients_raw:
        print("\n[CRON Message Notification Blocked]")
        return

    today = datetime.datetime.now().strftime("%Y-%m-%d")
    short_url = "https://tinyurl.com/job-app-agent-tracker"
    
    message = f"Hi, This is your job application agent. Your top 10 job applications for {today} are ready. \n\nMaster Tracker: {short_url}"
    
    recipients = [r.strip() for r in recipients_raw.split(',') if r.strip()]
    
    for phone in recipients:
        script = f'''
        tell application "Messages"
            set targetBuddy to buddy "{phone}"
            send "{message}" to targetBuddy
        end tell
        '''
        try:
            subprocess.run(['osascript', '-e', script])
            print(f"[CRON Notification] Successfully dispatched iMessage to '{phone}'.")
        except Exception as e:
            print(f"[CRON Notification] Failed to trigger macOS iMessage: {e}")

def extract_logistics(desc, location_city):
    desc_lower = desc.lower()
    if 'remote' in desc_lower and 'hybrid' not in desc_lower:
        mode = 'Fully Remote'
    elif 'hybrid' in desc_lower:
        mode = 'Hybrid'
    elif 'onsite' in desc_lower or 'on-site' in desc_lower or 'in office' in desc_lower or 'in-office' in desc_lower:
        mode = 'Fully Onsite'
    else:
        # Default fallback
        city_lower = location_city.lower()
        if 'remote' in city_lower: mode = 'Fully Remote'
        elif 'hybrid' in city_lower: mode = 'Hybrid'
        else: mode = 'Onsite/Unspecified'
            
    loc_clean = location_city.split('(')[0].strip()
    loc_clean = loc_clean if loc_clean else 'San Francisco Bay Area'
    return f"{loc_clean} ({mode})"

def main():
    print("Starting Multi-Agent Native DOCX & L6 Evaluator Orchestration System...")
    
    creds_path = os.path.join(base_dir, 'credentials.json')
    if not os.path.exists(creds_path):
        print(f"Error: Missing {creds_path}.")
        return
        
    if not ('GEMINI_API_KEY' in os.environ or 'OPENAI_API_KEY' in os.environ):
        print("Error: Missing Language Model API Key.")
        return

    # Safe project-internal path for cron reliability (avoids MacOS Desktop permission locks)
    base_resume_path = os.path.abspath(os.path.join(base_dir, 'data', 'base_resume.docx'))
    if not os.path.exists(base_resume_path):
        # Fallback to Desktop just in case, but warn
        alt_path = "/Users/mrunalshirude/Desktop/DeepMind Mrunal Shirude_Resume_IC.docx"
        if os.path.exists(alt_path):
            base_resume_path = alt_path
        else:
            print(f"Error: Base DOCX resume not found at {base_resume_path}")
            return

    print("\nInitializing Google APIs and Agent Architectures...")
    sheets = SheetsManager()
    docs = DocsManager()
    crew = ResumeCrew()

    print("\n[Orchestrator] Retrieving Master Tracker cache explicitly for logical automated Deduplication...")
    historic_signatures = sheets.get_existing_signatures()
    print(f"Isolated {len(historic_signatures)} historically parsed signature bounds preventing loop redundancies!")

    print("\n[Orchestrator] Launching automated Discovery & Multi-Tier selection phase...")
    resume_text = " ".join(DocxEditor.extract_bullets(base_resume_path))
    finder = JobFinder(crew, resume_text=resume_text)
    
    top_tier = [
        "OpenAI", "Anthropic", "NVIDIA", "Groq", "Cohere", "Perplexity",
        "Meta", "Microsoft", "Google", "Apple", "Netflix", "Amazon",
        "Roblox", "Tesla", "SpaceX", "Stripe", "Rippling", "Databricks", "Snowflake",
        "Uber", "Airbnb", "Palantir", "DoorDash"
    ]
    
    search_query = '"TPM" OR "Technical Program Manager" OR "Senior Technical Program Manager" OR "Technical Program Management" OR "Director of Technical Program Management" OR "Head of Technical Program Management" OR "Manager of Technical Program Management"'
    
    # --- Pass 1: Broad Discovery (Last 7 Days) ---
    print("\n--- Pass 1: Broad Discovery (Last 7 Days) ---")
    # Using r604800 for 7 days
    all_discovered_jobs, _ = finder.find_jobs(search_query, "San Francisco Bay Area", ignore_list=historic_signatures, pages=15, time_filter="r604800")
    
    # --- Pass 2: Top Tier Sniper Search (Last 30 Days) ---
    print("\n--- Pass 2: Top Tier Sniper Search (Last 30 Days) ---")
    seen_links = {j['link'] for j in all_discovered_jobs}
    
    for company in top_tier:
        # Sniper search targets the specific company STRONGLY
        # We avoid complex OR logic here to prevent generic TPM roles from flooding the sniper results
        sniper_query = f'"{company}" "Technical Program Manager"'
        tier_jobs, _ = finder.find_jobs(sniper_query, "San Francisco Bay Area", ignore_list=historic_signatures, pages=2, time_filter="r2592000")
        
        for tj in tier_jobs:
            if tj['link'] not in seen_links:
                # Double-check company match in case LinkedIn's guest search is loose
                if company.lower() in tj['company'].lower():
                    all_discovered_jobs.append(tj)
                    seen_links.add(tj['link'])

    # Apply Statistical Semantic Ranking with newly integrated Top-Tier + Duration factors
    print("\n--- Phase 3: Statistical Semantic Pre-Ranking (Tier-1.5) ---")
    for j in all_discovered_jobs:
        score = finder.ranker.calculate_score(
            j['title'], 
            j.get('city', ''), 
            jd_full=j['title'], 
            days_old=j.get('normalized_days_old', 0), 
            company=j.get('company', '')
        ) 
        j['heuristic_score'] = score
        
    all_discovered_jobs.sort(key=lambda x: (x['heuristic_score'], -x['normalized_days_old']), reverse=True)
    elite_top_20 = all_discovered_jobs[:20]
    
    # Phase 2: Update 'Jobs Board' with all discoveries (Target 100+)
    if all_discovered_jobs:
        print(f"\n[Jobs Board] Populating {len(all_discovered_jobs)} raw prospects with canonical standardization...")
        
        jobs_matrix = []
        for j in all_discovered_jobs:
            local_score = j.get('heuristic_score', 0)
            level = LocalRanker.evaluate_level(j['title'], "")
            
            # Format Job URL as a HYPERLINK formula for the word "LINK"
            job_url = j.get('link', '')
            job_hyperlink = f'=HYPERLINK("{job_url}", "LINK")' if "http" in job_url else "No Link"
            
            jobs_matrix.append([
                j['title'], 
                j['company'], 
                job_hyperlink, 
                j.get('posted_time', 'N/A'), 
                j.get('city', 'San Francisco Bay Area'),
                j.get('recruiting_status', 'Standard'),
                j.get('days_ago', 0),
                local_score,
                level
            ])
            
        sheets.overwrite_jobs_board(jobs_matrix)

    # Phase 3: AI Selection (1 Batch Call) for Elite 10
    elite_targets = finder.rank_top_10_with_ai(elite_top_20)
    
    if not elite_targets:
        print("\n[Orchestrator] No viable unique targets isolated today. Batch complete.")
        return
    else:
        print(f"\n[Orchestrator] AI Batch Ranker approved {len(elite_targets)} Elite targets for today's batch.")

        for i, job in enumerate(elite_targets):
            print(f"\n==============================================")
            print(f"Iterating Pipeline Job [{i+1}/{len(elite_targets)}]: {job.get('title')} at {job.get('company')}")
            print(f"==============================================")
            
            full_job_desc = finder.fetch_job_description(job['link'])
            job['description'] = full_job_desc
            
            print(f"Tailoring specifically FAANG-focused strictly 1-page DOCX format hooks structurally...")
            
            doc_resume_url = "N/A - System Error"
            doc_cl_url = "N/A - System Error"
            
            # Format variables correctly
            safe_company_name = "".join([c for c in job['company'] if c.isalpha() or c.isdigit()]).rstrip()
            role_snippet = "".join(filter(str.isalnum, job['title']))[:10]
            
            try:
                raw_bullets = DocxEditor.extract_bullets(base_resume_path)
                
                # Pre-calculate local heuristics to pass as fallbacks if API fails
                local_sc_engine = LocalRanker(resume_text=resume_text)
                local_score = job.get('heuristic_score', local_sc_engine.calculate_score(job['title'], job.get('city', '')))
                local_level = LocalRanker.evaluate_level(job['title'], "")
                
                # Simple salary hint for fallback
                salary_hint = "Not disclosed"
                desc = job.get('description', '')
                for sentence in desc.replace('\n', '. ').split('. '):
                    if any(char.isdigit() for char in sentence) and (',' in sentence or '.' in sentence):
                        if any(k in sentence.lower() for k in ['salary', 'range', 'pay', '$', 'usd']):
                            salary_hint = sentence.strip()
                            break
                
                # --- UNIFIED API CALL ---
                assets = crew.generate_unified_job_assets(
                    job['title'], 
                    job['company'], 
                    job['description'], 
                    raw_bullets,
                    local_score=local_score,
                    local_level=local_level
                )
                
                # --- 1. RESUME ---
                tailored_map = assets.get("resume_edits", [])
                if tailored_map:
                    resume_path = os.path.join(base_dir, 'data', f'Resume_{safe_company_name}_{role_snippet}.docx')
                    DocxEditor.apply_edits(base_resume_path, resume_path, tailored_map)
                    
                    doc_title = f"Resume | {job['company']} | {job['title']} (Perfectly Trimmed)"
                    doc_resume_url = docs.create_resume_doc_from_file(title=doc_title, file_path=resume_path, folder_type="resumes")
                
                # --- 2. COVER LETTER ---
                cl_text = assets.get("cover_letter")
                if cl_text:
                    cl_path = os.path.join(base_dir, 'data', f'CoverLetter_{safe_company_name}_{role_snippet}.docx')
                    DocxEditor.create_cover_letter_docx(cl_text, cl_path)
                    
                    cl_title = f"Cover Letter | {job['company']} | {job['title']}"
                    doc_cl_url = docs.create_resume_doc_from_file(title=cl_title, file_path=cl_path, folder_type="cover_letters")
                    
                # --- 3. METADATA ---
                metadata = assets.get("metadata", {})
                salary = metadata.get('salary', 'Not disclosed')
                seniority = metadata.get('seniority', 'L6 (Probable)')
                match_score = metadata.get('match_score', 85)
                    
            except Exception as e:
                err_msg = str(e)
                print(f"Agent logic gracefully bypassing explicit Drive Builders natively due to API/JSON Exceptions: {err_msg}")
                # Use a specific error tag so we can tell if it was Quota or something else
                if "429" in err_msg or "QUOTA" in err_msg.upper() or "RESOURCE_EXHAUSTED" in err_msg:
                    salary, seniority, match_score = salary_hint, local_level, local_score
                else:
                    salary, seniority, match_score = salary_hint, local_level, local_score

            print(f"Agent Logic: Extracted Base Compensation Profile -> {salary}")
            print(f"Agent Logic: Evaluated Architectural Level -> {seniority}")
            print(f"Agent Logic: Calculated Target Match Score -> {match_score}")
            
            city_tag = job.get('city', 'San Francisco Bay Area')
            logistics_val = extract_logistics(full_job_desc, city_tag)
            
            try:
                print(f"Appending Google Native URL schemas seamlessly down into backend Sheets Analytics DB... mapped natively via {logistics_val}")
                sheets.append_job_row(job['title'], job['company'], job['link'], doc_resume_url, doc_cl_url, salary, seniority, match_score, logistics_val)
            except Exception as e:
                print(f"Failed to post strictly constrained structural row to tracker explicitly. Ex: {e}")
                pass
                
            print("Sleeping 35 seconds to bypass Gemini 2.5 Flash Free Tier TPM/RPM limits... 💤")
            time.sleep(35)
        
        print("\nBatch generation orchestrator finished! All uniquely constrained jobs cleanly explicitly appended safely into the analytics layer.")
    
    # TRIGGER MAC COMPLETION MESSAGE!
    trigger_mac_message()

    from src.monitoring.telemetry_manager import TelemetryManager
    stats = TelemetryManager.get_summary_stats()
    print("\n" + stats)

if __name__ == "__main__":
    main()
