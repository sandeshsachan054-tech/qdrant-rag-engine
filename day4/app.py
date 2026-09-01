import os
import json
from dotenv import load_dotenv
from groq import Groq
from pydantic import BaseModel
from typing import List
import PyPDF2

# 1. Load Environment Variables (.env file check karega)
load_dotenv(dotenv_path=r"C:\Users\sande\sandeshsachan\day4\.env", override=True)
api_key = os.getenv("GROQ_API_KEY")

if not api_key:
    raise ValueError("Bhai, .env file me GROQ_API_KEY check karo, nahi mili!")

client = Groq(api_key=api_key)

# 2. Pydantic Structure Definition for Final AI Output
class MatchResult(BaseModel):
    matching_percentage: int
    matched_skills: List[str]
    missing_skills: List[str]
    experience_status: str
    verdict: str

# 3. PDF se Text Nikalne ka Function
def extract_text_from_pdf(pdf_path):
    try:
        with open(pdf_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            text = ""
            for page in reader.pages:
                text += page.extract_text() or ""
            return text
    except Exception as e:
        print(f"PDF read karne me dikkat aayi bhai: {e}")
        return ""

# 4. Resume aur HR List Match karne wala main function
def match_resume_with_hr(resume_text, hr_skills, hr_exp, hr_projects):
    hr_requirements = f"""
    - Required Skills: {", ".join(hr_skills)}
    - Required Experience: {hr_exp} years
    - Target Projects/Domain: {", ".join(hr_projects)}
    """
    
    system_prompt = (
        "You are an expert HR ATS (Applicant Tracking System). Your job is to strictly analyze "
        "the provided Resume text against the HR Requirements. Calculate the true match percentage, "
        "list matched/missing skills, look at experience, and give a short final verdict. "
        "You must respond ONLY with a JSON object that matches the requested schema."
    )
    
    user_prompt = f"""
    HR Requirements:
    {hr_requirements}
    
    Candidate Resume Text:
    {resume_text}
    """
    
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        response_format={"type": "json_object"}
    )
    
    raw_content = response.choices[0].message.content
    return json.loads(raw_content)

# --- EXECUTION ---
if __name__ == "__main__":
    hr_skills = ["Python", "SQL", "FastAPI", "Git", "Docker"]
    hr_experience_required = 2
    hr_projects_required = ["REST APIs", "Microservices"]
    
    # PDF ka lafda hi khatam! Direct text variable bana diya
    print("Reading Resume Text directly...")
    resume_data = """
    Rahul Sharma - Backend Developer
    Skills: Python, SQL, FastAPI, Git, Docker
    Experience: 3 years building scalable microservices.
    Projects: Integrated REST APIs and optimized database queries.
    """
    
    print("AI matching process running on Groq...")
    output = match_resume_with_hr(resume_data, hr_skills, hr_experience_required, hr_projects_required)
    
    print("\n" + "="*40)
    print("      ATS MATCHING REPORT      ")
    print("="*40)
    
    # Case-insensitive checks taaki key mismatch na ho
    def find_key(data, target):
        for k, v in data.items():
            if target.lower() in k.lower():
                return v
        return data.get(target, "N/A")

    print(f"Match Percentage    : {find_key(output, 'percentage')}%")
    print(f"Skills Matched      : {', '.join(find_key(output, 'matched_skills')) if isinstance(find_key(output, 'matched_skills'), list) else find_key(output, 'matched_skills')}")
    print(f"Skills Missing      : {', '.join(find_key(output, 'missing_skills')) if isinstance(find_key(output, 'missing_skills'), list) else find_key(output, 'missing_skills')}")
    print(f"Experience Check    : {find_key(output, 'experience')}")
    print(f"Final Verdict       : {find_key(output, 'verdict')}")
    print("="*40)