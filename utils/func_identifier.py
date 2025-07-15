import time
import csv
import json
from dotenv import load_dotenv
import os

from .llms import call_llm
from .schemas.workflow import Task_Apis
from .utilities import escape_json

from langchain_community.vectorstores import FAISS
from langchain.embeddings import OpenAIEmbeddings
filepath = "./db/api_info/"
filename = filepath + 'api_information.json'
NO_FUNC = False

# Load environment variables
load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")

if not os.getenv("OPENAI_API_KEY"):
    os.environ["OPENAI_API_KEY"] = openai_api_key

embedding_function = OpenAIEmbeddings(model="text-embedding-3-large")
loaded_faiss = FAISS.load_local(filepath + 'vectordb/LangChain_FAISS/', embedding_function, "api_vec", allow_dangerous_deserialization=True)

# def read_json_to_dict(filename):
#     api_info = []
#     with open(filename, 'r') as file:
#         for line in file:
#             api_info.append(json.loads(line))

#     return api_info
# import json

def read_json_to_dict(filename):
    """
    Reads a JSON file that contains a single JSON array and returns it as a list of dictionaries.
    """
    with open(filename, 'r') as file:
        api_info = json.load(file)
    return api_info

def find_topk_functions(query, api_info, k):
    """
    Find the top-k functions from the vector database using the user query.
    """
    faiss_obj_path = "./db/api_info/vectordb/LangChain_FAISS/"
    loaded_faiss = FAISS.load_local(faiss_obj_path, embedding_function, "api_vec", allow_dangerous_deserialization=True)
    results_with_scores = loaded_faiss.similarity_search_with_score(query, k=k)

    # results_with_scores is a list of (Document, score) tuples. Access the Document at index 0.
    selected_id = [doc.metadata['id'] for doc, score in results_with_scores]
    
    # Create a dictionary for quick lookups of functions by their ID
    api_info_by_id = {api['Id']: api for api in api_info if 'Id' in api}
    
    # Retrieve the full function details by looking up the ID
    topk_functions = [api_info_by_id[j] for j in selected_id if j in api_info_by_id]
    
    return topk_functions

def retry_find_func(task_description: str, api_info, user_query, subtask):
    SYSTEM_PROMPT = """
    You will be given a main objective, sub-task infomation, and available API information.
    Let's think step by step.
    Your task is to select the most suitable API for the given subtask from available APIs, and extract information.
    Please compare task_descriptoin and API information carefully and choose the API. 
    
    This task was found no function can be applicable, and now we are double checking. 
    Make sure to select the API if the task matches the API description.
    """

    topk_functions = find_topk_functions(model_name, task_description, api_info, 10)
    names = [func["name"] for func in topk_functions]
    USER_PROMPT = f"""
        Objective: {user_query},
        Sub-task: {subtask},
        Available APIs: {topk_functions}
        """
    response = call_llm(model_name, Task_Apis, "Task_Apis", SYSTEM_PROMPT, escape_json(USER_PROMPT))
    return response, topk_functions, names

