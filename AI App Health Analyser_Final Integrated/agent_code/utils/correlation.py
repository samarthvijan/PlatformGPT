import pandas as pd
import json
import os

def correlate_logs_with_servers(system_mapping_path:str):


    df = pd.read_csv(system_mapping_path)
    df.columns = df.columns.str.strip()

    expected_cols = {'App', 'Component', 'NodeType'}
    if not expected_cols.issubset(df.columns):
        raise ValueError(f"Excel file must have columns: {expected_cols}")

    comp_to_server = {
        f"{row['App'].strip()}-{row['Component'].strip()}": row['NodeType'].strip()
        for _, row in df.iterrows()
    }

    with open('agent_code\data\out_put.json', "r") as f:
        logs = json.load(f)

    for log in logs:
        app = log.get("App", "").strip()
        component = log.get("component", "").strip()
        key = f"{app}-{component}"
        if not log.get("server"):
            log["server"] = comp_to_server.get(key, "Unknown")

    save_path ='agent_code\data\enriched_logs.json'
    with open(save_path, "w") as f:
        json.dump(logs, f, indent=2)

    # return f"✅ Logs enriched and saved to {save_path}"
