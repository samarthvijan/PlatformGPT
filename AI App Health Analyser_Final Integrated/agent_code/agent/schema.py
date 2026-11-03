# agent/schemas.py
from pydantic import BaseModel
from typing import Optional, List


class ToolOutput(BaseModel):
    status: str  # "success" or "error"
    message: Optional[str] = None
    data: Optional[dict] = None