def func_identifier(model_name, task_list, user_query, db_name="api_vec"):
    #load faiss
    global NO_FUNC
    api_info = read_json_to_dict(filename)
    
    """
    Use this prompt for no function found edge case
    Also, add the ", If none is applicable N/A" to Task_Api schema
    Example:
    """
    # SYSTEM_PROMPT = """
    # You will be given a main objective, sub-task info, and available APIs' information.
    # Let's think step by step.
    # Your task is to select an API from available APIs that is most suitable for the given subtask and extract information.
    # Please compare task_descriptoin and API information carefully and choose the API. 
    
    # Make sure to select the API if the task matches the API description.
    # If any of available APIs are not applicable to the subtask, make sure to return N/A.
    # """

    non_func_list, selected_functions = [], []
    for i in range(len(task_list)):
    # for i in range(0, 1): #Test
        topk_functions = find_topk_functions(task_list[i]["subtask_description"], api_info, 40)
        # Extract only the 'Id', 'name', and 'summary' fields for each item
        extracted_data = [{'name': item['name'], 'summary': item['summary']} for item in topk_functions]
    
        names = [func["name"] for func in topk_functions]
        SYSTEM_PROMPT = f'''
            Instruction: 
            Objective: {user_query},
            Subtask: {task_list[i]},
            Available APIs: {extracted_data}

            Given a Subtask, and Available APIs'. 
            Your task:
            1. Select one API from available APIs that is most suitable for the given subtask.
            2. Extract the information of "subtask_number", "subtask_description", and "selected_API_name".
            Please compare given subtask_description and API information carefully and select an API. 
            
            You must select one API that is the most closest, so please make sure that one API is selected from the given available APIs.  
            
            Below are examples of output format:

            Example 1:
            {{
                "Task_Apis": [
                    {{
                    "subtask_number": [extracted subtask number here],
                    "subtask_description": [extracted subtask description here],
                    "selected_API_name": [extracted selected API name here]
                    }}
                ]
            }}

            You must only generate the Answer. Your answer must be in JSON format. 
            Your Answer format must start with "```json" and end with "```".
        '''


        USER_PROMPT = f"""            
            Answer:"""

        response = call_llm(model_name, Task_Apis, "Task_Apis", escape_json(SYSTEM_PROMPT), escape_json(USER_PROMPT))
        try:
            response = response["Task_Apis"]
        except:
            print("-----", response)
        try:
            if response[0]["selected_API_name"] == "N/A":
                response, topk_functions, names = retry_find_func(model_name, task_list[i]["task_description"], api_info, user_query, task_list[i])

            if response[0]["selected_API_name"] in names:
                for func in topk_functions:
                    if func["name"] == response[0]['selected_API_name']:
                        selected_func = func.copy()  # Make a copy to avoid mutating the original
                        selected_func["task_num"] = int(response[0]["subtask_number"])
                        selected_func["task_description"] = response[0]["subtask_description"]
                        selected_functions.append(selected_func)
            else:
                default_func = {
                    "name": response[0]['selected_API_name'],
                    "task_num": int(response[0]["subtask_number"]),
                    "task_description": response[0]["subtask_description"]
                }
                selected_functions.append(default_func)
                non_func_list.append(default_func)
                NO_FUNC = True

        except:
            top_1_func = find_topk_functions(task_list[i]["subtask_description"], api_info, 1)
            for func in top_1_func:
                selected_func = func.copy()  # Make a copy to avoid mutating the original
                selected_func["task_num"] = int(response[0]["subtask_number"])
                selected_func["task_description"] = response[0]["subtask_description"]
            selected_functions.append(selected_func)
            return selected_functions, NO_FUNC, non_func_list

    return selected_functions, NO_FUNC, non_func_list

    """
    selected_functions example return value
[
    {
        "Id": "1",
        "name": "tti_Animation_Art",
        "input_parameters_with_datatype": [
            {
                "name": "prompt",
                "datatype": "string"
            }
        ],
        "input_description": "The input parameter for this API is a user prompt in string data type.",
        "output_data_type": "binary_image_file",
        "output description": "Generated animation image as a binary_image_file",
        "description": "This API takes a user prompt and generates an image in animation style using a pre-trained model. The user needs to provide a prompt in string format and the API will return the generated animation image as a response in the form of a FileResponse.",
        "method": "POST",
        "url": "",
        "task_num": 1,
        "task_description": "Generate animated image of a dog."
    },
    {
        "Id": "1",
        "name": "tti_Animation_Art",
        "input_parameters_with_datatype": [
            {
                "name": "prompt",
                "datatype": "string"
            }
        ],
        "input_description": "The input parameter for this API is a user prompt in string data type.",
        "output_data_type": "binary_image_file",
        "output description": "Generated animation image as a binary_image_file",
        "description": "This API takes a user prompt and generates an image in animation style using a pre-trained model. The user needs to provide a prompt in string format and the API will return the generated animation image as a response in the form of a FileResponse.",
        "method": "POST",
        "url": "",
        "task_num": 2,
        "task_description": "Generate animated image of a cat."
    },
    {
        "name": "N/A",
        "task_num": 3,
        "task_description": "Create a video using the animated images of dog and cat."
    },
    {
        "Id": "14",
        "name": "send_email",
        "input_parameters_with_datatype": [
            {
                "name": "sender_address",
                "datatype": "string"
            },
            {
                "name": "receiver_address",
                "datatype": "string"
            },
            {
                "name": "message_text",
                "datatype": "string"
            },
            {
                "name": "message_subject",
                "datatype": "string"
            },
            {
                "name": "file",
                "datatype": "binary_image_file"
            }
        ],
        "input_description": "The input for this API is an sender email address, receiver email address, message, and subject in string, and image file in binary format ",
        "output_data_type": "string",
        "output description": "Message of success or failure of the email",
        "description": "The objective of this API endpoint is to send an email message. The endpoint accepts various parameters including the sender's email address, receiver's email address, optional message text, optional message subject, and an optional file attachment.",
        "method": "POST",
        "url": "",
        "task_num": 4,
        "task_description": "Send the video via email."
    }
]

    """