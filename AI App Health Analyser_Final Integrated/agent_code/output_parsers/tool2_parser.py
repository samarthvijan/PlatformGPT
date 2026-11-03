from typing import Optional, List
from pydantic import BaseModel, Field
import json

class Component(BaseModel):
    component: str = Field(
        description="Name of the component generating the logs (e.g., API Gateway, Auth Service)."
    )
    App: str = Field(
        description="Name of the application or microservice this component belongs to."
    )
    Issue: Optional[List[str]] = Field(
        default=None,
        description="List of summarized issues or errors associated with this component, if any but in detail."
    )
    severity: Optional[List[str]] = Field(
        default=None,
        description="List of Severity level of the all the issues (e.g., info, warning, critical)."
    )
    Arrows: Optional[List[List[str]]] = Field(
        default=None,
        description=(
            "List of downstream components or services this component interacts with. "
            "Used to describe the call flow in the deployment architecture."
        )
    )
    server: Optional[str] = Field(
        default=None,
        description="Name of the server or server id"
    )


from pydantic import RootModel

class ComponentList(RootModel[List[Component]]):
    pass
