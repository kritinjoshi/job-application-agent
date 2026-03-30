import requests
from bs4 import BeautifulSoup
import urllib.parse
keywords = '"TPM" OR "Technical Program Manager" OR "Technical Program Management" OR "Manager of Technical Program Management"'
url = f"https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search?keywords={urllib.parse.quote(keywords)}&location=San+Francisco+Bay+Area&start=0"
headers = {"User-Agent": "Mozilla/5.0"}
resp = requests.get(url, headers=headers)
soup = BeautifulSoup(resp.text, 'html.parser')
cards = soup.find_all('div', class_='base-search-card__info')
if not cards: cards = soup.find_all('div', class_='job-search-card')
for c in cards[:5]:
    title = c.find('h3', class_='base-search-card__title').text.strip()
    loc = c.find('span', class_='job-search-card__location')
    loc_text = loc.text.strip() if loc else 'Unknown'
    print(f"{title} -> Location: {loc_text}")
