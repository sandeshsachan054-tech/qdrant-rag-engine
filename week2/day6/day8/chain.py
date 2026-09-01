import os
from pathlib import Path
from dotenv import load_dotenv
from groq import Groq
from time import sleep
load_dotenv()

my_api_key=os.getenv("GROQ_API_KEY")

if not my_api_key:
    raise ValueError("Api key kaha hai bhai")
client=Groq(api_key=my_api_key)
model="llama-3.3-70b-versatile"

JD="""
We are hiring a backend python developer.

Requirements:
- Strong Python
- Fast API or Django
- PostgreSQL
- Docker
- AWS
- REST APIs
- 2+ years experience
"""

RESUME="""
Name = Rahul Sharma

Experience:

3 years as a software developer.

Skills:
Python, FastAPI, MySQL, Docker, REST APIs, Git

Projects:
Build a food delivery backend using FastAPI and MySQL.
Deployed applications using Docker.
"""
def ask_llm(system_prompt, user_prompt):
    sys_msg={
        "role": "system",
        "content": system_prompt
    }
    user_msg={
        "role": "user",
        "content": user_prompt
    }
    messages=[sys_msg, user_msg]
    response=client.chat.completions.create(model=model, messages=messages)
    answer = response.choices[0].message.content
    return answer

def step1_resume_extract(RESUME):
    print("STEP1")
    #extract skills from resume
    system_prompt = """
    You are a proffessional HR assisstant.Extract the skills from the candidates resumes provided.
    Only return the skills no other information. Do not invent any skills by yourself.

    OUTPUT FORMAT:
    Skills should be separated by commas.just return comma separated skills do not return any other filler information.
    """

    user_prompt = f"""
    Extract the skills fro this resume
    {RESUME}
    """

    result = ask_llm(system_prompt, user_prompt)
    print(result)
    return result
def step2_JD_extract(JD):
    print("STEP2")
    system_prompt="""
    You are a professional HR assistant.Extract the skills from the job discription provided.
    Only return the skills no other information.
    Do not invent any skills by yourself.
    OUTPUT FORMATE:
    Skills should be separeted by commas. just return comma separeted skills do not return any othe filler information.
    """

    user_prompt=f"""
    Extract the skills from this JD
    {JD}
    """

    return ask_llm(system_prompt, user_prompt)

def step3_match(candidate, jd):

    print("STEP3")
    system_prompt = """
    You are a professional HR assistant. 
    Compare the skills of candidates and the skills required in the JD and produce a final score between 1 to 100.
    also produce short verdict whether a candidate good fit for the role.
    """
    user_prompt = f"""
    Compare and match the skills.
    {candidate}
JD:
{jd}
Candidate:
{candidate}
"""

    return ask_llm(system_prompt, user_prompt)

candidate = step1_resume_extract(RESUME)
print(candidate)
sleep(2)
jd = step2_JD_extract(JD)
print(jd)
sleep(2)

score = step3_match(candidate,jd)
print(score)


