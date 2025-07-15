from pydantic import BaseModel, Field
from typing import List, Optional

"""
SubTask Division
"""
class Task(BaseModel):
    """Tag the piece of text with particular info."""
    subtask_number: int = Field(description="The number of subtask divided from the given task")
    subtask_description: str = Field(description="The detailed description of the subtask")

class Tasks(BaseModel):
    Tasks: List[Task] = Field(description="List of info about subtasks")


"""
API Identifier
"""
class Task_Api(BaseModel):
    subtask_number: int = Field(description="The number of subtask divided from the given task")
    subtask_description: str = Field(description="The detailed description of the subtask")
    selected_API_name: str = Field(description="The name of selected API")

class Task_Apis(BaseModel):
    Task_Apis: List[Task_Api] = Field(description="Information about subtasks and selected API")

"""
Workflow Optimizer
"""
class State(BaseModel):
    state: str = Field(description="The name of the state type 'sequential' or 'paralell'")
    task_nums: List = Field(description="List of task number in the state, if sequential is the state type a single task number, if paralell multiple numbers")

class Workflow(BaseModel):
    Workflow: List[State] = Field(description="List of info about state and task numbers")

"""
Data Dependency Management
"""
class TaskOutputDescription(BaseModel):
    task_output_description: str = Field(description="A task specialized api output desciption")

class DependentParam(BaseModel):
    param_name: str = Field(description="A name of the parameter if not any add empty string")
    param_value: str = Field(description="task number like t1 or t2 as a value of the parameter if not any add empty string")

class DependentParams(BaseModel):
    DependentParams: List[DependentParam] = Field(description="List of info about parameters")

"""
Missing API Message
"""
class MissingMessage(BaseModel):
    message: str = Field(description="A message to inform user about missing function")



#************For Evaluation******************
"""
End-to-End
"""

# ActionEngine without Compiler
class ArgoYAML(BaseModel):
    extracted_yaml: str = Field(description="The extracted yaml code")
