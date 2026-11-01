# from flask import Flask, render_template, request, jsonify
# import os
# import re
# from datetime import datetime
# import google.generativeai as genai
# from api_key import GEMINI_API_KEY

# app = Flask(__name__)
# app.secret_key = os.urandom(24)

# def load_file(path):
#     with open(path, 'r', encoding='utf-8') as f:
#         return f.read()

# def build_prompt(user_question, template, logs):
#     return template.replace("{USER_QUESTION}", user_question.strip()).replace("{LOG_CONTENT}", logs)

# def analyze_logs(prompt):
#     genai.configure(api_key=GEMINI_API_KEY)
#     model = genai.GenerativeModel("gemini-2.0-flash")
#     response = model.generate_content(prompt)
#     return response.text

# @app.route('/')
# def index():
#     return render_template("index.html")

# @app.route('/ask', methods=['POST'])
# def ask():
#     question = request.form['question'].strip()
#     try:
#         logs = load_file("app_logs.txt")
#         prompt_template = load_file("prompt_template.txt")
#         full_prompt = build_prompt(question, prompt_template, logs)

#         analysis = analyze_logs(full_prompt)

#         analysis = re.sub(r'\*\*(.*?)\*\*', r'<strong style="color: goldenrod;">\1</strong>', analysis)
#         analysis = re.sub(r'^Summary:', r'<strong style="color: goldenrod;">Summary:</strong>', analysis, flags=re.MULTILINE)
#         analysis = analysis.replace("\n", "<br>")

#         with open("analysis_output.txt", "w", encoding='utf-8') as f:
#             f.write(analysis)

#         timestamp = datetime.now().strftime('%I:%M %p')

#         return jsonify({ "response": analysis, "timestamp": timestamp })

#     except Exception as e:
#         timestamp = datetime.now().strftime('%I:%M %p')
#         return jsonify({ "response": f"❌ Error: {e}", "timestamp": timestamp })

# if __name__ == '__main__':
#     app.run(debug=True)



# from flask import Flask, render_template, request, jsonify
# import os
# import re
# import json
# from datetime import datetime
# import google.generativeai as genai
# from api_key import GEMINI_API_KEY

# app = Flask(__name__)
# app.secret_key = os.urandom(24)

# def infer_error_type(message):
#     msg = message.lower()
#     known_pattern = re.search(r"([a-zA-Z]+Error)", message)
#     if known_pattern:
#         return known_pattern.group(1)
#     if "timeout" in msg:
#         return "Timeout"
#     if "not found" in msg:
#         return "NotFound"
#     if "failed" in msg:
#         return "Failure"
#     if "invalid" in msg:
#         return "InvalidInput"
#     if "permission" in msg or "unauthorized" in msg:
#         return "PermissionDenied"
#     if "unreachable" in msg:
#         return "UnreachableService"
#     if "503" in msg or "502" in msg:
#         return "ServiceUnavailable"
#     if "exception" in msg:
#         return "Exception"
#     return "Uncategorized"

# def parse_logs(log_file="app_logs.txt", output_file="parsed_logs.txt"):
#     log_pattern = re.compile(
#         r"^(?P<timestamp>\S+)\s+\[(?P<level>ERROR|WARNING|INFO|DEBUG|SUCCESS)\]\s+"
#         r"(?P<source>\S+)\s+-\s+(?P<message>.*)$"
#     )
#     parsed = []
#     with open(log_file, "r", encoding="utf-8") as f:
#         for line in f:
#             match = log_pattern.match(line.strip())
#             if not match:
#                 continue
#             level = match.group("level")
#             if level not in {"ERROR", "WARNING"}:
#                 continue
#             timestamp = match.group("timestamp")
#             source = match.group("source")
#             message = match.group("message").strip()
#             error_type = infer_error_type(message)
#             parsed.append({
#                 "timestamp": timestamp,
#                 "level": level,
#                 "service": source,
#                 "message": message,
#                 "error_type": error_type,
#                 "context": source
#             })
#     with open(output_file, "w", encoding="utf-8") as out:
#         json.dump(parsed, out, indent=2)

