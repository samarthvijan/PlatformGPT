from flask import Flask, render_template, request, jsonify, session
import os
import re
import json
from datetime import datetime
import google.generativeai as genai
from api_key import GEMINI_API_KEY
from log_parser import parse_logs
import pandas as pd

app = Flask(__name__)
app.secret_key = os.urandom(24)

MEMORY_FILE = "long_term_memory.txt"
SHORT_TERM_MEMORY_FILE = "short_term_memory.txt"

def load_file(path):
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()

def load_cmdb_text(file_path="CMDB_Amazon.csv"):
    try:
        df = pd.read_csv(file_path)
        df = df[["ID", "App", "Component", "Programming Language"]]
        return df.to_string(index=False)
    except Exception as e:
        return f"⚠️ Error loading CMDB: {e}"

def load_long_term_memory():
    if os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE, 'r', encoding='utf-8') as f:
            return f.read()
    return ""

def append_to_long_term_memory(summary):
    with open(MEMORY_FILE, 'a', encoding='utf-8') as f:
        f.write(summary + "\n\n")

def summarize_message(message, response):
    return f"User: {message.strip()}\nAI: {response.strip()[:300]}..."

def load_short_term_memory():
    if os.path.exists(SHORT_TERM_MEMORY_FILE):
        with open(SHORT_TERM_MEMORY_FILE, 'r', encoding='utf-8') as f:
            return f.read()
    return ""

def append_to_short_term_memory(user, ai_response):
    clean_response = re.sub('<[^<]+?>', '', ai_response)
    entry = f"User: {user.strip()}\nAI: {clean_response.strip()}\n\n"
    with open(SHORT_TERM_MEMORY_FILE, 'a', encoding='utf-8') as f:
        f.write(entry)

def build_prompt(user_question, template, parsed_log_data, cmdb_text, long_term_memory="", short_term_memory=""):
    formatted_logs = ""
    for entry in parsed_log_data:
        formatted_logs += f"[{entry['timestamp']}] [{entry['level']}] {entry['service']} - {entry['message']} (Type: {entry['error_type']})\n"

    return (
        template
        .replace("{USER_QUESTION}", user_question.strip())
        .replace("{LOG_CONTENT}", formatted_logs)
        .replace("{CMDB_DB}", cmdb_text)
        .replace("{MEMORY}", long_term_memory.strip())
        .replace("{SHORT_MEMORY}", short_term_memory.strip())
    )

def analyze_logs(prompt):
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel("gemini-2.0-flash")
    response = model.generate_content(prompt)
    return response.text

@app.route('/')
def index():
    # Clear short-term memory when the chatbot is reopened
    with open(SHORT_TERM_MEMORY_FILE, 'w', encoding='utf-8') as f:
        f.write("")
    session['history'] = []
    return render_template("index.html")

@app.route('/ask', methods=['POST'])
def ask():
    question = request.form['question'].strip()
    try:
        # Parse logs
        parse_logs("app_logs.txt", "parsed_logs.txt")
        with open("parsed_logs.txt", "r", encoding="utf-8") as f:
            parsed_data = json.load(f)

        # Load files and memory
        prompt_template = load_file("prompt_template.txt")
        cmdb_text = load_cmdb_text()
        long_memory = load_long_term_memory()
        short_memory = load_short_term_memory()

        # Build prompt
        full_prompt = build_prompt(question, prompt_template, parsed_data, cmdb_text, long_memory, short_memory)

        # Call LLM
        raw_response = analyze_logs(full_prompt)

        # Style for UI
        styled_response = re.sub(r'\*\*(.*?)\*\*', r'<strong style="color: goldenrod;">\1</strong>', raw_response)
        styled_response = re.sub(r'^Summary:', r'<strong style="color: goldenrod;">Summary:</strong>', styled_response, flags=re.MULTILINE)
        styled_response = styled_response.replace("\n", "<br>")

        # Save raw response
        with open("analysis_output.txt", "w", encoding='utf-8') as f:
            f.write(raw_response)

        # Update memories
        essence = summarize_message(question, raw_response)
        append_to_long_term_memory(essence)
        append_to_short_term_memory(question, raw_response)

        # Save UI history (if needed)
        if 'history' not in session:
            session['history'] = []
        session['history'].append({ "question": question, "response": styled_response })

        timestamp = datetime.now().strftime('%I:%M %p')
        return jsonify({ "response": styled_response, "timestamp": timestamp })

    except Exception as e:
        timestamp = datetime.now().strftime('%I:%M %p')
        return jsonify({ "response": f"❌ Error: {e}", "timestamp": timestamp })

#if __name__ == '__main__':
    #app.run(debug=True)

def task1_3(question):
    parse_logs("app_logs.txt", "parsed_logs.txt")
    with open("parsed_logs.txt", "r", encoding="utf-8") as f:
        parsed_data = json.load(f)

    # Load files and memory
    prompt_template = load_file("prompt_template.txt")
    cmdb_text = load_cmdb_text()
    long_memory = load_long_term_memory()
    short_memory = load_short_term_memory()

    # Build prompt
    full_prompt = build_prompt(question, prompt_template, parsed_data, cmdb_text, long_memory, short_memory)

    # Call LLM
    raw_response = analyze_logs(full_prompt)

    # Style for UI
    styled_response = re.sub(r'\*\*(.*?)\*\*', r'<strong style="color: goldenrod;">\1</strong>', raw_response)
    styled_response = re.sub(r'^Summary:', r'<strong style="color: goldenrod;">Summary:</strong>', styled_response, flags=re.MULTILINE)
    styled_response = styled_response.replace("\n", "<br>")
    return styled_response