import requests
from bs4 import BeautifulSoup
import json
from textwrap import dedent
from src.utils.local_ranker import LocalRanker

class JobFinder:
    def __init__(self, crew_agent, resume_text=None):
        self.crew = crew_agent
        self.ranker = LocalRanker(resume_text)
        
    def fetch_job_description(self, url):
        try:
            if 'linkedin.com' in url:
                headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"}
                resp = requests.get(url, headers=headers, timeout=10)
                if resp.status_code == 200:
                    soup = BeautifulSoup(resp.text, 'html.parser')
                    div = soup.find('div', class_='show-more-less-html__markup')
                    if div:
                        return div.get_text(separator='\n', strip=True)
                    desc = soup.find('div', class_='description__text')
                    if desc:
                        return desc.get_text(separator='\n', strip=True)
        except Exception as e:
            print(f"Extraction error fetching {url}: {e}")
            pass
        return "Generic TPM description. The automated text scraper engine encountered errors bypassing the security headers for this precise explicit endpoint link!"

    def find_jobs(self, keywords="Technical Program Manager", location="San Francisco Bay Area", ignore_list=None, pages=12, company_name=None, time_filter=None):
        search_label = f"[{company_name}] " if company_name else ""
        print(f"\n{search_label}[Heuristic Discovery] Scanning LinkedIn for '{keywords}' (Pages: {pages})...")
        
        query = f'"{company_name}" {keywords}' if company_name else keywords
        jobs = []
        # Scraping multiple pages of generic target structures to ensure volume for AI ranking
        for p in range(pages):
            start = p * 25
            url = f"https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search?keywords={requests.utils.quote(query)}&location={requests.utils.quote(location)}&start={start}"
            if time_filter:
                url += f"&f_TPR={time_filter}"
            
            headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0"}
            
            try:
                resp = requests.get(url, headers=headers)
                if resp.status_code == 200:
                    soup = BeautifulSoup(resp.text, 'html.parser')
                    cards = soup.find_all('div', class_='base-search-card__info')
                    if not cards:
                        cards = soup.find_all('div', class_='job-search-card')
                        
                    for c in cards:
                        try:
                            title_tag = c.find('h3', class_='base-search-card__title')
                            title = title_tag.text.strip() if title_tag else "Unknown Role"
                            
                            company_tag = c.find('h4', class_='base-search-card__subtitle')
                            company = company_tag.text.strip() if company_tag else "Unknown Company"
                            
                            time_tag = c.find('time')
                            posted_time = time_tag.text.strip() if time_tag else "1 day ago"
                            
                            # Recruiting Status / Benefits extraction
                            benefits_tag = c.find('span', class_='result-benefits__text')
                            if not benefits_tag:
                                benefits_tag = c.find('span', class_='job-search-card__benefits')
                            
                            raw_benefits = benefits_tag.text.strip() if benefits_tag else "Standard"
                            benefits = LocalRanker.standardize_status(raw_benefits)
                            
                            num_match = __import__('re').search(r'\d+', posted_time)
                            num = int(num_match.group()) if num_match else 1
                            t_str = posted_time.lower()
                            
                            if 'hour' in t_str or 'minute' in t_str: days = num / 24.0
                            elif 'day' in t_str: days = float(num)
                            elif 'week' in t_str: days = num * 7.0
                            elif 'month' in t_str: days = num * 30.0
                            else: days = float(num)
                            
                            if 'reposted' in t_str:
                                days += 30.0
                                
                            loc = c.find('span', class_='job-search-card__location')
                            loc_text = loc.text.strip() if loc else 'San Francisco Bay Area'
                            
                            parent_card = c.find_parent('div', class_='base-card') or c.find_parent('div', class_='job-search-card')
                            a_tag = parent_card.find('a', class_='base-card__full-link') if parent_card else None
                            link = a_tag.get('href', "No Link").split('?')[0] if a_tag else "No Link"
                            
                            cache_key = f"{company.lower().strip()}_{title.lower().strip()}"
                            if ignore_list and (link in ignore_list or cache_key in ignore_list):
                                continue
                                
                            jobs.append({
                                "title": title, 
                                "company": company, 
                                "link": link, 
                                "posted_time": posted_time, 
                                "normalized_days_old": round(days, 2), 
                                "city": loc_text,
                                "recruiting_status": benefits,
                                "days_ago": int(days) if days < 30 else "30+"
                            })
                        except Exception:
                            continue
                else:
                    if resp.status_code == 429:
                        print(f"Rate limited by LinkedIn on page {p}. Stopping discovery.")
                        break
            except Exception as e:
                print(f"Scrape API payload failure on sequence page {start}: {e}")
                
        # Deduplication logically against active pull array bounds
        unique_jobs = []
        seen = set()
        for j in jobs:
            # Slightly relaxed filter for the Jobs Board pool to ensure 100+ volume
            if j['normalized_days_old'] > 30.0:
                continue
                
            key = f"{j['title']}_{j['company']}"
            if key not in seen:
                seen.add(key)
                unique_jobs.append(j)
                
        print(f"Successfully discovered {len(unique_jobs)} raw unique prospects for 'Jobs Board'.")
        
        # Apply Statistical Semantic Ranking to pick the Top 20 for AI review
        print("\n--- Phase 2: Statistical Semantic Pre-Ranking (Tier-1.5) ---")
        scored_jobs = []
        for j in unique_jobs:
            score = self.ranker.calculate_score(j['title'], j.get('city', ''), jd_full=j['title']) 
            j['heuristic_score'] = score
            scored_jobs.append(j)
            
        scored_jobs.sort(key=lambda x: (x['heuristic_score'], -x['normalized_days_old']), reverse=True)
        top_20 = scored_jobs[:20]
        
        print(f"Top 20 'Elite' prospects isolated locally for Tier-2 AI ranking.")
        return unique_jobs, top_20

    def rank_top_10_with_ai(self, candidates):
        if not candidates:
            return []
            
        print("Agent [Tier-2]: Selecting final Top 10 Elite matches using Gemini 2.5 Flash Batching...")
        
        prompt = dedent(f"""\
            You are an Elite Executive Talent Architect ranking the absolute Top 10 job opportunities for Mrunal Shirude (Meta L6 TPM).
            I will provide a JSON list of 20 high-quality roles pre-filtered locally.
            
            Your Task:
            1. Rank exactly the Top 10 by 'Role-of-a-Lifetime' quality.
            2. Priority: Staff, Sr Staff, Director roles with AI/Hardware/Payments complexity.
            3. Discard: Any role that you judge to be a definitive downgrade (L5/Junior) despite the keywords.
            
            Return ONLY a raw JSON array of the top 10 jobs. Return NOTHING ELSE.
            
            # Candidates to Review:
            {json.dumps(candidates)}
            """)
        
        text = self.crew.get_ai_response(prompt)
        
        if not text:
            print("Agent [Tier-2]: AI selection failed (all models). Falling back to local heuristic top 10.")
            return candidates[:10]
            
        try:
            clean_text = text.replace('```json', '').replace('```', '').strip()
            return json.loads(clean_text)
        except Exception as e:
            print(f"Agent [Tier-2]: AI parsing error: {e}")
            return candidates[:10]
