from langchain.agents import initialize_agent, AgentType
from agent_code.tools.tool1 import extract_file_paths
# print(1)
from agent_code.tools.tool2 import run_common_llm_tasks
from agent_code.tools.tool3 import run_task1_log_summarization_tool  # ✅ Use the structured version
from agent_code.tools.tool4 import generate_deployment_diagram
from agent_code.tools.tool5 import suggest_fixes_tool
from agent_code.agent.llm_handler import llm_json
from langchain_core.tools import Tool
from langchain.memory import ConversationBufferMemory
from langchain.memory import ConversationBufferMemory
from langchain.schema import AIMessage, HumanMessage, SystemMessage
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage

def load_memory_from_textfile(file_path="agent_code/data/chat_memory_log.txt"):
    messages = []
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
            if not lines:
                print("Memory file is empty. Starting fresh.")
            else:
                for line in lines:
                    line = line.strip()
                    if not line or ": " not in line:
                        continue

                    role, content = line.split(": ", 1)
                    role = role.strip().lower()

                    if role == "human":
                        messages.append(HumanMessage(content=content.strip()))
                    elif role == "ai":
                        messages.append(AIMessage(content=content.strip()))
                    elif role == "system":
                        messages.append(SystemMessage(content=content.strip()))
    except Exception as e:
        print(f"❌ Error reading memory file: {e}")

    memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
    memory.chat_memory.messages = messages
    return memory


def get_react_agent():
    # Load previous chat memory
    memory = load_memory_from_textfile()

    # 🧠 Add System Role Description
    system_description = """
You are an expert system health and architecture analysis assistant and also you have power to help people fix there problems with the help of code. 
You work for a company that specializes in log analysis and intelligent diagnostics and also sometimes fix the user issues and also generate code if asked. 
nOTE: Very Very Important . So when you are analysisng and summari
You are not allowed to say things like 'investigation required' or 'please look into it' as that violates our policy.
--Note If a user asks detailed response give hime the detailed one
- If a tool returns a detailed response (especially SystemHealthAnalyzer), you must return a very detailed answer about 100 words.
- Always be technical and concise unless the query includes words like 'detailed', 'explain', or 'elaborate', in which case provide an in-depth technical breakdown.

-Note: Note:very very important If the user asks only detailed response only give him detailed reponse but make sure that response should not include fixes and also in detail about 100 words 
But if query doesnn't contains workd like detail give an brief response which includes component facing issue app which it belongs to and  how severe the issue is 

"""

    # Inject the system message once, only if not already in memory
    if not any(isinstance(msg, SystemMessage) for msg in memory.chat_memory.messages):
        memory.chat_memory.messages.insert(0, SystemMessage(content=system_description.strip()))

    llm = llm_json()

    tools = [
        run_task1_log_summarization_tool,
        Tool(
            name="DeploymentDiagramBuilder",
            func=generate_deployment_diagram,
            description=(
                "Generates a deployment diagram showing which component calls which. "
                "Use when asked about app communication or architecture."
            )
        )
    ]

    agent = initialize_agent(
        tools=tools,
        llm=llm,
        agent=AgentType.STRUCTURED_CHAT_ZERO_SHOT_REACT_DESCRIPTION,
        memory=memory,
        verbose=True,
        SystemMessage=system_description, 
        handle_parsing_errors=True
    )

    return agent
