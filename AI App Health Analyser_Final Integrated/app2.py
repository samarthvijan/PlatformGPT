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

from flask import Flask, render_template, request, jsonify
import os
import re
import json
from datetime import datetime
from agent_code.agent.llm_handler import llm_json
from log_parser import parse_logs
import pandas as pd

app = Flask(__name__)
app.secret_key = os.urandom(24)

def load_file(path):
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()
def load_cmdb_text(file_path="CMDB_Amazon.csv"):
    try:
        df = pd.read_csv(file_path)
        df = df[["ID", "App", "Component", "Programming Language"]]  # keep only relevant
        return df.to_string(index=False)
    except Exception as e:
        return f"⚠️ Error loading CMDB: {e}"

def build_prompt(user_question, template, parsed_log_data, cmdb_text):
    formatted_logs = ""
    for entry in parsed_log_data:
        print(entry)
        break
        formatted_logs += f"[{entry['timestamp']}] [{entry['level']}] {entry['service']} - {entry['message']} (Type: {entry['error_type']})\n"

    return (
        template
        .replace("{USER_QUESTION}", user_question.strip())
        .replace("{LOG_CONTENT}", formatted_logs)
        .replace("{CMDB_DB}", cmdb_text)
    )

def analyze_logs(prompt):
    # genai.configure(api_key=GEMINI_API_KEY)
    # model = genai.GenerativeModel("gemini-2.0-flash")
    model=llm_json()
    response = model.invoke(prompt)
    return response.content

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/ask', methods=['POST'])
def ask():
    question = request.form['question'].strip()
    try:
        # Step 1: Parse logs and load parsed data
        parse_logs("app_logs.txt", "parsed_logs.txt")

        with open("parsed_logs.txt", "r", encoding="utf-8") as f:
            parsed_data = json.load(f)
        print(type(parsed_data))
        # Step 2: Load prompt template
        prompt_template = load_file("prompt_template.txt")

        # Step 3: Load CMDB as text (only required columns)
        import pandas as pd
        cmdb_df = pd.read_csv("CMDB_Amazon.csv")
        cmdb_df = cmdb_df[["ID", "App", "Component", "Programming Language"]]
        cmdb_text = cmdb_df.to_string(index=False)

        # Step 4: Build full prompt
        full_prompt = build_prompt(question, prompt_template, parsed_data, cmdb_text)

        # Step 5: Call LLM
        analysis = analyze_logs(full_prompt)

        # Step 6: Apply styling
        analysis = re.sub(r'\*\*(.*?)\*\*', r'<strong style="color: goldenrod;">\1</strong>', analysis)
        analysis = re.sub(r'^Summary:', r'<strong style="color: goldenrod;">Summary:</strong>', analysis, flags=re.MULTILINE)
        analysis = analysis.replace("\n", "<br>")

        # Step 7: Save & return
        with open("analysis_output.txt", "w", encoding='utf-8') as f:
            f.write(analysis)

        timestamp = datetime.now().strftime('%I:%M %p')
        return jsonify({ "response": analysis, "timestamp": timestamp })

    except Exception as e:
        timestamp = datetime.now().strftime('%I:%M %p')
        return jsonify({ "response": f"❌ Error: {e}", "timestamp": timestamp })

# if __name__ == '__main__':
#     app.run(debug=True)



# def task3(question):
#     llm=llm_json()
#     with open(r"C:\Users\AnirudhVijan\Desktop\project2\Coding\prot5\q\agent_code\data\enriched_logs.json", "r", encoding="utf-8") as f:
#         parsed_data = json.load(f)

#     # Step 2: Load prompt template
#     prompt_template = load_file("prompt_task3.txt")
#     print(prompt_template)
#     # Step 3: Load CMDB as text (only required columns)
#     import pandas as pd
#     cmdb_df = pd.read_csv(r"C:\Users\AnirudhVijan\Desktop\project2\Coding\prot5\q\agent_code\data\cmdb_with_languages.csv")
#     cmdb_df = cmdb_df[["ID", "App", "Component", "ProgrammingLanguage"]]
#     cmdb_text = cmdb_df.to_string(index=False)

#     # Step 4: Build full prompt
#     full_prompt = build_prompt(question, prompt_template, parsed_data, cmdb_text)

#     # Step 5: Call LLM
#     analysis = analyze_logs(full_prompt)

#     # Step 6: Apply styling
#     analysis = re.sub(r'\*\*(.*?)\*\*', r'<strong style="color: goldenrod;">\1</strong>', analysis)
#     analysis = re.sub(r'^Summary:', r'<strong style="color: goldenrod;">Summary:</strong>', analysis, flags=re.MULTILINE)
# #     analysis = analysis.replace("\n", "<br>")
# #     with open("analysis_output.txt", "w", encoding='utf-8') as f:
# #         f.write(analysis)

# #     timestamp = datetime.now().strftime('%I:%M %p')
# #     return jsonify({ "response": analysis, "timestamp": timestamp })
    




# from flask import app