# def load_file(path):
#     with open(path, 'r', encoding='utf-8') as f:
#         return f.read()

# def build_prompt(user_question, template, parsed_log_data):
#     formatted_logs = ""
#     for entry in parsed_log_data:
#         formatted_logs += f"[{entry['timestamp']}] [{entry['level']}] {entry['service']} - {entry['message']} (Type: {entry['error_type']})\n"
#     return template.replace("{USER_QUESTION}", user_question.strip()).replace("{LOG_CONTENT}", formatted_logs)

# def analyze_logs(prompt):
#     genai.configure(api_key=GEMINI_API_KEY)
#     model = genai.GenerativeModel("gemini-2.0-flash")
#     response = model.generate_content(prompt)
#     return response.text

# @app.route('/')
# def index():
#     return render_template("index.html")

# @app.route('/ask', methods=['POST'])
# def ask():
#     question = request.form['question'].strip()
#     try:
#         parse_logs(log_file="app_logs.txt", output_file="parsed_logs.txt")

#         with open("parsed_logs.txt", "r", encoding="utf-8") as f:
#             parsed_data = json.load(f)

#         prompt_template = load_file("prompt_template.txt")
#         full_prompt = build_prompt(question, prompt_template, parsed_data)

#         analysis = analyze_logs(full_prompt)

#         analysis = re.sub(r'\*\*(.*?)\*\*', r'<strong style="color: goldenrod;">\1</strong>', analysis)
#         analysis = re.sub(r'^Summary:', r'<strong style="color: goldenrod;">Summary:</strong>', analysis, flags=re.MULTILINE)
#         analysis = analysis.replace("\n", "<br>")

#         with open("analysis_output.txt", "w", encoding='utf-8') as f:
#             f.write(analysis)

#         timestamp = datetime.now().strftime('%I:%M %p')
#         return jsonify({ "response": analysis, "timestamp": timestamp })

#     except Exception as e:
#         timestamp = datetime.now().strftime('%I:%M %p')
#         return jsonify({ "response": f"❌ Error: {e}", "timestamp": timestamp })

# if __name__ == '__main__':
#     app.run(debug=True)

# from flask import Flask, render_template, request, jsonify, session
# import os
# import re
# import json
# from datetime import datetime
# import google.generativeai as genai
# from api_key import GEMINI_API_KEY
# from log_parser import parse_logs
# import pandas as pd

# app = Flask(__name__)
# app.secret_key = os.urandom(24)

# MEMORY_FILE = "long_term_memory.txt"
# SHORT_TERM_MEMORY_FILE = "short_term_memory.txt"

# def load_file(path):
#     with open(path, 'r', encoding='utf-8') as f:
#         return f.read()

# def load_cmdb_text(file_path="CMDB_Amazon.csv"):
#     try:
#         df = pd.read_csv(file_path)
#         df = df[["ID", "App", "Component", "Programming Language"]]
#         return df.to_string(index=False)
#     except Exception as e:
#         return f"⚠️ Error loading CMDB: {e}"

# def load_long_term_memory():
#     if os.path.exists(MEMORY_FILE):
#         with open(MEMORY_FILE, 'r', encoding='utf-8') as f:
#             return f.read()
#     return ""

# def append_to_long_term_memory(summary):
#     with open(MEMORY_FILE, 'a', encoding='utf-8') as f:
#         f.write(summary + "\n\n")

# def summarize_message(message, response):
#     return f"User: {message.strip()}\nAI: {response.strip()[:300]}..."

# def load_short_term_memory():
#     if os.path.exists(SHORT_TERM_MEMORY_FILE):
#         with open(SHORT_TERM_MEMORY_FILE, 'r', encoding='utf-8') as f:
#             return f.read()
#     return ""

# def append_to_short_term_memory(user, ai_response):
#     clean_response = re.sub('<[^<]+?>', '', ai_response)
#     entry = f"User: {user.strip()}\nAI: {clean_response.strip()}\n\n"
#     with open(SHORT_TERM_MEMORY_FILE, 'a', encoding='utf-8') as f:
#         f.write(entry)

