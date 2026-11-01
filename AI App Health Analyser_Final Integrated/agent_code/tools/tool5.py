from agent_code.tools.tool3 import run_task1_log_summarization_tool
from agent_code.agent.llm_handler import llm_json
from langchain.tools import StructuredTool
from langchain.prompts import PromptTemplate
from typing import Optional
from pydantic import BaseModel
import os
import json
import json
import re
import json
import re

def clean_llm_response(raw: str) -> str:
    """Remove ```json or ```yaml fences from LLM output."""
    raw = raw.strip()
    if raw.startswith("```json"):
        raw = raw[len("```json"):].strip()
    if raw.startswith("```yaml"):
        raw = raw[len("```yaml"):].strip()
    if raw.endswith("```"):
        raw = raw[:-3].strip()
    return raw

def clean_code_snippet_field(snippet: str) -> str:
    """Remove internal code block markers from the YAML snippet."""
    snippet = snippet.strip()
    if snippet.startswith("```yaml"):
        snippet = snippet[len("```yaml"):].strip()
    if snippet.endswith("```"):
        snippet = snippet[:-3].strip()
    return snippet

def format_llm_result_for_agent(raw_output) -> dict:
    """Parses, cleans, and wraps LLM result in LangChain-compatible format."""
    try:
        raw_content = raw_output.content if hasattr(raw_output, 'content') else raw_output
        cleaned = clean_llm_response(raw_content)
        parsed = json.loads(cleaned)

        # Optional: clean nested fields like code_snippet
        if 'code_snippet' in parsed:
            parsed['code_snippet'] = clean_code_snippet_field(parsed['code_snippet'])

        return {
            "status": "Success",
            "message": "Suggestion done properly",
            "agent_output": {
                "action": "Final Answer",
                "action_input": parsed
            }
        }

    except Exception as e:
        return {
            "status": "Fail",
            "message": f"Parsing error: {str(e)}",
            "agent_output": {
                "action": "Final Answer",
                "action_input": {
                    "root_cause": "Unable to parse structured response.",
                    "fix_suggestions": [raw_output.content if hasattr(raw_output, 'content') else str(raw_output)],
                    "code_snippet": ""
                }
            }
        }


class FixesInput(BaseModel):
    query: str
    app: Optional[str] = None
    component: Optional[str] = None

def rephrase(query):
    llm = llm_json()
    template = '''You are a input rephraser which helps me to understand better about the user demands.
Our company mainly focus on analysing logs but your work is to return an output paraphrased in such a way it is easily understood by the agent.    
Note: If you receive a query which asks to fix the issue then output a query like "summarize the problem" since our company only focuses on analysing logs not fixing the problem.
Note: Just return me the query; don't respond in a way like "I understand". This is the query:
Query:
{query}
    '''
    prompt = PromptTemplate(input_variables=['query'], template=template)
    formatted_prompt = prompt.format(query=query)
    result = llm.invoke( formatted_prompt)
    return result.content

# def suggest_fixes(query: str, app: Optional[str] = None, component: Optional[str] = None):
#     rephrased_query = rephrase(query)
#     # print("🔁 Rephrased Query:\n", rephrased_query)

#     summary_issue = run_task1_log_summarization_tool.invoke({
#         "query": rephrased_query,
#         "app": app,
#         "component": component
#     })

#     summary_issue = summary_issue.get("data", "No summary available")

#     file_path = r"C:\Users\AnirudhVijan\Desktop\project2\Coding\prot4\q\agent_code\prompts\tool5_prompt.txt"
#     with open(file_path, 'r', encoding='utf-8') as f:
#         template = f.read()

#     prompt = PromptTemplate(
#         input_variables=['query', 'app', 'component', 'issue_summary'],
#         template=template
#     )
#     formatted_prompt = prompt.format(
#         query=query,
#         app=app,
#         component=component,
#         issue_summary=summary_issue
#     )

#     llm = llm_json()
#     result = llm.invoke(formatted_prompt)
#     # print("🧠 LLM Response:\n", result.content)
#     return result.content
def suggest_fixes(query: str, app: Optional[str] = None, component: Optional[str] = None):
    rephrased_query = rephrase(query)
    print(rephrased_query)
    summary_issue = run_task1_log_summarization_tool.invoke({
        "query": rephrased_query,
        "app": app,
        "component": component
    })

    summary_issue = summary_issue.get("data", "No summary available")

    file_path = r"C:\Users\AnirudhVijan\Desktop\project2\Coding\prot4\q\agent_code\prompts\tool5_prompt.txt"
    with open(file_path, 'r', encoding='utf-8') as f:
        template = f.read()

    prompt = PromptTemplate(
        input_variables=['query', 'app', 'component', 'issue_summary'],
        template=template
    )
    formatted_prompt = prompt.format(
        query=query,
        app=app,
        component=component,
        issue_summary=summary_issue
    )

    llm = llm_json()
    result = llm.invoke(formatted_prompt)
    final_result = format_llm_result_for_agent(result)
    agent_output = final_result['agent_output']  # <- use this with your agent
    print(final_result['status'], final_result['message'])

    return agent_output

    # result1={}
    # try:
    #     raw_response = result.content
    #     cleaned_response = clean_llm_response(raw_response)
        
    #     response_json = json.loads(cleaned_response)
    #     response_json['code_snippet'] = clean_code_snippet(response_json.get('code_snippet', ''))

    #     result1 = {
    #         'status': 'Success',
    #         'message': 'Suggestion done properly',
    #         'data': response_json
    #     }
    #     print(result1)
    # except Exception:
    #     # Fallback: return everything as plain text to avoid crashing
    #     response = {
    #         "root_cause": "Unable to parse structured response.",
    #         "fix_suggestions": [result.content],
    #         "code_snippet": ""
    #     }
    

    # return result1

suggest_fixes_tool = StructuredTool.from_function(
    name="SuggestFixes",
    description=(
         "Suggests root causes, potential fixes, and code snippets based on logs. "
        "Use this tool when the user asks to fix communication issues, reduce server load, or requests code for resolution. "
        "Prefer this tool when the user mentions specific apps or components along with a desire for actionable or code-based solutions."
    ),
    func=suggest_fixes,
    args_schema=FixesInput
)
