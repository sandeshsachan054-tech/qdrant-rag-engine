import os
import sys
sys.stdout.reconfigure(encoding='utf-8')
from pathlib import Path
from dotenv import load_dotenv
from groq import Groq
load_dotenv()
my_api_key=os.getenv("GROQ_API_KEY")
if not my_api_key:
    raise ValueError("API key kaha hai bhai")
client=Groq(api_key=my_api_key)
model="openai/gpt-oss-120b"
#step1
knowledge_base = {
    "age" : "The age of sandesh is 20 years",
    "net worth" : "The net worth of sandesh is 1000"
}
#step2 retrieval
def retrieve_info(question):
    question=question.lower()
    retrieved = []
    if "age" in question:
        retrieved.append(knowledge_base["age"])
    if "net worth" in question:
        retrieved.append(knowledge_base["net worth"])
    if retrieved:
        return" ".join(retrieved)
    return None
def ask_llm(question):
        context=retrieve_info(question)

        sys_prompt=f"""answer in one line only. Answer only based on this context. Do not hallucinate.context:{context}"""
        system_message={
            "role":"system",
            "content": sys_prompt
        }
        user_message = {
            "role": "user",
            "content": question
        }
        messages = [system_message, user_message]
        response=client.chat.completions.create(model=model,messages=messages)
        answer=response.choices[0].message.content
        return answer
question= "do you know sandesh age and net worth"
print(ask_llm(question))