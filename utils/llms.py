import os
import re
from dotenv import load_dotenv
from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline, Pipeline
from langchain.prompts import ChatPromptTemplate
from langchain.utils.openai_functions import convert_pydantic_to_openai_function
from langchain.output_parsers.openai_functions import JsonOutputFunctionsParser
from langchain_community.chat_models import ChatOpenAI
import torch
from huggingface_hub import login
from vllm import LLM, SamplingParams

import json
import yaml
import ruamel.yaml

# Load environment variables
load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")
huggingface_token = os.getenv("HUGGINGFACE_TOKEN")
login(huggingface_token)

# Global variable to store the loaded model
_loaded_model = None
_loaded_pipeline = None

def get_model(model_name):
    print("Model Name: ", model_name)
    global tokenizer, _loaded_pipeline
    
    # Load the model based on the model_name
    if model_name == "gpt-4o":
        _loaded_model = ChatOpenAI(model="gpt-4o", temperature=0, api_key=openai_api_key)
    elif model_name == "gpt-3.5-turbo":
        _loaded_model = ChatOpenAI(model="gpt-3.5-turbo", temperature=0, api_key=openai_api_key)
    elif model_name == "Qwen/Qwen2.5-Coder-32B-Instruct-GPTQ-Int8":
        #   Runnig on Parallel
        print("Runnig on Parallel - Loading tokenizer...")
        tokenizer = AutoTokenizer.from_pretrained(model_name, legacy=False)
        print("Loading model across multiple GPUs...")
        _loaded_pipeline = LLM(model=model_name, tensor_parallel_size=2)
        
        print("------------Qwen model loaded across GPUs.------------")
        return _loaded_pipeline, tokenizer

    else:
        print("------------Geeral model loaded.------------")
        # Load tokenizer and model for HuggingFace models
        tokenizer = AutoTokenizer.from_pretrained(model_name)
        model = AutoModelForCausalLM.from_pretrained(
            model_name, 
            device_map="auto",
            torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
        )
        _loaded_pipeline = pipeline(
            "text-generation",
            model=model,
            tokenizer=tokenizer
        )

    return _loaded_pipeline

def extract_json_answer(text, max_retries=2):
    """
    Extracts the JSON answer from the given text using a regex pattern.
    
    Parameters:
    text (str): The text containing the answer.
    max_retries (int): Maximum number of retries if extraction fails.

    Returns:
    dict or list: Extracted JSON content if found, otherwise an error message.
    """
    # Regex pattern to find content between "```json" and "```"
    match = re.search(r"```json\s*(\{.*?\}|\[.*?\])\s*```", text, re.DOTALL)
    
    for attempt in range(max_retries):
        if match:
            json_content = match.group(1).strip()
            try:
                # Attempt to load and return the JSON as a Python object for better validation
                return json.loads(json_content)
            except json.JSONDecodeError as e:
                # Log the error and retry
                print(f"Attempt {attempt + 1}/{max_retries} - Error parsing JSON: {e}")
                match = re.search(r"```json\s*(\{.*?\}|\[.*?\])\s*```", text, re.DOTALL)
        else:
            # Log that no JSON block was found before retrying
            print(f"Attempt {attempt + 1}/{max_retries} - JSON block not found.")
            match = re.search(r"```json\s*(\{.*?\}|\[.*?\])\s*```", text, re.DOTALL)
    
    # Return an error if all attempts fail
    return {"error": "Failed to extract JSON after multiple attempts", "output": text}

def extract_yaml_answer(text):
    """
    Extracts the raw YAML content from the given text.
    Handles cases where the closing ``` is missing by extracting from the first occurrence.
    
    Parameters:
    text (str): The text containing the answer.

    Returns:
    str: Extracted YAML content as a raw string if found, otherwise an empty string.
    """
    # Regex pattern to find content between "```yaml" and "```" or until the end of the text
    match = re.search(r"```yaml\s*(.*?)\s*(?:```|$)", text, re.DOTALL)
    
    if match:
        return match.group(1).strip()
    
    return ""  # Return empty string if no YAML content is found

