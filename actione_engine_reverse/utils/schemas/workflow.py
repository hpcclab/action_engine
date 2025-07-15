from pydantic import BaseModel, Field
from typing import List, Optional, Any

"""
Ultimate Goal from Given User Request
"""
class UltimateOutputDescription(BaseModel):
    ultimate_goal: str = Field(description="The detailed description of ultimate output for a given user request")


"""
Chosen API from API List
"""
class SelectAPI(BaseModel):
    chose_api_name: str = Field(description="The name of the selected API")

"""
Extracted Parameter from Given User Request
"""
class ExtractedParameter(BaseModel):
    name: str = Field(description="The name of the API parameter")
    value: Any = Field(description=f"The extracted value for the parameter with required parameter datatype, or 'None' if not found")

"""
Workflow Optimizer
"""
class State(BaseModel):
    state: str = Field(description="The name of the state type 'sequential' or 'paralell'")
    task_nums: List = Field(description="List of task number in the state, if sequential is the state type a single task number, if paralell multiple numbers")

class Workflow(BaseModel):
    Workflow: List[State] = Field(description="List of info about state and task numbers")

"""
Parameter Output Description
"""
class ParamOutputDescription(BaseModel):
    description: str = Field(description="The description of parameter")

