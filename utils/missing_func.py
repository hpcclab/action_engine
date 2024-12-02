import json
from .llm import call_llm

from .schemas.workflow import MissingMessage
from .utilities import escape_json

def missing_func(task):
    SYSTEM_PROMPT = '''
    You will be given a task that was not completed because there was not API that can proceed the task. 
    Your goal is to generate a message to inform user about missing function including information about how many function a missing and whats kind of function needs to be constracted to proceed further, and extract infomation.
    '''

    USER_PROMPT = f"""
        Task: {task}
    """

    # Loading the response as a JSON object
    response = call_llm(MissingMessage,"MissingMessage" ,SYSTEM_PROMPT, escape_json(USER_PROMPT))

    return response["message"]