def remove_prompt_from_response(prompt: str, response: str) -> str:
    """
    Removes the prompt from the response if the response starts with the prompt.
    
    Parameters:
    - prompt (str): The input prompt given to the model.
    - response (str): The model's response.
    
    Returns:
    - str: The response with the prompt removed.
    """
    if response.startswith(prompt):
        return response[len(prompt):].strip()
    return response.strip()


# llms.py
def call_llm(model, pydantic_schema, schema_name, system_prompt, user_prompt, max_retries=3):
    """
    Invokes the LLM with the given prompt and schema, then extracts the JSON answer.
    If extraction fails, retries calling the LLM up to max_retries times.

    Parameters:
    model (object): Preloaded model instance.
    pydantic_schema (dict): Schema to be used for data extraction.
    schema_name (str): Name of the schema for extraction.
    system_prompt (str): System prompt for the LLM.
    user_prompt (str): User-provided prompt.
    max_retries (int): Maximum number of retries if extraction fails.

    Returns:
    dict or list: Extracted JSON response or error message.
    """
    # Create the prompt template
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("human", user_prompt)
    ])
    print(model)
    # Convert the Pydantic schema to a format that can be used with the model
    extraction_functions = [convert_pydantic_to_openai_function(pydantic_schema)]
    
    for attempt in range(max_retries):
        # print(f"Attempt {attempt + 1}/{max_retries} - Invoking LLM.")
        
        if isinstance(model, ChatOpenAI):
            # Handle OpenAI models using LangChain
            extraction_model = model.bind(functions=extraction_functions, function_call={"name": schema_name})
            extraction_chain = prompt | extraction_model | JsonOutputFunctionsParser()
            response = extraction_chain.invoke({})
        
        else:
            # Handle open-source models with the text-generation pipeline
            combined_prompt = f"{system_prompt}\n{user_prompt}"
            result = model(
                combined_prompt, 
                max_new_tokens=1000,  
                num_return_sequences=1, 
                do_sample=True,  
                temperature=0.7
            )
            raw_output = result[0]['generated_text']
            # Extract JSON answer from the raw output using the dedicated function
            if not schema_name == "ArgoYAML":
                response = extract_json_answer(raw_output)
            else:
                response = extract_yaml_answer(raw_output)

        # Check if the response is a valid extraction (not an error)
        if isinstance(response, (list, dict)) and "error" not in response:
            # print("Extraction successful.")
            return response
        else:
            # Log the retry attempt and reason for failure
            print(f"Attempt {attempt + 1}/{max_retries} failed. Reason: {response.get('error', 'Unknown error')}")

    # If all attempts fail, return the last error response
    return response

def call_local_llm(
    _loaded_pipeline, 
    tokenizer,
    model_name: str,
    pydantic_schema: dict,
    schema_name: str,
    system_prompt: str,
    user_prompt: str,
    max_retries: int = 3
):
    combined_prompt = f"{system_prompt}\n{user_prompt}"
    sampling_params = SamplingParams(temperature=0.7, top_p=0.8, repetition_penalty=1.05, max_tokens=1024)
    for attempt in range(max_retries):
        try:
            # generate outputs
            outputs = _loaded_pipeline.generate([combined_prompt], sampling_params)

            # Print the outputs.
            for output in outputs:
                prompt = output.prompt
                generated_text = output.outputs[0].text
            response = remove_prompt_from_response(combined_prompt, generated_text)
            response = extract_yaml_answer(response)  
            return response
        except Exception as e:
            print(f"Attempt {attempt + 1}/{max_retries} failed. Exception: {str(e)}")
            response = {"error": str(e)}
            continue
    return response  # Return the last error response after retries are exhausted