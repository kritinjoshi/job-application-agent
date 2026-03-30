import os
import sys
import re

# Add project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

def test_rivian_salary():
    jd = """
    Staff Technical Program Manager, Autonomy - AI/ML at Rivian
    ...
    The salary range for this role is $167,400-$209,300 for San Francisco Bay Area based applicants.
    ...
    """
    
    print("\n--- Testing Salary Extraction Logic ---")
    sentences = re.split(r'(?<=[.!?])\s+|\n', jd)
    number_pattern = re.compile(r'[0-9]{1,3},[0-9]{3}')
    context_keywords = ["salary", "range", "pay", "compensation", "base", "benefits", "annually", "a year", "per year", "usd", "$"]
    
    potential_sentences = []
    for s in sentences:
        clean_s = s.strip()
        if number_pattern.search(clean_s):
            score = sum(1 for kw in context_keywords if kw in clean_s.lower())
            potential_sentences.append((score, clean_s))
            
    if potential_sentences:
        potential_sentences.sort(key=lambda x: x[0], reverse=True)
        print(f"Match Found: {potential_sentences[0][1]}")
    else:
        print("No Match Found!")

if __name__ == "__main__":
    test_rivian_salary()
