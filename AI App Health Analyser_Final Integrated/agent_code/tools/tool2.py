import json
import os
from typing import List
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import PromptTemplate
from pydantic import ValidationError

from agent_code.tools.tool1 import extract_file_paths
from agent_code.agent.schema import ToolOutput
from agent_code.output_parsers.tool2_parser import ComponentList
from agent_code.utils.split_json import split_json_file
from agent_code.utils.add_outputs import add_output_json
from agent_code.agent.llm_handler import llm_json


def run_common_llm_tasks() -> ToolOutput:
    """
    Parses logs and extracts correlated application/component info and summaries.
    Returns a ToolOutput with status and message.
    """

    try:
        print("1️⃣ Starting Tool2...")
        extract_result = extract_file_paths()
        print("📄 File paths extracted:", extract_result)

        log_path = extract_result.data.get("raw_log_path")
        if not log_path or not os.path.exists(log_path):
            return ToolOutput(
                status="error",
                message=f"Tool2 failed: Log file not found at path {log_path}",
                data=None
            )

        # Dynamic prompt path
        base_dir = os.path.dirname(__file__)
        prompt_path = os.path.join(base_dir, "../prompts/tool2_prompt.txt")

        with open(prompt_path, "r", encoding="utf-8") as f:
            template = f.read()

        parser = PydanticOutputParser(pydantic_object=ComponentList)
        prompt = PromptTemplate(
            input_variables=["logs"],
            partial_variables={"format_instruction": parser.get_format_instructions()},
            template=template
        )

        # Ensure output file exists and is cleared
        output_path = os.path.join(base_dir, "../data/out_put.json")
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump([], f)

        # Split logs
        chunks = split_json_file(log_path, chunk_size=50)
        print(f"🔍 Total chunks to process: {len(chunks)}")

        llm = llm_json()
        chain = prompt | llm
        successful_chunks = 0

        for i, chunk in enumerate(chunks):
            print(f"🔄 Processing chunk {i + 1}/{len(chunks)}")
            try:
                raw_output = chain.invoke({"logs": json.dumps(chunk)})
                content = raw_output.content.strip()

                if content.startswith("```json"):
                    content = content.removeprefix("```json").removesuffix("```").strip()
                elif content.startswith("```"):
                    content = content.removeprefix("```").removesuffix("```").strip()

                parsed_output = json.loads(content)
                validated_output = ComponentList(root=parsed_output)
                add_output_json(validated_output.root)

                successful_chunks += 1
                print(f"✅ Chunk {i + 1} processed successfully.")

            except (ValidationError, json.JSONDecodeError) as e:
                print(f"⚠️ [Chunk {i + 1}] Skipped due to error: {e}")

        if successful_chunks == 0:
            return ToolOutput(
                status="error",
                message="Tool2 failed: All LLM responses were invalid or failed to parse.",
                data=None
            )

        return ToolOutput(
            status="success",
            message="LLM correlation task completed successfully.",
            data=None
        )

    except Exception as e:
        return ToolOutput(
            status="error",
            message=f"Tool2 failed: {str(e)}",
            data=None
        )
