import os
import sys

# Add project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

from src.discovery.engine import JobFinder
from src.agents.crew import ResumeCrew

def verify_sniper_search():
    crew = ResumeCrew()
    finder = JobFinder(crew)
    
    print("\n--- Verifying Sniper Search: Roblox ---")
    # Simulate Pass 2 for Roblox specifically using the new strict query
    company = "Roblox"
    sniper_query = f'"{company}" "Technical Program Manager"'
    
    # We use find_jobs directly with the fixed query
    roblox_jobs, _ = finder.find_jobs(
        sniper_query, 
        "San Francisco Bay Area", 
        pages=2, 
        time_filter="r2592000" # 30 Days
    )
    
    found = False
    for j in roblox_jobs:
        # Check company match as per main.py logic
        if company.lower() in j['company'].lower():
            print(f"Discovered: {j['title']} at {j['company']} (Posted: {j['posted_time']})")
            if "4359121996" in j['link'] or "Engine" in j['title']:
                found = True
                print(f"  >>> SUCCESS: Found Target Roblox Role via Sniper Search!")
            
    if not found:
        print("  >>> FAILED: Target Roblox role not found in first 2 pages.")

if __name__ == "__main__":
    verify_sniper_search()
