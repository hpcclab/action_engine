"""
Generate DAG part of workflow
"""
import yaml
import ruamel.yaml
import re

filepath = "./output_file/"

def sp_ch_change(name):
    return re.sub(r'[^a-zA-Z0-9]+', '-', name).lower()

# Function to generate Argo Workflow DAG YAML
def generate_argo_dag(selected_api_info, user_inputs):
    dag_tasks = []
    for api in selected_api_info:
        task = {
            "name": "t"+str(api["task_num"]),
            "template": sp_ch_change(api["name"]),
            "arguments": {
                "parameters": [ {"name": param["name"], "value": f"{{{{ inputs.parameters.{param['name']} }}}}"}
                            for param in api["input_parameters_with_datatype"] if any(p["name"] == param["name"] for p in user_inputs) # add user input params
                                ] + [ {"name": key, "value": f"{{{{ tasks.{value}.result }}}}"} for param in api["depended_params"] for key, value in param.items()] # add depended params (from selected_functions["dependent_params")
            },
            "dependencies": [dep for dep in api["dependencies"] if dep]
        }


        dag_tasks.append(task)

    dag_yaml = [{"name": "main",
        "inputs": {"parameters": [{"name": param["name"]} for param in user_inputs]},
        "dag": {
            "tasks": dag_tasks
        }}]

    return dag_yaml

def generate_argo_templates(selected_api_info):
    templates = []
    for api in selected_api_info:
      """
      # TODO
        gether proper URL and store it to the API database
      """
      template = {
          "name": sp_ch_change(api["name"]),
          "inputs": {
              "parameters": [{"name": param["name"]}
                                for param in api["input_parameters_with_datatype"]]
          },
          "http": {
              "method": api["method"],
              "url": api["url"],
              "successCondition": "response.statusCode == 200"
          }}
      if template not in templates:
        templates.append(template)
    return templates

def generate_argo_header(argo_dag_yaml, user_inputs):
    workflow = {
        "apiVersion": "argoproj.io/v1alpha1",
        "kind": "Workflow",
        "metadata": {
            "generateName": "http-wf-"
        },
        "spec": {
            "arguments": {
                "parameters": [{"name": param["name"]} for param in user_inputs]
            },
            "entrypoint": "main",
            "templates": argo_dag_yaml
        }
    }
    return workflow

def yaml_compiler(selected_api_info, user_inputs):
    argo_dag_yaml = generate_argo_dag(selected_api_info, user_inputs)
    argo_template_yaml = generate_argo_templates(selected_api_info)
    argo_dag_yaml.extend(argo_template_yaml)
    argo_header_yaml = generate_argo_header(argo_dag_yaml, user_inputs)

    return argo_header_yaml