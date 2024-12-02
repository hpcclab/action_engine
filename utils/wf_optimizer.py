from .llm import call_llm
from .schemas.workflow import Workflow
from .utilities import escape_json
def wf_optimizer(user_query, task_list):
    SYSTEM_PROMPT = f"""
    Instruction:
    User Request - {user_query}
    ACTIONS - {task_list}

    Given the User Request and a set of actions to accomplish the user order, your task is to create a realistic workflow plan by converting each given action into a state machine defined below.

    [Sequential State]:
    Description - Represents a single unit of action within your workflow.
    When to Use - Use this when you need to call a specific function within your workflow in sequential order.

    [Parallel State]:
    Description - Represents a parallel execution of multiple branches of actions.
    When to Use - Use this when you need to execute multiple tasks or workflows concurrently.

    Your workflow should be in a realistically executable order, considering dependencies and task relationships.

    Example:
    INPUT Example:
    ORDER - Generate 2 PNG format images of a dog and a cat, and convert one image to JPG and the other image to PDF. Send both images in an email.
    ACTIONS -
    [
        {{'task_number': 1, 'task_description': 'Generate animated PNG format image of a dog.'}}, 
        {{'task_number': 2, 'task_description': 'Generate animated PNG format image of a cat.'}}, 
        {{'task_number': 3, 'task_description': 'Convert dog image to JPG.'}}, 
        {{'task_number': 4, 'task_description': 'Convert cat image to PDF.'}},
        {{'task_number': 5, 'task_description': 'Send both images in an email.'}}
    ]

    OUTPUT Example:
    {{
        "Workflow": 
        [
            [Parallel State] - [1, 2],
            [Parallel State] - [3, 4],
            [Sequential State] - [5]
        ]
    }}

    You must only generate the Answer. Your answer must be in JSON format. 
    Your Answer format must start with "```json" and end with "```".
    """

    USER_PROMPT = f"""
    Answer:
    """

    semantic_wf = call_llm(Workflow, "Workflow", escape_json(SYSTEM_PROMPT), escape_json(USER_PROMPT))
    return semantic_wf["Workflow"]

"""
semantic_wf Return Example
[{'state': 'Paralell', 'task_nums': [1, 2]}, {'state': 'Sequential', 'task_nums': [3]}, {'state': 'Sequential', 'task_nums': [4]}]
"""