# Tools


# Prompt
DATA_DEPENDENCY_RITIREVAL_SYSYSTEM_PROMPT = """
You will be given the required parameters for the next API, the next API parameter descriptions, and outputs parameters from the past APIs already invoked only if there is any.
Your Job is to collect the required parameter only if the past API's output parameter can be used.
Only if the past output can be used as the next required parameter, add value "tasks.{past_API_name}.result"
where the past_API_name is the name of the api which include the output parameter used as next API's required parameter followed by number like t1, t2, etc.

If there is no output from APIs can be used as any input parameter of next api, DO NOT ADD THE PARAMETERS.
"""


DATA_DEPENDENCY_RITIREVAL_USER_PROMPT = f"""
Next API parameters: {selected_functions[i]["input_parameters_with_datatype"]},
Next API parameters description: {selected_functions[i]["input_description"]}
Outputs from list of past APIs: {[api["dependency_output"] for api in selected_functions[:i+1]]},
If there is no output from APIs can be used as any input parameter of next api, DO NOT ADD THE PARAMETERS
"""

-----------
DATA_DEPENDENCY_RITIREVAL_SYSYSTEM_PROMPT = """
You will be given the required parameters for the current API, the current API parameter descriptions, and outputs parameters from the past APIs already invoked only if there is any.
Your Job is to collect the current required parameter if the past API's output parameter can be used.
Only if the past output can be used as the current required parameter, add value "tasks.{past_API_name}.result"
where the past_API_name is the name of the api which include the output parameter used as current API's required parameter followed by number like t1, t2, etc.

You are not only allowed to use past parameter and not current ones, so if your at task number t1, you cannot use "task.t1.result"
because those are current parameter and you should only use it from past output parameters.
If there is no output from APIs can be used as any input parameter of next api, DO NOT ADD THE PARAMETERS.
"""


DATA_DEPENDENCY_RITIREVAL_USER_PROMPT = f"""
Current step number: t{i+1}
Current API parameters: {selected_functions[i]["input_parameters_with_datatype"]},
Current API parameters description: {selected_functions[i]["input_description"]}
Outputs from list of past APIs: {[api["dependency_output"] for api in selected_functions[:i+1]]},
"""