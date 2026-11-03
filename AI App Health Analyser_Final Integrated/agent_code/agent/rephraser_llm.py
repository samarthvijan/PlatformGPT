from langchain.prompts import PromptTemplate
from agent_code.agent.llm_handler import llm_json
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage

def format_chat_history(messages):
    if not messages:
        return "No prior messages. Assume user is asking about a system or application."
    formatted = []
    for msg in messages:
        if isinstance(msg, HumanMessage):
            formatted.append(f"Human: {msg.content}")
        elif isinstance(msg, AIMessage):
            formatted.append(f"AI: {msg.content}")
        elif isinstance(msg, SystemMessage):
            formatted.append(f"System: {msg.content}")
    return "\n".join(formatted)

def rephrase_input(chat_history, followup):
    llm = llm_json()
    # print(chat_history)
    # print(followup)
    prompt = PromptTemplate.from_template("""
You are given the previous conversation between a user and an AI assistant.
Now the user asked a follow-up question that lacks context.

Rewrite the user's follow-up question into a standalone question using the past messages.
Sometimes My chat history may be none then just make the query understandable and more specific example query: is everything fine with app1 response Analysis logs and tell if everything is fine with App1 . Second example Is everything fine with my system/software response Analysis every log and tell the problems with every system
If user query have words like detail and else then only use word detail otherwise use consice 
make queries more specific so that llm can understand and also my llm have no memory so dont use words like previous analysis 

                                          
NOTE : Always mention are you talking about application or system
Prioritize the events from the last logs more than from the intiall ones
Chat history:
{chat_history}

Follow-up question:
{question}

Standalone question:
""")

    formatted_history = format_chat_history(chat_history.chat_memory.messages)


    formatted_prompt = prompt.format(chat_history=formatted_history, question=followup)
    # print("==== Prompt Sent to LLM ====")
    # print(formatted_prompt)

    response = llm.invoke(formatted_prompt)
    # print("==== Response from LLM ====")
    # print(response.content)

    return response.content if hasattr(response, "content") else str(response)
