from .llms import call_llm
from .utilities import escape_json
from .schemas.workflow import Tasks

def subtask_diviser(model_name, user_query):
    SYSTEM_PROMPT = f'''
    Instruction: 
    User Request: {user_query}

    Given a user request. Your goal is to divide the user request into subtasks if the user request is a compound workload and extract information.
    Let's think step by step.
    Each subtask will be converted to an API in the next step. Please divide the given user request into the smallest executable subtasks.
    Each subtask needs to be precise and well descriptive.
    
    Below are examples of user requests and the divided subtasks:

    Example 1:
    User Request: "Can you add the song 'Imagine' by John Lennon to Jenny's 'Chill Vibes' playlist?" 
    {{'Tasks': [
            {{
                "subtask_number": 1, 
                "subtask_description": "Convert the username 'Jenny' to a user ID using the UserName2ID API."
            }}, 
            {{
                "subtask_number": 2, 
                "subtask_description": "Convert the playlist name 'Chill Vibes' to a playlist ID using the PlaylistName2ID API."
            }}, 
            {{
                "subtask_number": 3, 
                "subtask_description": "Add the song 'Imagine' by John Lennon to the playlist using the AddSongToPlaylist API, providing the user ID and playlist ID."
            }}
        ]
    }}
    Example 2:
    User Request: "Can you help me make a reservation in a 3-star hotel in Chicago from July 20 to July 25?"
    {{'Tasks': [
            {{
                "subtask_number": 1, 
                "subtask_description": "Find a 3-star hotel in Chicago using the FindHotel API."
            }}, 
            {{
                "subtask_number": 2, 
                "subtask_description": "Make a reservation in the hotel found using the BookRoom API with the check-in date 'July 20' and check-out date 'July 25'."
            }}
        ]
    }}
    Example 3:
    User Request:  "Can you help Jane Smith buy 5 units of 'Product Y'?"
    {{
        'Tasks': [
            {{
                "subtask_number": 1, 
                "subtask_description": "Convert the customer name 'Jane Smith' to a customer ID using the CustomerNameToID API."
            }}, 
            {{
                "subtask_number": 2, 
                "subtask_description": "Convert the product name 'Product Y' to a product ID using the ProductNameToID API."
            }}, 
            {{
                "subtask_number": 3, 
                "subtask_description": "Purchase 5 units of the product using the PurchaseProduct API with the customer ID and product ID."
            }}
        ]
    }}
    You must only generate the Answer. Your answer must be in JSON format. 
    Your Answer format must start with "```json" and end with "```".
    '''

    USER_PROMPT = f"""
    Answer: 
    """
    response = call_llm(model_name, Tasks, "Tasks" ,escape_json(SYSTEM_PROMPT), escape_json(USER_PROMPT))

    # return response["Tasks"]
    return response

"""
return value example
[{'subtask_number': 1, 'subtask_description': 'Generate animated image of a dog.'}, {'subtask_number': 2, 'subtask_description': 'Generate animated image of a cat.'}, {'subtask_number': 3, 'subtask_description': 'Create a video using the animated images of dog and cat.'}, {'subtask_number': 4, 'subtask_description': 'Send the created video via email.'}]
"""