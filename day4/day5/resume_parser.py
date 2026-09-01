import os
from pathlib import Path
from dotenv import load_dotenv
from groq import Groq
from pydantic import BaseModel
import json
import time
from pypdf import PdfReader
from docx import Document
load_dotenv(override=True)
my_api_key=os.getenv("GROQ_API_KEY")

if not my_api_key:
    raise ValueError("API key kaha hai bhai")

client=Groq(api_key=my_api_key)
model="llama-3.3-70b-versatile"

job_description = """"
Description

Selling Parter Identity Verifcation operates at the core of Amazon's marketplace security infrastructure, implementing complex distributed systems that ensure marketplace compliance and seller authenticity. Our engineering teams build and maintain high-throughput verification systems that process over 1.5M requests weekly, focusing on scalable identity verification and fraud prevention mechanisms.

The Seller Registration domain encompasses a suite of distributed services handling seller verification and onboarding across Amazon's global marketplace. Our technical charter focuses on three primary engineering challenges: architecting streamlined, globally distributed registration systems; implementing robust identity verification services with real-time validation capabilities; and developing sophisticated automation frameworks that maintain high accuracy while scaling horizontally. Our systems are designed to handle complex state management across regions while maintaining strict security protocols and data consistency.

We are scaling our architecture to simplify onboarding and enabling global entities. This involves developing stateless microservices, implementing event-driven architectures for cross-regional communication, and creating scalable data models that support multi-region operations.

We're seeking Senior Engineers with extensive experience in distributed systems design and implementation. The role requires deep technical expertise in building high-throughput, low-latency services and a thorough understanding of cloud-native architectures. You'll be working with modern tech stacks including microservices architecture, step functions, event-driven systems, distributed databases, and sophisticated identity verification services.

The Ideal Candidate Will Have Demonstrated Expertise In

Architecting globally distributed systems with emphasis on scalability and reliability. This includes experience with cross-regional data consistency, cache invalidation strategies, and distributed transaction management. You should be well-versed in designing fault-tolerant systems that maintain high availability across multiple regions while handling complex state management. Good background in security protocols and identity management systems is essential, as is experience with event-driven architectures and asynchronous processing patterns. Additionally, you should be comfortable with modern DevOps practices and maintaining CI/CD pipelines for large-scale distributed systems.

Our engineering culture emphasizes technical excellence, innovation, and iterative development using advanced technologies. We operate in an environment where architectural decisions have significant impact on Amazon's global marketplace operations, requiring careful consideration of scalability, security, and performance implications.

Key job responsibilities
• Computer Science fundamentals in algorithm design, problem solving, and complexity analysis
• Experience System Design Skills
• Ability to build product from scratch
• Take bottom line ownership and drive tech initiatives
• Drive enterprise Architecture and Solution Architecture
• Drive tech team and be a role model for engineering excellence

Basic Qualifications
• Bachelor's degree in computer science or equivalent
• 5+ years of non-internship professional software development experience
• 5+ years of programming with at least one software programming language experience
• 5+ years of leading design or architecture (design patterns, reliability and scaling) of new and existing systems experience
• Experience as a mentor, tech lead or leading an engineering team

Preferred Qualifications
• 5+ years of full software development life cycle, including coding standards, code reviews, source control management, build processes, testing, and operations experience

Our inclusive culture empowers Amazonians to deliver the best results for our customers. If you have a disability and need a workplace accommodation or adjustment during the application and hiring process, including support for the interview or onboarding process, please visit https://amazon.jobs/content/en/how-we-hire/accommodations for more information. If the country/region you’re applying in isn’t listed, please contact your Recruiting Partner.

Company - ADCI HYD 13 SEZ

Job ID: A10474686
"""
class JobD(BaseModel):
    required_skills: list[str]
    preferred_skills: list[str]
    minimum_experience: float | None
    education_requirements: list[str]
    responsibilities: list[str]

jobd_schema = JobD.model_json_schema()

system_prompt = f"""
You are an expert HR assistant.

Your job is to analyze job descriptions and extract 
structured information from them.

Return ONLY valid JSON matching this schema:

{jobd_schema}

IMPORTANT:
Do NOT return the schema itself.
Do NOT return fields like "properties", "title" or "type".
Fill the schema with actual information extracted from the job description.

If minimum experience is not mentioned, return null.
If information for a list is missing, return an empty list.
Do not invent information.
"""
user_prompt = f"""
Analyze the following job description:

{job_description}
"""

message_system = {
    "role": "system",
    "content": system_prompt
}

message_user = {
    "role": "user",
    "content": user_prompt
}

response_format = {
    "type": "json_object"
}

messages = [message_system, message_user]

response = client.chat.completions.create(
    model=model,
    messages=messages,
    response_format=response_format
)
answer = response.choices[0].message.content

raw_json = answer
# print(raw_json)


import json
job_data = json.loads(raw_json)

job = JobD(**job_data)

print(job.minimum_experience)
print(job.education_requirements)


#parse real
class MatchResult(BaseModel):
    score: float
    details: dict

