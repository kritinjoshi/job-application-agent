import os
import json
import requests
import re
from src.monitoring.telemetry_manager import TelemetryManager
from textwrap import dedent

class ResumeCrew:
    def __init__(self):
        self.api_key = os.environ.get('GEMINI_API_KEY')
        self.model = "gemini-2.5-flash"
        self.url_template = "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key=" + self.api_key

    def get_ai_response(self, prompt, model_override=None):
        """
        Sends a prompt to the Gemini API with automatic fallback for 429 errors.
        """
        models_to_try = [model_override or self.model, "gemini-1.5-flash-latest", "gemini-2.0-flash"]
        
        for model in models_to_try:
            try:
                url = self.url_template.format(model=model)
                payload = {"contents": [{"parts": [{"text": prompt}]}]}
                
                resp = requests.post(url, json=payload, timeout=60)
                
                if resp.status_code == 200:
                    data = resp.json()
                    text = data["candidates"][0]["content"]["parts"][0]["text"]
                    # Log success (dummy tokens for now)
                    TelemetryManager.log_request(model, 1000, 500, 200) 
                    return text
                elif resp.status_code == 429:
                    print(f"Agent [Quota]: {model} exhausted (429). Falling back...")
                    TelemetryManager.log_request(model, 0, 0, 429)
                    continue
                else:
                    print(f"Agent [Error]: {model} failed with {resp.status_code}")
                    TelemetryManager.log_request(model, 0, 0, resp.status_code)
            except Exception as e:
                print(f"Agent [Exception]: {model} connection error: {e}")
                
        return None

    def generate_unified_job_assets(self, job_title, company, job_description, raw_bullets, local_score=0, local_level="L6"):
        """
        Agent [Unified Mode]: Consolidates AI payload generation for Cover Letter, Resume edits, & Metadata.
        """
        print(f"Agent [Unified Mode]: Consolidating AI payload for '{company}' targeting '{job_title}'...")
        
        # 1. Salary Sentence Picker (Local Source of Truth)
        salary_fallback = "Not disclosed"
        sentences = re.split(r'(?<=[.!?])\s+|\n', job_description)
        # Handles 167,400, 181K, and non-standard dashes like —
        number_pattern = re.compile(r'[0-9]{1,3}[,.]?[0-9]{0,3}k|[0-9]{1,3},[0-9]{3}', re.IGNORECASE)
        context_keywords = ["salary", "range", "pay", "compensation", "base", "benefits", "annually", "a year", "per year", "usd", "$"]
        
        potential_sentences = []
        for s in sentences:
            clean_s = s.strip()
            # If it has a number and a currency symbol / keyword
            if number_pattern.search(clean_s):
                score = sum(1 for kw in context_keywords if kw in clean_s.lower())
                potential_sentences.append((score, clean_s))
        
        if potential_sentences:
            potential_sentences.sort(key=lambda x: x[0], reverse=True)
            for score, sent in potential_sentences:
                # Relaxed length for currency-heavy strings (catch short blocks like $170k-$240k)
                min_len = 10 if '$' in sent or 'usd' in sent.lower() else 20
                if min_len < len(sent) < 300:
                    salary_fallback = sent
                    break
                    
        # 2. Prompt construction... (Omitted for brevity, using existing template)
        prompt = dedent(f"""\
            You are an elite Silicon Valley Talent Architect & Executive TPM Strategist.
            Consolidate your expert evaluation of the target role into a single JSON payload.
            
            Target Company: {company}
            Target Role: {job_title}
            Identified Salary Context: {salary_fallback}
            
            # Asset 1: Metadata (Seniority & Match)
            Derive the seniority (L5-L8) using the Salary Context AND Job Title.
            Rubric:
            - L8: Title 'Director', 'L8', or 'VP'.
            - L7: Title 'Sr Staff', 'L7', or 'Principal'.
            - L6: Title 'Staff', 'L6', or 'Manager'.
            - L5: Title 'Senior' AND Salary < $210k.
            *UPGRADE: 'Senior' + Salary $210k-$275k -> L6.
            *UPGRADE: 'Senior' + Salary > $275k -> L7.
            
            # Asset 2: Impact-First Cover Letter
            Write a concise, high-impact letter (Max 2 short, punchy paragraphs). 
            Tone: Honest, direct, and executive. Strictly avoid flowery AI-speak like "profound interest" or "passionate about."
            Strategy:
            1. Value to Company: Align candidate's Meta L6 scaling/budget ($100M+) experience with the JD's specific needs.
            2. Value to Candidate: State why this role is a great next step for Mrunal's growth.
            Sign-off: "Thanks and Regards,\n\nMrunal Shirude"
            
            # Asset 3: Strategic Resume Re-Imagining (Aggressive Brevity)
            Identify Top 3 Strategic Pillars of the JD and re-imagine 6-10 bullets for specific alignment.
            STRICT CONSTRAINTS:
            - Max Length: Each bullet MUST be a single, punchy sentence (Max 2 lines). No multi-line blocks.
            - Flexible Formula: [Action Verb] -> [Technical/Domain Context] -> [Strategic Alignment OR Impact].
            - Guidance: Do NOT force numerical results if they feel unnatural. Instead, focus on the "HOW" and the strategic relevance that proves you can thrive in the target role's specific environment.
            - Goal: Maintain creative strategic depth while cutting out all prepositional bloat.
            
            # STRICT JSON OUTPUT FORMAT (No markdown, no backticks):
            {{
              "metadata": {{
                "seniority": "L5/L6/L7/L8",
                "match_score": 95
              }},
              "cover_letter": "Dear hiring team...",
              "resume_edits": [
                {{"old": "exact string", "new": "transformed version"}}
              ]
            }}
            
            JD: {job_description[:6000]}
            Resume Bullets: {json.dumps(raw_bullets)}
            """)
            
        # 3. Execution with Fallback
        fallback_res = {
            "metadata": {"seniority": local_level, "match_score": local_score, "salary": salary_fallback},
            "cover_letter": None,
            "resume_edits": []
        }

        def finalize(data):
            if not data or 'metadata' not in data: data = fallback_res
            data['metadata']['salary'] = salary_fallback # Central Source of Truth
            if 'seniority' not in data['metadata']: data['metadata']['seniority'] = local_level
            if 'match_score' not in data['metadata']: data['metadata']['match_score'] = local_score
            return data

        ai_text = self.get_ai_response(prompt)
        if not ai_text:
            return finalize(fallback_res)
            
        try:
            clean_text = ai_text.replace('```json', '').replace('```', '').strip()
            data = json.loads(clean_text)
            return finalize(data)
        except Exception:
            return finalize(fallback_res)
