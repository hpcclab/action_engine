from .llms import call_llm
from .utilities import escape_json
from .schemas.workflow import UltimateOutputDescription, SelectAPI, ExtractedParameter, ParamOutputDescription


import json
from dotenv import load_dotenv
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import OpenAIEmbeddings
import os
filepath = "./db/api_info/"
filename = filepath + 'api_information.json'
# Load environment variables
load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")

if not os.getenv("OPENAI_API_KEY"):
    os.environ["OPENAI_API_KEY"] = openai_api_key

embedding_function = OpenAIEmbeddings(model="text-embedding-3-large")
loaded_faiss = FAISS.load_local(filepath + 'vectordb/LangChain_FAISS_output_db/', embedding_function, "api_vec", allow_dangerous_deserialization=True)

def read_json_to_dict(filename):
    """
    Reads a JSON file that contains a single JSON array and returns it as a list of dictionaries.
    """
    with open(filename, 'r') as file:
        api_info = json.load(file)
    return api_info

def find_topk_functions(task: str, k=5) -> list:
    api_info = read_json_to_dict(filename)
    top_k = loaded_faiss.similarity_search_with_score(task, k)
    selected_id = [top_k[j][0].metadata["id"] for j in range(k)]
    topk_functions = [api_info[j-1] for j in selected_id]
    return topk_functions

def determine_output(model, user_request) -> str:
    SYSTEM_PROMPT = f'''
    Instruction: 
    User Request: {user_request}

    "You are a highly intelligent and efficient assistant designed to interpret user requests "
    "and determine the ultimate output for their needs. Your task is to analyze the user's input, infer their intent, "
    "and produce a concise, clear description of the expected output.\n\n"
    "### Guidelines:\n"
    "1. Always infer the user's intent from their request and focus on their desired outcome.\n"
    "2. Return a single sentence describing the nature of the final output they want.\n"
    "3. If the request is a question, specify what the user wants to learn or understand.\n"
    "4. If the request is a command or instruction, summarize the action or result they want.\n"
    "5. If the request is vague or ambiguous, return a clarification prompt asking for more details.\n"
    "6. The output must not directly restate the user's input but instead interpret it into a meaningful action or response.\n\n"
    "### Examples:\n"
    "- Input: 'How do I bake a cake?'\n"
    "  Output: 'A step-by-step guide to baking a cake.'\n"
    "- Input: 'Generate a motivational quote about perseverance.'\n"
    "  Output: 'A motivational quote about perseverance.'\n"
    "- Input: 'I need help but don’t know what to ask.'\n"
    "  Output: 'A request for clarification on what assistance the user needs.'\n"
    "- Input: 'Explain quantum mechanics.'\n"
    "  Output: 'An explanation of the basic principles of quantum mechanics.'"

    You must only generate the Answer. Your answer must be in JSON format. 
    Your Answer format must start with "```json" and end with "```".
    '''

    USER_PROMPT = f"""
    Answer: 
    """
    response = call_llm(model, UltimateOutputDescription, "UltimateOutputDescription" ,escape_json(SYSTEM_PROMPT), escape_json(USER_PROMPT))

    if "ultimate_goal" in response:
        return response["ultimate_goal"]
    return response


def find_apis_by_output_description(output_description: str) -> list:
    """
    Searches the API repository for APIs that produce the given output description.
    Returns a list of candidate APIs.
    """
    top_k_functions = find_topk_functions(output_description)
    return top_k_functions


def select_best_api(model, api_list, final_output_description) -> dict:
    """
    Given a list of candidate APIs and context (e.g., user's request), 
    select the most appropriate API.
    """
    api_output_list = [{"api_name": api["name"], "api_function": api["summary"], "api_output": api["output_parameters_with_datatype"][0]}for api in api_list]

    SYSTEM_PROMPT = f'''
    Instruction: 
    We have 5 APIs:
    {api_output_list}

    If someone is saying: {final_output_description}
    Which final API should we use for this instruction? Only return API code.
    Only return one word!

    You must only generate the Answer. Your answer must be in JSON format. 
    Your Answer format must start with "```json" and end with "```".
    '''

    USER_PROMPT = f"""
    Answer: 
    """
    response = call_llm(model, SelectAPI, "SelectAPI" ,escape_json(SYSTEM_PROMPT), escape_json(USER_PROMPT))

    if "chose_api_name" in response:
        selected_api_name = response["chose_api_name"]
    else:
        """
        TODO:
        If not OpenAI gpt api, system require to create program to extract content from response
        due to lack of no common method to extract structured output for all open source model
        """
        return None
    for api in api_list:
        if api["name"] == selected_api_name:
            return api
        
    return response


def can_fulfill_directly(model, user_request, param):
    """
    Checks if the user request provides the necessary input directly for the given parameter.
    Uses LLM or other logic.
    :param user_request: The user's textual request.
    :param param: The parameter definition (dict) with keys like 'name', 'description', 'datatype'.
    :return: The extracted value if found, otherwise None.
    """
    # Prepare system and user prompts
    SYSTEM_PROMPT = f"""
    Instruction: 
    User Input: {user_request}
    Here is the parameter information:
    - Name: {param['name']}
    - Description: {param['description']}
    - Expected Data Type: {param['datatype']}

    You are a highly capable assistant for extracting structured data from unstructured user input.
    Your task is to analyze the user's input and extract a value for a specified parameter, if possible.

    Only extract the value if it is explicitly or implicitly mentioned in the user's input. Return "None" if it cannot be found.

    You must only generate the Answer. Your answer must be in JSON format. 
    Your Answer format must start with "```json" and end with "```".
    """
    
    USER_PROMPT = f"""
    Answer: 
    """

    response = call_llm(model, ExtractedParameter, "ExtractedParameter" ,escape_json(SYSTEM_PROMPT), escape_json(USER_PROMPT))

    return response

def get_param_output_description(model, param):
    """
    Returns the output description needed to fulfill this parameter.
    This might come from API schema or other metadata.
    """
    SYSTEM_PROMPT = f"""
    You are an expert assistant designed to understand structured and unstructured data.
    Your task is to generate an effective output description for an API search. The output description should
    clearly specify what is required to fulfill a specific parameter.

    Here is the context:
    - Parameter Name: {param['name']}
    - Parameter Description: {param['description']}
    - Parameter Data Type: {param['datatype']}


    Generate a concise and clear output description that specifies what needs to be produced or retrieved to fulfill the parameter.

    You must only generate the Answer. Your answer must be in JSON format. 
    Your Answer format must start with "```json" and end with "```".
    """
    
    USER_PROMPT = f"""
    Answer:
    """

    response = call_llm(model, ParamOutputDescription, "ParamOutputDescription" ,escape_json(SYSTEM_PROMPT), escape_json(USER_PROMPT))

    return response

def create_workflow(api: dict, param_values: dict) -> str:
    """
    Constructs a string representing a Python-like function call, with sub-workflows
    nested if needed.
    """
    function_name = api["name"]
    args = []
    
    for key, value in param_values.items():
        if isinstance(value, str):
            # If it looks like a subcall (contains '(') -> insert as-is
            if "(" in value and value.endswith(")"):
                args.append(f"{key}={value}")
            else:
                # It's a normal string
                args.append(f"{key}='{value}'")
        else:
            # Might be int, float, bool, or otherwise
            args.append(f"{key}={value}")

    joined_args = ", ".join(args)
    print("+"*40)
    print(f"{function_name}({joined_args})")
    return f"{function_name}({joined_args})"