# def task3(question):
#     llm = llm_json()
#     with open(r"C:\Users\AnirudhVijan\Desktop\project2\Coding\prot5\q\agent_code\data\enriched_logs.json", "r", encoding="utf-8") as f:
#         parsed_data = json.load(f)
#     print(type(parsed_data))
#     prompt_template = load_file("prompt_task3.txt")

#     import pandas as pd
#     cmdb_df = pd.read_csv(r"C:\Users\AnirudhVijan\Desktop\project2\Coding\prot5\q\agent_code\data\cmdb_with_languages.csv")
#     cmdb_df = cmdb_df[["ID", "App", "Component", "ProgrammingLanguage"]]
#     cmdb_text = cmdb_df.to_string(index=False)

#     full_prompt = build_prompt(question, prompt_template, parsed_data, cmdb_text)

#     analysis = analyze_logs(full_prompt)

#     analysis = re.sub(r'\*\*(.*?)\*\*', r'<strong style="color: goldenrod;">\1</strong>', analysis)
#     analysis = re.sub(r'^Summary:', r'<strong style="color: goldenrod;">Summary:</strong>', analysis, flags=re.MULTILINE)
#     analysis = analysis.replace("\n", "<br>")

#     with open("analysis_output.txt", "w", encoding='utf-8') as f:
#         f.write(analysis)

#     timestamp = datetime.now().strftime('%I:%M %p')

#     # ✅ FIX HERE: wrap jsonify in app.app_context()
#     with app.app_context():
#         return jsonify({ "response": analysis, "timestamp": timestamp })


from datetime import datetime
import json
import pandas as pd
import re
from flask import jsonify
from langchain.prompts import ChatPromptTemplate
from agent_code.agent.llm_handler import llm_json
from agent_code.tools.tool4 import generate_deployment_diagram
def load_file(path):
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()

def task3(question):
    # Load enriched logs
   
    file_path = r"C:\Users\AnirudhVijan\Desktop\project2\Coding\prot5\q\agent_code\data\enriched_logs.json"

    if not os.path.exists(file_path):
        generate_deployment_diagram()

    print(1)
    with open(file_path, "r", encoding="utf-8") as f:
        parsed_data = json.load(f)

    # Load CMDB and format it
    cmdb_df = pd.read_csv(r"C:\Users\AnirudhVijan\Desktop\project2\Coding\prot5\q\agent_code\data\cmdb_with_languages.csv")
    cmdb_df = cmdb_df[["ID", "App", "Component", "ProgrammingLanguage"]]
    cmdb_text = cmdb_df.to_string(index=False)
    print(2)
    # # Format the logs into a clean string for LLM
    # formatted_logs = ""
    # for entry in parsed_data:
    #     component = entry.get("component", "Unknown")
    #     app = entry.get("App", "Unknown")
    #     issues = entry.get("Issue", [])
    #     severities = entry.get("severity", [])
    #     arrows = entry.get("Arrows", [])

    #     formatted_logs += f"🔧 Component: {component} (App: {app})\n"
    #     issues = entry.get("Issue") or []
    #     severities = entry.get("severity") or []

    #     for i, issue in enumerate(issues):
    #         sev = severities[i] if i < len(severities) else "Unknown"
    #         formatted_logs += f"  • [{sev}] {issue}\n"
    #     for arrow in arrows:
    #         if len(arrow) == 2:
    #             formatted_logs += f"  → Calls: {arrow[0]} → {arrow[1]}\n"
    #     formatted_logs += "\n"
    formatted_logs = ""
    for entry in parsed_data:
        component = entry.get("component", "Unknown")
        app = entry.get("App", "Unknown")
        issues = entry.get("Issue") or []
        severities = entry.get("severity") or []
        arrows = entry.get("Arrows") or []

        formatted_logs += f"🔧 Component: {component} (App: {app})\n"

        for i, issue in enumerate(issues):
            sev = severities[i] if i < len(severities) else "Unknown"
            formatted_logs += f"  • [{sev}] {issue}\n"

        for arrow in arrows:
            if isinstance(arrow, list) and len(arrow) == 2:
                formatted_logs += f"  → Calls: {arrow[0]} → {arrow[1]}\n"

        formatted_logs += "\n"

    print(3)
    # Load prompt from external file
    prompt_template_str = load_file("prompt_task3.txt")
    prompt_template = ChatPromptTemplate.from_template(prompt_template_str)

    # Fill prompt
    messages = prompt_template.format_messages(
        USER_QUESTION=question,
        LOG_CONTENT=formatted_logs,
        CMDB_DB=cmdb_text
    )


    # Call the LLM
    llm = llm_json()
    response = llm.invoke(messages)

    # Postprocess LLM output
    analysis = response.content
    analysis = re.sub(r'\*\*(.*?)\*\*', r'<strong style="color: goldenrod;">\1</strong>', analysis)
    analysis = re.sub(r'^Summary:', r'<strong style="color: goldenrod;">Summary:</strong>', analysis, flags=re.MULTILINE)
    analysis = analysis.replace("\n", "<br>")

    # Save to file
    # with open("analysis_output.txt", "w", encoding='utf-8') as f:
    #     f.write(analysis)

    # timestamp = datetime.now().strftime('%I:%M %p')
    # return { "response": analysis, "timestamp": timestamp }
    return analysis
