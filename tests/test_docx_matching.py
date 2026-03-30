import difflib

def fuzzy_match(s1, s2, threshold=0.8):
    # Normalize
    n1 = " ".join(s1.lower().split())
    n2 = " ".join(s2.lower().split())
    
    if n1 == n2:
        return True
        
    similarity = difflib.SequenceMatcher(None, n1, n2).ratio()
    return similarity >= threshold

def test_matching():
    # Original bullet from DOCX
    bullet_docx = "Led a cross-functional team of 150+ engineers to deliver Meta's first Metaverse platform, increasing user engagement by 45%."
    
    # AI returned "old" bullet (slightly modified or with extra spaces)
    bullet_ai_old = "Led a cross-functional team of 150+ engineers to deliver Meta's first Metaverse platform, increasing user engagement by 45% ."
    
    print(f"Testing fuzzy match:")
    print(f"Original: '{bullet_docx}'")
    print(f"AI Old:   '{bullet_ai_old}'")
    print(f"Match Results: {fuzzy_match(bullet_docx, bullet_ai_old)}")

if __name__ == "__main__":
    test_matching()
