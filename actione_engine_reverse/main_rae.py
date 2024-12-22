from .utils.modules import determine_output, find_apis_by_output_description, select_best_api, can_fulfill_directly, get_param_output_description, create_workflow
from .utils.llms import get_model
"""
Choose from below
"gpt-4o"
"gpt-3.5"
"meta-llama/Meta-Llama-3-8B-Instruct"
"mistralai/Mistral-7B-Instruct-v0.3"
"meta-llama/Llama-3.2-3B-Instruct"
"google/gemma-2b-it"
"""
# model_name = "gpt-4o"
# model = get_model(model_name)

class ReverseActionEngine:
    def __init__(self, model):
        # Initialize any required state, such as references to LLM, API repository, etc.
        self.user_request = None
        self.model = model
        self.final_output_description = None
        self.selected_apis = []
    def reverse_action_engine(self, user_request: str):
        """
        Main flow to generate a workflow by starting from the user's desired output and working backwards.
        """
        self.user_request = user_request
        # Step 1: Determine the final output description from the user's request
        # self.final_output_description = determine_output(self.model, self.user_request)
        # Step 2: Find candidate APIs that produce the desired output
        candidate_apis = find_apis_by_output_description(self.user_request)
        
        if not candidate_apis:
            return "No API found that can produce the requested final output."
        # Select the best matching API
        chosen_api = select_best_api(self.model, candidate_apis, self.user_request)
        # Step 3 & 4: Resolve parameters for the chosen API
        workflow = self.build_workflow_for_api(chosen_api, self.user_request)

        if workflow is None or workflow == "failure":
            return "Unable to build a workflow for the requested output."
        
        return workflow

    def build_workflow_for_api(self, api, user_request):
        """
        Recursively resolve inputs for the given API by checking if the user request 
        provides them directly, or by finding other APIs to produce them.
        """
        param_values = {}
        for param in api.get('input_parameters_with_datatype', []):
            extracted_param = can_fulfill_directly(self.model, user_request, param) or not "None"
            if extracted_param and not extracted_param["value"] == "None":
                print("Extracted from user input")
                param_values[param["name"]] = extracted_param["value"]
            else:
                # Parameter not directly provided, need to find another API
                print("Extracted from API")
                param_output_desc = get_param_output_description(self.model, param)
                sub_candidate_apis = find_apis_by_output_description(param_output_desc["description"])
                if not sub_candidate_apis:
                    return "failure"
                chosen_sub_api = select_best_api(self.model, sub_candidate_apis, param_output_desc)
                print(chosen_sub_api)
                print(param_output_desc)
                print(">"*40)
                # Recursively get the sub-workflow string
                param_api = self.build_workflow_for_api(chosen_sub_api, user_request)
                if param_api is None or param_api == "failure":
                    return "failure"

                # Store the entire sub-workflow call (string) in the param_values
                param_values[param["name"]] = param_api

        # Once all parameters are resolved, create the workflow node (string)
        return create_workflow(api, param_values)
    
