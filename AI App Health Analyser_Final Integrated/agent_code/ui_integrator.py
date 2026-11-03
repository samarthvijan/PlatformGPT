# main.py
# print(1)
from agent_code.agent.react_agent import get_react_agent
# print(2)
from agent_code.agent.rephraser_llm import rephrase_input


def save_memory_to_textfile(memory, file_path="agent_code/data/chat_memory_log.txt"):
    with open(file_path, "w", encoding="utf-8") as f:
        for msg in memory.chat_memory.messages:
            role = getattr(msg, "type", msg.__class__.__name__.replace("Message", ""))
            content = getattr(msg, "content", str(msg))
            f.write(f"{role}: {content}\n")
    print(f"✅ Chat history saved to {file_path}")



def analysis(prompt):
    agent = get_react_agent()
    chat_history = agent.memory
    # print(chat_history)

    query = rephrase_input(chat_history=chat_history,followup= prompt)
    print(query)
    try:
        response = agent.invoke({"input": query})
        output=response['output']
    
    except Exception as e:
        output=f"\n⚠️ Error: {e}"
    chat_history=agent.memory
    # print(chat_history)
    save_memory_to_textfile(chat_history)
    return output




