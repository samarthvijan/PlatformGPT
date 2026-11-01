from langchain.tools import tool
# print(1)
from agent_code.agent.schema import ToolOutput
# print(2)

RAW_LOG_PATH = "agent_code/data/impacted_logs_full.json"
SYSTEM_MAP_PATH = "agent_code/data/components_with_shared_nodes.csv"

def extract_file_paths() -> ToolOutput:
    """
    Returns the absolute paths of raw logs and system mapping files.
    """
    try:
        print(1)
        return ToolOutput(
            status="success",
            message="Log and system mapping paths retrieved.",
            data={
                "raw_log_path": RAW_LOG_PATH,
                "system_map_path": SYSTEM_MAP_PATH,
            }
        
        )
        
    except Exception as e:
        return ToolOutput(
            status="error",
            message=str(e),
            data=None
        )
