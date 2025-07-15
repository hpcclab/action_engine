from openai import OpenAI
import os
from dotenv import load_dotenv
from langchain.utils.openai_functions import convert_pydantic_to_openai_function
from langchain.prompts import ChatPromptTemplate
from langchain.chat_models import ChatOpenAI
from langchain.output_parsers.openai_functions import JsonOutputFunctionsParser
from langchain.output_parsers.openai_functions import JsonKeyOutputFunctionsParser
load_dotenv()
model = ChatOpenAI(
      model='gpt-3.5-turbo',
    #   model="gpt-4o",
      temperature=0,
      api_key=os.getenv("OPENAI_API_KEY"),
    )

# invoke gpt Function
def call_llm(pydantic_schema, schema_name: str, system_prompt: str, user_prompt: str):
    

    prompt = ChatPromptTemplate.from_messages([
    ("system", system_prompt),
    ("human", user_prompt)
    ])
    extraction_functions = [convert_pydantic_to_openai_function(pydantic_schema)]
    extraction_model = model.bind(functions=extraction_functions, function_call={"name": schema_name})
    extraction_chain = prompt | extraction_model | JsonOutputFunctionsParser()
    response = extraction_chain.invoke({})

    return response

"""
return value example
[{'task_number': 1, 'task_description': 'Generate animated image of a dog.'}, {'task_number': 2, 'task_description': 'Generate animated image of a cat.'}, {'task_number': 3, 'task_description': 'Create a video using the animated images of dog and cat.'}, {'task_number': 4, 'task_description': 'Send the created video via email.'}]
"""

def call_openai(system_prompt: str, user_prompt: str):
    """
    Generates a YAML file using OpenAI's API based on the provided system and user prompts.

    """
    client = OpenAI(
        # defaults to os.environ.get("OPENAI_API_KEY")
        api_key=os.getenv("OPENAI_API_KEY"),
    )
    response = client.chat.completions.create(
      # model='gpt-3.5-turbo',
        model="gpt-4o",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        max_tokens=1000,  
    )

    # Extract the generated text from the response
    yaml_content = response.choices[0].message.content.strip()
    return yaml_content