# def build_prompt(user_question, template, parsed_log_data, cmdb_text, long_term_memory="", short_term_memory=""):
#     formatted_logs = ""
#     for entry in parsed_log_data:
#         formatted_logs += f"[{entry['timestamp']}] [{entry['level']}] {entry['service']} - {entry['message']} (Type: {entry['error_type']})\n"

#     return (
#         template
#         .replace("{USER_QUESTION}", user_question.strip())
#         .replace("{LOG_CONTENT}", formatted_logs)
#         .replace("{CMDB_DB}", cmdb_text)
#         .replace("{MEMORY}", long_term_memory.strip())
#         .replace("{SHORT_MEMORY}", short_term_memory.strip())
#     )

# def analyze_logs(prompt):
#     genai.configure(api_key=GEMINI_API_KEY)
#     model = genai.GenerativeModel("gemini-2.0-flash")
#     response = model.generate_content(prompt)
#     return response.text

# @app.route('/')
# def index():
#     # Clear short-term memory when the chatbot is reopened
#     with open(SHORT_TERM_MEMORY_FILE, 'w', encoding='utf-8') as f:
#         f.write("")
#     session['history'] = []
#     return render_template("index.html")

# @app.route('/ask', methods=['POST'])
# def ask():
#     question = request.form['question'].strip()
#     try:
#         # Parse logs
#         parse_logs("app_logs.txt", "parsed_logs.txt")
#         with open("parsed_logs.txt", "r", encoding="utf-8") as f:
#             parsed_data = json.load(f)

#         # Load files and memory
#         prompt_template = load_file("prompt_template.txt")
#         cmdb_text = load_cmdb_text()
#         long_memory = load_long_term_memory()
#         short_memory = load_short_term_memory()

#         # Build prompt
#         full_prompt = build_prompt(question, prompt_template, parsed_data, cmdb_text, long_memory, short_memory)

#         # Call LLM
#         raw_response = analyze_logs(full_prompt)

#         # Style for UI
#         styled_response = re.sub(r'\*\*(.*?)\*\*', r'<strong style="color: goldenrod;">\1</strong>', raw_response)
#         styled_response = re.sub(r'^Summary:', r'<strong style="color: goldenrod;">Summary:</strong>', styled_response, flags=re.MULTILINE)
#         styled_response = styled_response.replace("\n", "<br>")

#         # Save raw response
#         with open("analysis_output.txt", "w", encoding='utf-8') as f:
#             f.write(raw_response)

#         # Update memories
#         essence = summarize_message(question, raw_response)
#         append_to_long_term_memory(essence)
#         append_to_short_term_memory(question, raw_response)

#         # Save UI history (if needed)
#         if 'history' not in session:
#             session['history'] = []
#         session['history'].append({ "question": question, "response": styled_response })

#         timestamp = datetime.now().strftime('%I:%M %p')
#         return jsonify({ "response": styled_response, "timestamp": timestamp })

#     except Exception as e:
#         timestamp = datetime.now().strftime('%I:%M %p')
#         return jsonify({ "response": f"❌ Error: {e}", "timestamp": timestamp })

# if __name__ == '__main__':
#     app.run(debug=True)

from flask import Flask, render_template, request, jsonify, session
import os
import re
import json
from datetime import datetime
import google.generativeai as genai
from api_key import GEMINI_API_KEY
from log_parser import parse_logs
import pandas as pd
from helper_app import rephrase_input, classify_query
from agent_code.ui_integrator import analysis

app = Flask(__name__)
app.secret_key = os.urandom(24)

MEMORY_FILE = "long_term_memory.txt"
SHORT_TERM_MEMORY_FILE = "short_term_memory.txt"

def load_file(path):
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()

def load_cmdb_text(file_path="CMDB_V2.csv"):
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
        else:
            raw_response = analysis(question)
            styled_response=raw_response
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

if __name__ == '__main__':
    app.run(debug=True)