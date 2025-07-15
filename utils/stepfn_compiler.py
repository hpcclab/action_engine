import json
import yaml
import os

AWS_ACCOUNT_ID = os.environ.get("AWS_ACCOUNT_ID")

def convert_argo_to_stepfn(argo_yaml):
    entrypoint = argo_yaml["spec"]["entrypoint"]
    templates = {t["name"]: t for t in argo_yaml["spec"]["templates"]}
    dag_tasks = templates[entrypoint]["dag"]["tasks"]

    states = {}
    for i, task in enumerate(dag_tasks):
        name = task["name"]
        template_name = task["template"]
        lambda_arn = f"arn:aws:lambda:us-east-2:{AWS_ACCOUNT_ID}:function:{template_name}"

        state = {
            "Type": "Task",
            "Resource": lambda_arn,
            "ResultPath": "$"  
        }

        if i < len(dag_tasks) - 1:
            next_state = dag_tasks[i + 1]["name"]
            state["Next"] = next_state
        else:
            state["End"] = True

        states[name] = state

    return {
        "StartAt": dag_tasks[0]["name"] if dag_tasks else "",
        "States": states
    }


def write_stepfn_json(argo_yaml, output_path="step_function_workflow.json"):
    stepfn_json = convert_argo_to_stepfn(argo_yaml)
    with open(output_path, "w") as f:
        json.dump(stepfn_json, f, indent=2)
    print(f"[✓] Step Functions workflow JSON written to {output_path}")
