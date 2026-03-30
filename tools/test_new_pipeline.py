import os
import sys
from dotenv import load_dotenv

def test_discovery_and_local_rank():
    # 1. Setup
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    load_dotenv(os.path.join(base_dir, '.env'))
    sys.path.append(base_dir)
    
    from src.scraper.job_finder import JobFinder
    from src.agents.crew import ResumeCrew
    
    crew = ResumeCrew()
    finder = JobFinder(crew)
    
    search_query = '"TPM" OR "Technical Program Manager" OR "Technical Program Management" OR "Manager of Technical Program Management"'
    
    print("\n--- TEST: PHASE 1 (Discovery of 100 Jobs) ---")
    # Using pages=2 for a faster test run (50 jobs)
    all_jobs, top_20 = finder.find_jobs(search_query, pages=2)
    
    print(f"\nTotal Discovered: {len(all_jobs)}")
    print("\n--- TEST: PHASE 2 (Local Semantic Top 20) ---")
    print(f"{'Rank':<5} | {'Heuristic':<10} | {'Company':<20} | {'Title'}")
    print("-" * 65)
    
    for i, j in enumerate(top_20):
        print(f"{i+1:<5} | {j['heuristic_score']:<10} | {j['company']:<20} | {j['title']}")

if __name__ == "__main__":
    test_discovery_and_local_rank()
