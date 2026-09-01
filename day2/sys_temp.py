import os
from pathlib import Path
from dotenv import load_dotenv
from groq import Groq

load_dotenv(override=True)
my_api_key=os.getenv("GROQ_API_KEY")

if not my_api_key:
    raise ValueError("API key kaha hai bhai")

client=Groq(api_key=my_api_key)
model="llama-3.3-70b-versatile"
role="user"
prompt="Suggests name for my iron company"
message_system={
    "role":"system",
    "content":"You are a brand manager who suggests name for my iron  company. name should be in one word. suggest one name only"
}
message={
    "role": role,
    "content":prompt
}


messages=[message_system, message]

response=client.chat.completions.create(model=model,messages=messages,temperature=2)
print(response.choices[0].message.content)