class Experience(BaseModel):
    role: str | None = None
    duration: str | None = None
    description: str | None = None
    skills_used: list[str] = []

class Resume(BaseModel):
    name: str | None = None
    email: str | None = None
    phone: str | None = None

    total_experience_years: float | None = None

    skills: list[str] = []
    experiences: list[Experience] = []
    education: list[str] = []
    projects: list[str] = []
    certifications: list[str] = []
resume_schema = Resume.model_json_schema()

def final_score(job, resume):
    match_schema = MatchResult.model_json_schema()
    prompt = f"""
You are an HR recruiter.

Compare the candidate's resume with the job description.

JOB DESCRIPTION:
{job.model_dump_json(indent=2)}

CANDIDATE RESUME:
{resume.model_dump_json(indent=2)}
Return JSON matching this schema:

{match_schema}

Give me:

1. Candidate name
2. Matching skills
3. Missing important skills
4. Whether experience requirement is met
5. Overall match percentage from 0 to 100
"""
    # --- Yahan se missing line start ho rahi hain aur function complete ho raha hai ---
    messages = [
        {"role": "system", "content": prompt}
    ]
    
    response_format = {"type": "json_object"}
    
    response = client.chat.completions.create(
        model=model,
        messages=messages,
        response_format=response_format
    )
    
    data = json.loads(response.choices[0].message.content)
    return MatchResult(**data)


# --- Naya Function jo aapki nayi image me dikh raha hai ---
def parse_resume(resume_text):
    system_prompt = f"""
You are an expert resume parser.

Extract information from the resume based on its meaning,
not only based on exact section headings.

Different resumes may use different headings.

For example:
- Experience
- Professional Experience
- Work History
- Employment
- Internships

These may all contain relevant experience.
"""
    system_prompt = f"""
You are an expert resume parser.

Extract information from the resume based on its meaning,
not only based on exact section headings.

Different resumes may use different headings.

For example:
- Experience
- Professional Experience
- Work History
- Employment
- Internships

These may all contain relevant experience.
Skills may also appear in the skills section, work experience,
internships or projects.

Return ONLY valid JSON matching this schema:

{resume_schema}

Important rules:

1. Do not invent information.
2. If a value is not available, return null.
3. If a list has no information, return an empty list.
4. Include internships inside experiences.
5. Extract skills mentioned across the entire resume.
"""

    user_prompt = f"""
Parse the following resume:

{resume_text}
"""

    message_system = {
        "role": "system",
        "content": system_prompt
    }
    message_user = {
        "role": "user",
        "content": user_prompt
    }

    messages = [message_system, message_user]
    
    response_format = {
        "type": "json_object"
    }

    response = client.chat.completions.create(
        model=model,
        messages=messages,
        response_format=response_format
    )

    raw_output = response.choices[0].message.content
    data = json.loads(raw_output)
    resume = Resume(**data)
    return resume


# --- File Reading Utility Section ---
from pypdf import PdfReader
from docx import Document

def read_pdf(file_path):
    reader = PdfReader(file_path)
    # --- File Reading Utility Section ---
from pathlib import Path
from pypdf import PdfReader
from docx import Document
import time

def read_pdf(file_path):
    try:
        reader = PdfReader(file_path)
        text = ""
        for page in reader.pages:
            text += page.extract_text() or ""
        return text
    except Exception as e:
        print(f"Error reading PDF {file_path}: {e}")
        return ""

def read_docx(file_path):
    try:
        doc = Document(file_path)
        text = []
        for para in doc.paragraphs:
            text.append(para.text)
        return "\n".join(text)
    except Exception as e:
        print(f"Error reading DOCX {file_path}: {e}")
        return ""

def read_resume(file_path):
    suffix = file_path.suffix.lower()
    if suffix == ".pdf":
        return read_pdf(file_path)
    elif suffix == ".docx":
        return read_docx(file_path)
    return ""


# # lets do it now
resume_folder = Path("resumes")
all_results = []

for file_path in resume_folder.iterdir():
    if file_path.suffix.lower() not in [".pdf", ".docx"]:
        continue
        
    print(f"\nProcessing:", file_path.name)
    resume_text = read_resume(file_path)
    
    parsed_resume = parse_resume(resume_text)
    time.sleep(5)
    
    result = final_score(job, parsed_resume)
    time.sleep(5)
    
    print("Score:", result.score)
    all_results.append({
        "name": parsed_resume.name,
        "score": result.score,
        "details": result.details
    })

# Sorting results based on score in descending order (highest score first)
all_results.sort(key=lambda candidate: candidate["score"], reverse=True)
all_results.sort(
    key=lambda candidate: candidate["score"],
    reverse=True
)

top_2 = all_results[:2]
worst_2 = all_results[-2:]


print("TOP 2 CANDIDATES")
for candidate in top_2:
    print(
        candidate["name"],
        "-",
        candidate["score"]
    )
    print(candidate["details"])

print("LOWEST 2 CANDIDATES")
for candidate in worst_2:
    print(
        candidate["name"],
        "-",
        candidate["score"],
        "%"
    )
    print(candidate["details"])