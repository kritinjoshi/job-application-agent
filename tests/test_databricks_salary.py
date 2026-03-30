import re

def test_databricks_salary():
    jd = """
    Staff Technical Program Manager – GenAI Ops Capacity Planning at Databricks
    ...
    Local Pay Range

    $171,900—$240,675 USD
    ...
    """
    
    print("\n--- Testing Databricks Salary Extraction ---")
    # Current split logic
    sentences = re.split(r'(?<=[.!?])\s+|\n', jd)
    number_pattern = re.compile(r'[0-9]{1,3},[0-9]{3}')
    
    for i, s in enumerate(sentences):
        clean_s = s.strip()
        if not clean_s: continue
        
        match = number_pattern.search(clean_s)
        print(f"Segment {i} ['{clean_s}']: Match Found={bool(match)}, Length={len(clean_s)}")
        
        if match:
            if 20 < len(clean_s) < 300:
                print(f"  >>> PASSED FILTERS: {clean_s}")
            else:
                print(f"  >>> FAILED FILTERS (Length={len(clean_s)})")

if __name__ == "__main__":
    test_databricks_salary()
