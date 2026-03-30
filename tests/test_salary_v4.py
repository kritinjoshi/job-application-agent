import re

def test_salary_picker():
    # JD Snippets
    google_str = "The US base salary range for this full-time position is $240,000-$334,000 + bonus + equity + benefits."
    tesla_str = "Base pay: 120,000 - 250,000 USD per year. Some other text."
    zoox_str = "Salary: $172,000 - $262,000 a year"
    noise_str = "We are a company of 150,000 employees. Founded in 19,000 BC."
    
    jd = "\n".join([google_str, tesla_str, zoox_str, noise_str])
    
    # Logic from crew.py
    salary_fallback = "Not disclosed"
    sentences = re.split(r'(?<=[.!?])\s+|\n', jd)
    number_pattern = re.compile(r'[0-9]{1,3},[0-9]{3}')
    context_keywords = ["salary", "range", "pay", "compensation", "base", "benefits", "annually", "a year", "per year", "usd", "$"]
    
    potential_sentences = []
    for s in sentences:
        clean_s = s.strip()
        if number_pattern.search(clean_s):
            score = sum(1 for kw in context_keywords if kw in clean_s.lower())
            potential_sentences.append((score, clean_s))
            print(f"Candidate: '{clean_s}' | Score: {score}")
    
    if potential_sentences:
        potential_sentences.sort(key=lambda x: x[0], reverse=True)
        for score, sent in potential_sentences:
            if 20 < len(sent) < 300:
                salary_fallback = sent
                break
    
    print(f"\nFINAL PICK: '{salary_fallback}'")

if __name__ == "__main__":
    test_salary_picker()
