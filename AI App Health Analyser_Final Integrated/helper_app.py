

from langchain.prompts import ChatPromptTemplate
from agent_code.agent.llm_handler import llm_json
from task1_3_function import task1_3

def rephrase_input(question):
    # Step 1: Load chat history
    try:
        with open("short_term_memory.txt", "r", encoding="utf-8") as f:
            chat_history = f.read()
    except Exception as e:
        raise RuntimeError(f"Failed to read chat history: {e}")

    # Step 2: Define rephrasing prompt
    prompt_template_str = """You are a helpful AI assistant.

Using the following conversation history:
{chat_history}
Also if quesry goes like is everyhting fine with all or with my system that means all the applications it is very very important
Rephrase the following question to make it fully self-contained and contextually complete:
{user_question}

Only return the rephrased question. Do not explain anything."""

    prompt = ChatPromptTemplate.from_template(prompt_template_str)

    # Step 3: Prepare and call LLM
    messages = prompt.format_messages(
        chat_history=chat_history,
        user_question=question
    )

    llm = llm_json()
    response = llm.invoke(messages)

    return response.content.strip()
original_question = "What should I fix in AuthService?"
rephrased = rephrase_input(original_question)
print("Rephrased Question:", rephrased)

# Then use it like:
# result = classify_query(rephrased)

from langchain.prompts import ChatPromptTemplate
from agent_code.agent.llm_handler import llm_json  # assuming this returns a LangChain-compatible chat model

def classify_query(rephrase_input):
    question1 = rephrase_input  # or question(rephrase_input) if that's a function

    llm = llm_json()

    template = '''You are a AI router for my project. My tools deal with three things only:
1. Summarizing issues or explaining them in detail.
2. Representing these issues visually via displaying a deployment diagram.
3. Suggesting fixes for the issues.

I am providing you with a user query. You must return **true** or **false**, and **nothing else**, based on these rules:

- If the query asks for a "visualization" or a "deployment diagram" --> return **false**
- Otherwise --> return **true**


Query:
{user_query}

Note: Do NOT return any explanation. Only return **true** or **false**. This is very important.'''

    # Create prompt
    prompt_template = ChatPromptTemplate.from_template(template)

    # Format the message
    messages = prompt_template.format_messages(user_query=question1)

    # Call the model
    response = llm.invoke(messages)

    # Clean output
    result = response.content.strip().lower()
    # print(result)

    # Return as boolean string (optional: validate output)
    if result not in {"true", "false"}:
        raise ValueError(f"Unexpected output: {result}")
    
    return result

from agent_code.agent.llm_handler import llm_json

from flask import Flask, render_template, request, jsonify
#from ollama import Client
import os
import re
from datetime import datetime
from agent_code.ui_integrator import analysis
from flask import request, jsonify
from datetime import datetime
from datetime import datetime
# from agent_code.agent.rephraser_llm import rephrase_input
def get_time():
    now = datetime.now()
    hours = now.hour % 12 or 12
    minutes = str(now.minute).zfill(2)
    am_pm = 'AM' if now.hour < 12 else 'PM'
    return f"{hours}:{minutes} {am_pm}"


app = Flask(__name__)
app.secret_key = os.urandom(24)

# def load_file(path):
#     with open(path, 'r', encoding='utf-8') as f:
#         return f.read()

# def build_prompt(user_question, template, logs):
#     return f"{user_question.strip()}\n\n" + template.replace("{LOG_CONTENT}", logs)

# def analyze_logs(prompt):
#     client = Client()
#     response = client.chat(model="llama3", messages=[
#         {"role": "user", "content": prompt}
#     ])
#     return response['message']['content']
from app2 import task3
@app.route('/')
def index():
    return render_template("index.html")

@app.route('/ask', methods=['POST'])
def ask():
    # print("POST /ask received")
    question = request.form['question'].strip()
    # print(question)

    try:
        # logs = load_file("app_logs.txt")
        # print(question)
        question1=rephrase_input(question)
        # llm=llm_json()
        # template= '''You are a AI router my project. My tools deal with three things only summarize issues using logs create deployment architecture 
        # and  last suggest fixes . I am providing you with user query what you need to do is return true of false it is very very importand return only true
        # or false based on the following conditions
        # 1 If query asks for fixes use return false
        # else return true
        # if query have both fixes and summaries then return false only

        # Note: You only have to return true or false nothing else this is very very very very important
        # '''
        print(question1)
        a=classify_query(question1)
        print(a)
        if a == "true":  # ✅ compare string to string
            result = analysis(question)
        else:
            result = task1_3(question)
        with open(r'C:\Users\AnirudhVijan\Desktop\project2\Coding\prot5\q\agent_code\data\chat_memory_log.txt', 'r') as f:
            hist=f.read()

        hist+=f'\nhuman:{question1}\nai: {result}'

        with open(r'C:\Users\AnirudhVijan\Desktop\project2\Coding\prot5\q\agent_code\data\chat_memory_log.txt', 'w') as f:
            f.write(hist)


        with open("analysis_output.txt", "w", encoding='utf-8') as f:
            f.write(result)

        # Timestamp after analysis is complete
        # timestamp = datetime.now().strftime('%I:%M %p')

        return jsonify({ "response": result })

    except Exception as e:
        timestamp = datetime.now().strftime('%I:%M %p')
        return jsonify({ "response": f"❌ Error: {e}", "timestamp": timestamp })


if __name__ == '__main__':
    app.run(debug=True)


