import requests
from bs4 import BeautifulSoup

def examine_linkedin_apply(url):
    headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"}
    print(f"Fetching {url}")
    resp = requests.get(url, headers=headers)
    if not resp.ok:
        print("Failed to fetch.")
        return
        
    soup = BeautifulSoup(resp.text, 'html.parser')
    
    a_tags = soup.find_all('a')
    button_tags = soup.find_all('button')
    
    print("--- Links ---")
    for tag in a_tags:
        text = tag.get_text(separator=' ', strip=True).upper()
        if 'APPLY' in text:
            href = tag.get('href', 'NO_HREF')
            print(f"Link text: '{text}' -> {href}")
            
    print("--- Buttons ---")
    for tag in button_tags:
        text = tag.get_text(separator=' ', strip=True).upper()
        if 'APPLY' in text:
            print(f"Button text: '{text}' -> {tag.attrs}")

if __name__ == "__main__":
    # Test with a real LinkedIn Jobs-Guest URL (which is what we actually fetch in `fetch_job_description`)
    # The URL needs to be a standard job posting URL. Our scraper gets them from search. Let's just search and pick one.
    search_url = "https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search?keywords=Staff%20Technical%20Program%20Manager&location=San%20Francisco%20Bay%20Area&start=0"
    headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"}
    resp = requests.get(search_url, headers=headers)
    soup = BeautifulSoup(resp.text, 'html.parser')
    card = soup.find('div', class_='base-card')
    if card:
        a_tag = card.find('a', class_='base-card__full-link')
        link = a_tag.get('href').split('?')[0] if a_tag else None
        if link:
            examine_linkedin_apply(link)
