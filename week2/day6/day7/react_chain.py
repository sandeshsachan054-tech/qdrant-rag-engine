import os
from pathlib import Path
from time import sleep
from dotenv import load_dotenv
from groq import Groq
import re
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

load_dotenv()
my_api_key=os.getenv("GROQ_API_KEY")

if not my_api_key:
    raise ValueError("Api key kaha hai bhai")
client=Groq(api_key=my_api_key)
model="llama-3.3-70b-versatile"

#tool
def get_product_price(product):
    if product == "iphone 17":
        return 100000
    elif product == 'iphone 15':
        return 70000
    else:
        return 0
    def calculator(expression):
        try:
            return eval(expression)
        except:
            return "calc error!"

        tools={
            "get_product_price": get_product_price,
            "calculator":calculator
        }
        system_prompt = """
You are a shopping assistant.        
You have these tools:
get_product_price(product)
calculator(expression)

IMPORTANT:
Call tools exactly like these examples:

Action: get_product_price("iphone 17")
Action: calculator("200000-100000")

Never write:
get_product_price(product= "iphone 17")
Never write:
calculator(expreesion= "200000-100000")
Follow these rules:

1. Decide what you need to do next.
2. Call ONLY ONE tool at a time.
3. After writing an Action, Stop immediately.
4. Never guess or invent a tool result.
5. Wait until you receive an Observation.
6. Then decide your next action.
7. When the task is complete, give the Find Answer.

Format:

Thought: What you need to do
Action: tool_name(argument)

when finished:
Final Answer: your answer
"""
system_prompt = """
You are a helpful assistant...
"""
def run_agent(question, tools):
    messages = [
        {
            "role": "system",
            "content": system_prompt
        },
        {
            "role": "user",
            "content": question
        }
    ]
    
    for step in range(5):

        print("\n___________________")
        print("STEP",step+1)
        print("___________")

        response=client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=messages,
        temperature=0
        )

        answer=response.choices[0].message.content

        print(answer)

        #Agent has finished 
        if "Final Answer:"in answer:
            break


        # Find the Action


        match = re.search(
            r"Action:\s*(\w+)\((.*?)\)",
            answer
        )

        if match:

            tool_name = match.group(1)

            tool_input = match.group(2)

            tool_input = tool_input.strip()

            tool_input = tool_input.strip('"')

            #Run the tool
            
            
            if tool_name in tools:
                 tool = tools[tool_name]
                 observation = tool(tool_input)


            else:
                    
                    observation = "Tool not found"

            print(
                    "observation:",
                    observation
                )

                #Add LLM response to memory
            messages.append({
                    "role": "assistant",
                    "content": answer
                })
            

                #Give tool result back to LLM

            messages.append({
                    "role": "user",
                    "content":
                    "Observation:"
                    +str(observation)
                })
            sleep(5)



prompt="""

I have 200000 rupees what is the price of an iphone 17?
and how much money will I have left?
"""

run_agent(prompt, [])
                          












