import json
from typing import List

def split_json_file(input_path: str, chunk_size: int) -> List[List[dict]]:

    with open(input_path, 'r') as f:
        try:
            data = json.load(f)
        except json.JSONDecodeError:
            f.seek(0)
            data = [json.loads(line) for line in f if line.strip()]

    chunks = [data[i:i + chunk_size] for i in range(0, len(data), chunk_size)]
    return chunks
