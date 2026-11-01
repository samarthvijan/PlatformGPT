from langchain_core.tools import Tool
from langchain.tools import StructuredTool
from pydantic import BaseModel
from typing import Optional
from agent_code.agent.schema import ToolOutput
import json
from langchain.prompts import PromptTemplate
from agent_code.agent.llm_handler import llm_json
from agent_code.tools.tool2 import run_common_llm_tasks
import os

output_path="agent_code/data/out_put.json"
# sumary
class SummarizerInput(BaseModel):
    query: str
    app: Optional[str] = None
    component: Optional[str] = None

def run_task1_log_summarization_v2(query: str, app: Optional[str] = None, component: Optional[str] = None):
    try:
        if not os.path.exists(output_path):
            print("⚙️ output_path missing, calling run_common_llm_tasks()")
            run_common_llm_tasks()
        if not os.path.exists(output_path):
            print("⚙️ output_path missing, calling run_common_llm_tasks()")
            run_common_llm_tasks()

        with open('agent_code/prompts/tool3_prompt2.txt', encoding='utf-8') as f:
            template = f.read()

        with open(output_path, encoding='utf-8') as f:
            json1 = json.load(f)

        prompt = PromptTemplate(
            input_variables=["json", "query"],
            template=template
        )

        json1_str = json.dumps(json1)
        llm = llm_json()
        chain = prompt | llm

        response = chain.invoke({'json': json1_str, 'query': query})

        summary_path = "agent_code/outputs/tool3_summaries.txt"
        with open(summary_path, "w", encoding="utf-8") as f:
            f.write(response.content)

        return {
            "status": "success",
            "message": f"Summarization completed. Summaries saved to {summary_path}",
            "data": response.content
        }

    except Exception as e:
        return {
            "status": "error",
            "message": f"Tool3 failed: {str(e)}",
            "data": None
        }

    # summaries = []
    # try:
        # print(1)
    #     output_path = "agent_code/data/out_put.json"
    #     if not os.path.exists(output_path):
    #         run_common_llm_tasks()
    #     # print(2)
    #     with open(output_path, 'r') as f:
    #         # raw = f.read()
    #         # print("Raw contents:", raw)
    #         # f.seek(0)
    #         data = json.load(f)
    #         # print(4)
    #     # print(data)
    #     for entry in data:
    #         # print(entry)
    #         entry_app = entry.get("App", "").lower()
    #         entry_comp = entry.get("component", "").lower()
    #         summary = entry.get("Issue")

    #         if app and component:
    #             if entry_app == app.lower() and entry_comp == component.lower() and summary:
    #                 summaries.append(f"{entry_app}.{entry_comp}: {summary}")
    #         elif app:
    #             if entry_app == app.lower() and summary:
    #                 summaries.append(f"{entry_app}.{entry_comp}: {summary}")
    #         elif summary:
    #             summaries.append(f"{entry_app}.{entry_comp}: {summary}")
    #     # print(3)
    #     print(summaries)
    #     if not summaries:
    #         return ToolOutput(
    #             status="success",
    #             message="Everything is fine in the {app} , {component}.",
    #             data=None
    #         )

    #     with open("agent_code/prompts/tool3_prompt.txt", 'r') as f:
    #         template = f.read()

    #     prompt = PromptTemplate(
    #         input_variables=["summaries", 'query'],
    #         template=template
    #     )
    #     # print(query)

    #     llm = llm_json()
    #     chain = prompt | llm

    #     combined_summaries = "\n".join(summaries)
    #     result = chain.invoke({'summaries': combined_summaries, 'query': query})
    #     # print(type(result.content))
    #     summary_path = "agent_code/outputs/tool3_summaries.txt"
    #     with open(summary_path, "w", encoding="utf-8") as f:
    #         f.write(result.content)

    #     return {
    #         "status": "success",
    #         "message": f"Summarization completed. Summaries saved to {summary_path}",
    #         "data": result.content
    #     }


    # except Exception as e:
    #     return {
    #         'status':"error",
    #         'message':f"Tool3 failed: {str(e)}",
    #         'data':None
    #     }

from langchain.tools import StructuredTool

run_task1_log_summarization_tool = StructuredTool.from_function(
    name="SystemHealthAnalyzer",  # ✅ Better, more intuitive name
    description=(
        "Analyzes the health of the system or any specific app/component using logs. "
        "Use this tool when the user asks about system issues, health status, or anything possibly wrong, "
        "even if they don't explicitly mention logs."
    ),
    func=run_task1_log_summarization_v2,
    args_schema=SummarizerInput
)

