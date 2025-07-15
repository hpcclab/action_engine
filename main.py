from utils.subtask_div import subtask_diviser
from pydantic import BaseModel
from utils.func_identifier import func_identifier
from utils.wf_optimizer import wf_optimizer
from utils.data_dependency import confirm_dependency
from utils.argo_compiler import yaml_compiler
from utils.missing_func import missing_func
from utils.llms import get_model
from utils.s3_handler import S3FileHandler
import boto3
import re
import sys 
import json
import asyncio
from ruamel.yaml import YAML
from fastapi import FastAPI, Body, UploadFile, File, Form
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi import Request
from utils.stepfn_compiler import write_stepfn_json  
from utils.workflow_registry import save_workflow_arn
from fastapi import HTTPException
import os
import time
from utils.validate_dependencies import can_reorder_workflow
from typing import List, Optional
from dotenv import load_dotenv
load_dotenv()

""""
test

"""
#local
# filepath = "/home/UNT/ae0589/Desktop/HPCC/AutomaticWorkflowGeneration/ActionEngine/"
app = FastAPI()
yaml = YAML()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001", "*"],  # Allow all origins for development
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["*"],
    max_age=3600,
)

#cloud
filepath = "./"

# Initialize S3 handler
s3_handler = S3FileHandler()

# Initialize AWS Step Functions client
sf_client = boto3.client("stepfunctions", region_name="us-east-2")

"""
Choose from below
"gpt-4o"
"gpt-3.5"
"meta-llama/Meta-Llama-3-8B-Instruct"
"mistralai/Mistral-7B-Instruct-v0.3"
"meta-llama/Llama-3.2-3B-Instruct"
"google/gemma-2b-it"
"""

model_name = "gpt-4o"

AWS_ACCOUNT_ID = os.environ.get("AWS_ACCOUNT_ID")
AWS_ROLE_ARN = os.environ.get("AWS_ROLE_ARN", f"arn:aws:iam::{AWS_ACCOUNT_ID}:role/StepFunctionExecutionRole")

class QueryRequest(BaseModel):
    user_query: str

class QueryWithFilesRequest(BaseModel):
    user_query: str
    file_urls: Optional[List[str]] = []

class WorkflowUpdateRequest(BaseModel):
    definition: dict

class APIEndpointRequest(BaseModel):
    user_query: str
    description: Optional[str] = None

# user_query = "Create a graffiti-style image from a text prompt, enhance its quality, resize it to 800x600, convert it to a PDF, and send it via email."
# user_query ="It will be perfect if you play music that matches my mood. This is Anna."

@app.post("/upload-files")
async def upload_files(files: List[UploadFile] = File(...)):
    """Upload multiple files to S3 and return their URLs"""
    uploaded_files = []
    
    for file in files:
        try:
            # Read file content
            content = await file.read()
            
            # Upload to S3
            result = s3_handler.upload_file(
                file_content=content,
                filename=file.filename,
                content_type=file.content_type
            )
            
            if result["success"]:
                uploaded_files.append({
                    "original_filename": result["original_filename"],
                    "s3_key": result["s3_key"],
                    "s3_url": result["s3_url"],
                    "public_url": result["public_url"],
                    "content_type": result["content_type"],
                    "file_size": result["file_size"],
                    "presigned_url": s3_handler.get_presigned_url(result["s3_key"])
                })
            else:
                uploaded_files.append({
                    "original_filename": file.filename,
                    "error": result["error"],
                    "success": False
                })
                
        except Exception as e:
            uploaded_files.append({
                "original_filename": file.filename,
                "error": str(e),
                "success": False
            })
    
    return {"uploaded_files": uploaded_files}

@app.post("/generate-and-run-workflow-with-files")
async def generate_and_run_workflow_with_files(
    request_data: QueryWithFilesRequest, 
    request: Request
):
    """Generate and run workflow with file inputs from S3"""
    user_query = request_data.user_query
    file_urls = request_data.file_urls or []
    
    model = get_model(model_name)
    
    # Enhance query with file information
    if file_urls:
        file_info = []
        for url in file_urls:
            if url.startswith("s3://"):
                s3_key = url.replace("s3://automatic-workflow-files/", "")
                info = s3_handler.get_file_info(s3_key)
                if info:
                    file_info.append({
                        "url": url,
                        "content_type": info["content_type"],
                        "presigned_url": s3_handler.get_presigned_url(s3_key)
                    })
        
        enhanced_query = f"{user_query}\n\nInput files: {json.dumps(file_info, indent=2)}"
    else:
        enhanced_query = user_query
    
    # Generate workflow with file-aware context
    task_list = subtask_diviser(model, enhanced_query)
    selected_functions, NO_FUNC, non_func_list = func_identifier(model, task_list["Tasks"], enhanced_query)
    semantic_wf = wf_optimizer(model, enhanced_query, task_list)
    selected_functions, user_inputs, dependent_params = confirm_dependency(model, semantic_wf, selected_functions)
    
    # Add file URLs to user inputs
    if file_urls:
        user_inputs.append({"name": "input_files", "datatype": "file_list", "value": file_urls})
    
    argo_wf = yaml_compiler(selected_functions, user_inputs)

    try:
        output_dir = os.path.join(filepath, "output_file")
        os.makedirs(output_dir, exist_ok=True)
        yaml_path = os.path.join(output_dir, "argo_workflow.yaml")
        with open(yaml_path, "w") as f:
            yaml.dump(argo_wf, f)

        json_path = os.path.join(output_dir, "step_function_workflow.json")
        write_stepfn_json(argo_wf, json_path)

        state_machine_name = "workflow_" + re.sub(r'[^a-zA-Z0-9]+', '_', user_query)[:40]
        role_arn = AWS_ROLE_ARN

        with open(json_path, "r") as f:
            definition = f.read()

        response = sf_client.create_state_machine(
            name=state_machine_name,
            definition=definition,
            roleArn=role_arn,
            type="STANDARD"
        )

        state_machine_arn = response["stateMachineArn"]

        # Include file URLs in execution input
        execution_input = {"input_files": file_urls} if file_urls else {}
        
        execution_response = sf_client.start_execution(
            stateMachineArn=state_machine_arn,
            input=json.dumps(execution_input)
        )

        execution_arn = execution_response["executionArn"]

        invoke_url = str(request.base_url).rstrip("/") + f"/invoke-workflow/{state_machine_name}"
        save_workflow_arn(state_machine_name, state_machine_arn, user_query, invoke_url)

        return {
            "message": "Workflow generated and executed successfully with file inputs.",
            "execution_arn": execution_arn,
            "invoke_api_endpoint": invoke_url,
            "input_files": file_urls
        }

    except Exception as e:
        return {"status": "FAILED", "error": str(e)}

@app.get("/file-info/{s3_key}")
def get_file_info(s3_key: str):
    """Get information about a file stored in S3"""
    try:
        info = s3_handler.get_file_info(s3_key)
        if info:
            info["presigned_url"] = s3_handler.get_presigned_url(s3_key)
            return info
        else:
            raise HTTPException(status_code=404, detail="File not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/files/{s3_key}")
def delete_file(s3_key: str):
    """Delete a file from S3"""
    try:
        success = s3_handler.delete_file(s3_key)
        if success:
            return {"message": "File deleted successfully"}
        else:
            raise HTTPException(status_code=404, detail="File not found or deletion failed")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/workflows")
def list_workflows():
    with open("./output_file/workflow_registry.json", "r") as f:
        data = json.load(f)

    return [
        {
            "workflow_name": name,
            "invoke_api_endpoint": record.get("invoke_url"),
            "user_query": record.get("user_query"),
            "timestamp": record.get("timestamp"),
            "arn": record.get("arn") 
        }
        for name, record in data.items()
    ]

@app.post("/generate-and-run-workflow")
async def generate_and_run_workflow(request_data: QueryRequest, request: Request):
    user_query = request_data.user_query
    model = get_model(model_name)
    task_list = subtask_diviser(model, user_query)
    selected_functions, NO_FUNC, non_func_list = func_identifier(model, task_list["Tasks"], user_query)
    semantic_wf = wf_optimizer(model, user_query, task_list)
    selected_functions, user_inputs, dependent_params = confirm_dependency(model, semantic_wf, selected_functions)
    argo_wf = yaml_compiler(selected_functions, user_inputs)

    try:
        output_dir = os.path.join(filepath, "output_file")
        os.makedirs(output_dir, exist_ok=True)
        yaml_path = os.path.join(output_dir, "argo_workflow.yaml")
        with open(yaml_path, "w") as f:
            yaml.dump(argo_wf, f)

        json_path = os.path.join(output_dir, "step_function_workflow.json")
        write_stepfn_json(argo_wf, json_path)

        state_machine_name = "workflow_" + re.sub(r'[^a-zA-Z0-9]+', '_', user_query)[:40]
        role_arn = AWS_ROLE_ARN

        with open(json_path, "r") as f:
            definition = f.read()

        response = sf_client.create_state_machine(
            name=state_machine_name,
            definition=definition,
            roleArn=role_arn,
            type="STANDARD"
        )

        state_machine_arn = response["stateMachineArn"]

        execution_response = sf_client.start_execution(
            stateMachineArn=state_machine_arn,
            input=json.dumps({})
        )

        execution_arn = execution_response["executionArn"]

        invoke_url = str(request.base_url).rstrip("/") + f"/invoke-workflow/{state_machine_name}"
        save_workflow_arn(state_machine_name, state_machine_arn, user_query, invoke_url)

        return {
            "message": "Workflow generated and executed successfully.",
            "execution_arn": execution_arn,
            "invoke_api_endpoint": invoke_url
        }

    except Exception as e:
        return {"status": "FAILED", "error": str(e)}
    


def load_workflow_arn(name):
    with open("./output_file/workflow_registry.json", "r") as f:
        data = json.load(f)
    return data.get(name)

@app.post("/invoke-workflow/{workflow_name}")
async def invoke_workflow(workflow_name: str, request: Request):
    try:
        # Try to parse the request body as JSON
        body = await request.json()
    except Exception:
        # If parsing fails, fall back to empty dictionary
        body = {}

    # Load the stored ARN for the given workflow name
    workflow_arn = load_workflow_arn(workflow_name)
    if not workflow_arn:
        # Return a 404 status code with an error message
        return JSONResponse(
            status_code=404,
            content={"status": "FAILED", "output": {"error": f"Workflow '{workflow_name}' not found."}}
        )

    try:
        # Start execution of the Step Function
        response = sf_client.start_execution(
            stateMachineArn=workflow_arn["arn"],
            input=json.dumps(body)
        )

        execution_arn = response["executionArn"]

        # Poll the execution status for up to 10 seconds (1 second interval)
        for _ in range(10):
            result = sf_client.describe_execution(executionArn=execution_arn)
            if result["status"] != "RUNNING":
                # If execution is finished, parse output and return full result
                result["output"] = json.loads(result.get("output", "{}"))
                result["executionArn"] = execution_arn
                return result
            time.sleep(1)

        # If still running after 10 seconds, return a partial result
        return {
            "status": "RUNNING",
            "executionArn": execution_arn,
            "message": "Execution still running after timeout."
        }

    except Exception as e:
        # Catch and return any error with failed status
        return {"status": "FAILED", "error": str(e)}
    


@app.get("/execution-status")
def execution_status(executionArn: str):
    try:
        response = sf_client.describe_execution(executionArn=executionArn)
        return {
            "status": response["status"],
            "startDate": str(response["startDate"]),
            "stopDate": str(response.get("stopDate", "N/A")),
            "output": json.loads(response.get("output", "{}"))
        }
    except Exception as e:
        return {"error": str(e)}



@app.delete("/workflows/{workflow_name}")
def delete_workflow(workflow_name: str):
    try:
        with open("./output_file/workflow_registry.json", "r") as f:
            data = json.load(f)

        if workflow_name not in data:
            raise HTTPException(status_code=404, detail="Workflow not found.")

        del data[workflow_name]

        with open("./output_file/workflow_registry.json", "w") as f:
            json.dump(data, f, indent=2)

        return {"message": f"Workflow '{workflow_name}' deleted."}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/restructure-workflow")
def restructure_workflow(data: dict):
    """
    Expects:
    {
        "workflow_name": "workflow_xyz",
        "new_order": ["t2", "t1", "t3"],
        "create_new": false  # Optional: if false, update existing restructured version
    }
    """
    try:
        name = data["workflow_name"]
        order = data["new_order"]
        create_new = data.get("create_new", True)  # Default to creating new
        
        print(f"Restructuring workflow: {name}")
        print(f"New order: {order}")
        print(f"Create new: {create_new}")

        # Find the workflow in the registry
        with open("./output_file/workflow_registry.json", "r") as f:
            registry = json.load(f)
            
        workflow_entry = None
        for reg_name, entry in registry.items():
            if reg_name == name or name in entry["arn"]:
                workflow_entry = entry
                name = reg_name  # Use the full name from registry
                break
                
        if not workflow_entry:
            print(f"Workflow not found: {name}")
            raise HTTPException(status_code=404, detail="Workflow not found")

        # Load the original Step Functions JSON
        with open("./output_file/step_function_workflow.json") as f:
            stepfn_json = json.load(f)
            
        print(f"Current states: {list(stepfn_json['States'].keys())}")
        
        # Validate dependencies before reordering
        can_reorder, validation_errors = can_reorder_workflow(stepfn_json, order)
        if not can_reorder:
            print(f"Dependency validation failed: {validation_errors}")
            raise HTTPException(
                status_code=400, 
                detail=f"Cannot reorder workflow due to dependencies: {'; '.join(validation_errors)}"
            )

        # Extract and reorder states
        old_states = stepfn_json["States"]
        reordered_states = {k: old_states[k] for k in order if k in old_states}
        
        print(f"Reordered states: {list(reordered_states.keys())}")
        
        if len(reordered_states) != len(order):
            missing_states = [k for k in order if k not in old_states]
            print(f"Missing states: {missing_states}")
            raise HTTPException(status_code=400, detail=f"Invalid state IDs: {missing_states}")

        # Adjust Next/End fields
        for i, key in enumerate(order):
            if i + 1 < len(order):
                reordered_states[key]["Next"] = order[i + 1]
                reordered_states[key].pop("End", None)
            else:
                reordered_states[key].pop("Next", None)
                reordered_states[key]["End"] = True

        # Reconstruct Step Function JSON
        stepfn_json["States"] = reordered_states
        stepfn_json["StartAt"] = order[0]

        # Save new JSON
        restructured_path = "./output_file/restructured_stepfn.json"
        with open(restructured_path, "w") as f:
            json.dump(stepfn_json, f, indent=2)

        # Re-register Step Function
        role_arn = AWS_ROLE_ARN
        with open(restructured_path) as f:
            definition = f.read()

        # Check if we should reuse existing restructured workflow
        if not create_new:
            # Look for existing restructured version
            existing_name = f"{name}_restructured"
            try:
                # List all state machines to find existing restructured versions
                paginator = sf_client.get_paginator('list_state_machines')
                for page in paginator.paginate():
                    for sm in page['stateMachines']:
                        if sm['name'].startswith(f"{name}_restructured"):
                            existing_name = sm['name']
                            print(f"Found existing restructured workflow: {existing_name}")
                            
                            # Update the existing state machine
                            try:
                                sf_client.update_state_machine(
                                    stateMachineArn=sm['stateMachineArn'],
                                    definition=definition,
                                    roleArn=role_arn
                                )
                                
                                # Start execution
                                execution_response = sf_client.start_execution(
                                    stateMachineArn=sm['stateMachineArn'],
                                    input=json.dumps({})
                                )
                                
                                return {
                                    "message": "Workflow restructured and updated successfully",
                                    "invoke_api_endpoint": f"http://localhost:8000/invoke-workflow/{existing_name}",
                                    "step_function_arn": sm['stateMachineArn'],
                                    "execution_arn": execution_response["executionArn"],
                                    "new_order": order,
                                    "updated_existing": True
                                }
                            except Exception as e:
                                print(f"Failed to update existing workflow: {e}")
                                # Fall through to create new if update fails
                            break
            except Exception as e:
                print(f"Error checking for existing workflows: {e}")
        
        # Add timestamp to make the name unique (only if creating new)
        import time
        timestamp = int(time.time())
        new_name = f"{name}_restructured_{timestamp}" if create_new else f"{name}_restructured"
        
        try:
            # Try to create the state machine
            response = sf_client.create_state_machine(
                name=new_name,
                definition=definition,
                roleArn=role_arn,
                type="STANDARD"
            )
            arn = response["stateMachineArn"]
            
            # Start execution immediately
            execution_response = sf_client.start_execution(
                stateMachineArn=arn,
                input=json.dumps({})
            )
            
            execution_arn = execution_response["executionArn"]
            invoke_url = f"http://localhost:8000/invoke-workflow/{new_name}"
            
            # Save the workflow information
            save_workflow_arn(new_name, arn, "Restructured workflow", invoke_url)
            
            return {
                "message": "Workflow restructured and executed successfully",
                "invoke_api_endpoint": invoke_url,
                "step_function_arn": arn,
                "execution_arn": execution_arn,
                "new_order": order
            }
            
        except sf_client.exceptions.StateMachineAlreadyExists:
            # This should not happen anymore with unique timestamps
            print(f"State machine {new_name} already exists, which shouldn't happen with timestamps")
            raise
            
    except HTTPException:
        raise
    except Exception as e:
        print(f"Unexpected error in restructure_workflow: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/workflows/{workflow_name}")
def get_workflow_definition(workflow_name: str):
    try:
        # If this is an execution ID, extract the workflow name from it
        if "-" in workflow_name:  # This is likely an execution ID
            # Load all workflows to find the matching execution
            with open("./output_file/workflow_registry.json", "r") as f:
                registry = json.load(f)
            
            # Try to find the workflow by matching the execution ID pattern
            workflow_entry = None
            for name, entry in registry.items():
                if name in workflow_name or (entry.get("arn", "") and entry["arn"] in workflow_name):
                    workflow_entry = entry
                    workflow_name = name
                    break
        else:
            # Load the workflow registry
            with open("./output_file/workflow_registry.json", "r") as f:
                registry = json.load(f)
            workflow_entry = registry.get(workflow_name)
                
        if not workflow_entry:
            raise HTTPException(status_code=404, detail="Workflow not found")
            
        # Load the step function definition
        with open("./output_file/step_function_workflow.json", "r") as f:
            workflow_def = json.load(f)
            
        # Extract steps from the workflow definition
        steps = []
        states = workflow_def.get("States", {})
        for state_id, state in states.items():
            steps.append({
                "id": state_id,
                "name": state.get("name", state_id),
                "Resource": state.get("Resource", "")
            })
            
        return {
            "workflow_name": workflow_name,
            "definition": workflow_def,
            "steps": steps
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/workflows/{workflow_name}/update")
async def update_workflow_definition(workflow_name: str, request_data: WorkflowUpdateRequest, request: Request):
    """Update a workflow's JSON definition and regenerate it"""
    try:
        # Validate the definition structure
        definition = request_data.definition
        
        if "StartAt" not in definition:
            raise HTTPException(status_code=400, detail="Missing required field: StartAt")
        
        if "States" not in definition or not isinstance(definition["States"], dict):
            raise HTTPException(status_code=400, detail="Missing or invalid States object")
        
        if definition["StartAt"] not in definition["States"]:
            raise HTTPException(status_code=400, detail=f"StartAt references non-existent state: {definition['StartAt']}")
        
        # Validate state references
        for state_name, state in definition["States"].items():
            if "Next" in state and state["Next"] not in definition["States"]:
                raise HTTPException(status_code=400, detail=f"State '{state_name}' references non-existent Next state: {state['Next']}")
        
        # Save the updated definition
        output_dir = os.path.join(filepath, "output_file")
        os.makedirs(output_dir, exist_ok=True)
        
        # Update the step function JSON file
        json_path = os.path.join(output_dir, "step_function_workflow.json")
        with open(json_path, "w") as f:
            json.dump(definition, f, indent=2)
        
        # Create/update the state machine
        role_arn = AWS_ROLE_ARN
        definition_str = json.dumps(definition)
        
        # Check if workflow exists and update it, or create new one
        try:
            # Try to find existing state machine
            with open("./output_file/workflow_registry.json", "r") as f:
                registry = json.load(f)
            
            workflow_entry = registry.get(workflow_name)
            if workflow_entry and "arn" in workflow_entry:
                # Update existing state machine
                try:
                    sf_client.update_state_machine(
                        stateMachineArn=workflow_entry["arn"],
                        definition=definition_str,
                        roleArn=role_arn
                    )
                    
                    # Start new execution
                    execution_response = sf_client.start_execution(
                        stateMachineArn=workflow_entry["arn"],
                        input=json.dumps({})
                    )
                    
                    execution_arn = execution_response["executionArn"]
                    
                    return {
                        "message": "Workflow updated and executed successfully",
                        "execution_arn": execution_arn,
                        "state_machine_arn": workflow_entry["arn"],
                        "updated_existing": True
                    }
                    
                except Exception as update_error:
                    print(f"Failed to update existing workflow: {update_error}")
                    # Fall through to create new one
            
            # Create new state machine if update failed or doesn't exist
            import time
            timestamp = int(time.time())
            new_name = f"{workflow_name}_updated_{timestamp}"
            
            response = sf_client.create_state_machine(
                name=new_name,
                definition=definition_str,
                roleArn=role_arn,
                type="STANDARD"
            )
            
            state_machine_arn = response["stateMachineArn"]
            
            # Start execution
            execution_response = sf_client.start_execution(
                stateMachineArn=state_machine_arn,
                input=json.dumps({})
            )
            
            execution_arn = execution_response["executionArn"]
            
            # Save to registry
            invoke_url = str(request.base_url).rstrip("/") + f"/invoke-workflow/{new_name}"
            save_workflow_arn(new_name, state_machine_arn, f"Updated workflow: {workflow_name}", invoke_url)
            
            return {
                "message": "Workflow updated and executed successfully",
                "execution_arn": execution_arn,
                "state_machine_arn": state_machine_arn,
                "new_workflow_name": new_name,
                "invoke_api_endpoint": invoke_url,
                "updated_existing": False
            }
            
        except Exception as sf_error:
            raise HTTPException(status_code=500, detail=f"Failed to update AWS Step Function: {str(sf_error)}")
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/workflows/{workflow_name}/export")
def export_workflow(workflow_name: str):
    """Export a workflow configuration including its structure and metadata."""
    try:
        # Load workflow from registry
        with open("./output_file/workflow_registry.json", "r") as f:
            registry = json.load(f)
        
        if workflow_name not in registry:
            raise HTTPException(status_code=404, detail="Workflow not found")
        
        # Load the step function definition
        with open("./output_file/step_function_workflow.json", "r") as f:
            workflow_def = json.load(f)
        
        # Create export package
        export_data = {
            "workflow_name": workflow_name,
            "metadata": registry[workflow_name],
            "definition": workflow_def,
            "export_timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "version": "1.0"
        }
        
        return export_data
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/cleanup-restructured-workflows")
def cleanup_restructured_workflows(data: dict):
    """
    Clean up old restructured workflows, keeping only the most recent ones.
    Expects:
    {
        "workflow_name": "workflow_xyz",  # Base workflow name
        "keep_count": 2  # Number of recent versions to keep (default: 2)
    }
    """
    try:
        base_name = data["workflow_name"]
        keep_count = data.get("keep_count", 2)
        
        # Find all restructured versions
        restructured_workflows = []
        paginator = sf_client.get_paginator('list_state_machines')
        
        for page in paginator.paginate():
            for sm in page['stateMachines']:
                if sm['name'].startswith(f"{base_name}_restructured"):
                    restructured_workflows.append({
                        'name': sm['name'],
                        'arn': sm['stateMachineArn'],
                        'creationDate': sm['creationDate']
                    })
        
        # Sort by creation date (newest first)
        restructured_workflows.sort(key=lambda x: x['creationDate'], reverse=True)
        
        # Delete old versions
        deleted_count = 0
        kept_workflows = []
        
        for i, workflow in enumerate(restructured_workflows):
            if i < keep_count:
                kept_workflows.append(workflow['name'])
            else:
                try:
                    sf_client.delete_state_machine(stateMachineArn=workflow['arn'])
                    
                    # Also remove from registry
                    with open("./output_file/workflow_registry.json", "r") as f:
                        registry = json.load(f)
                    
                    if workflow['name'] in registry:
                        del registry[workflow['name']]
                        
                    with open("./output_file/workflow_registry.json", "w") as f:
                        json.dump(registry, f, indent=2)
                    
                    deleted_count += 1
                except Exception as e:
                    print(f"Failed to delete {workflow['name']}: {e}")
        
        return {
            "message": f"Cleanup completed. Deleted {deleted_count} old workflows.",
            "kept_workflows": kept_workflows,
            "deleted_count": deleted_count
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/generate-api-endpoint")
async def generate_api_endpoint(request_data: APIEndpointRequest, request: Request):
    """
    Main feature: Generate a custom API endpoint for any user query.
    This creates a workflow and returns a ready-to-use API endpoint.
    """
    user_query = request_data.user_query
    description = request_data.description
    
    try:
        model = get_model(model_name)
        
        # Generate workflow from user query
        print(f"Processing user query: {user_query}")
        task_list = subtask_diviser(model, user_query)
        selected_functions, NO_FUNC, non_func_list = func_identifier(model, task_list["Tasks"], user_query)
        semantic_wf = wf_optimizer(model, user_query, task_list)
        selected_functions, user_inputs, dependent_params = confirm_dependency(model, semantic_wf, selected_functions)
        argo_wf = yaml_compiler(selected_functions, user_inputs)

        # Create unique workflow name based on query
        import hashlib
        query_hash = hashlib.md5(user_query.encode()).hexdigest()[:8]
        safe_query = re.sub(r'[^a-zA-Z0-9]+', '_', user_query)[:30]
        workflow_name = f"api_{safe_query}_{query_hash}"
        
        # Save workflow files
        output_dir = os.path.join(filepath, "output_file")
        os.makedirs(output_dir, exist_ok=True)
        
        yaml_path = os.path.join(output_dir, f"{workflow_name}_workflow.yaml")
        with open(yaml_path, "w") as f:
            yaml.dump(argo_wf, f)

        json_path = os.path.join(output_dir, f"{workflow_name}_workflow.json")
        write_stepfn_json(argo_wf, json_path)

        # Create AWS Step Function
        role_arn = AWS_ROLE_ARN
        with open(json_path, "r") as f:
            definition = f.read()

        try:
            response = sf_client.create_state_machine(
                name=workflow_name,
                definition=definition,
                roleArn=role_arn,
                type="STANDARD"
            )
            state_machine_arn = response["stateMachineArn"]
        except sf_client.exceptions.StateMachineAlreadyExists:
            # If exists, get the existing one
            paginator = sf_client.get_paginator('list_state_machines')
            for page in paginator.paginate():
                for sm in page['stateMachines']:
                    if sm['name'] == workflow_name:
                        state_machine_arn = sm['stateMachineArn']
                        # Update the existing state machine
                        sf_client.update_state_machine(
                            stateMachineArn=state_machine_arn,
                            definition=definition,
                            roleArn=role_arn
                        )
                        break

        # Generate the API endpoint URL
        base_url = str(request.base_url).rstrip("/")
        api_endpoint = f"{base_url}/api/{workflow_name}"
        
        # Save workflow metadata
        save_workflow_arn(workflow_name, state_machine_arn, user_query, api_endpoint)
        
        # Create a test execution to verify it works
        test_execution = sf_client.start_execution(
            stateMachineArn=state_machine_arn,
            input=json.dumps({})
        )
        
        return {
            "success": True,
            "message": "Custom API endpoint generated successfully!",
            "api_endpoint": api_endpoint,
            "workflow_name": workflow_name,
            "user_query": user_query,
            "description": description or f"API endpoint for: {user_query}",
            "test_execution_arn": test_execution["executionArn"],
            "usage": {
                "method": "POST",
                "url": api_endpoint,
                "body": {
                    "input_data": "Optional: any input data for the workflow"
                },
                "example_curl": f"""curl -X POST "{api_endpoint}" \\
  -H "Content-Type: application/json" \\
  -d '{{"input_data": "your data here"}}'"""
            },
            "capabilities": task_list.get("Tasks", []),
            "required_functions": [func["function_name"] for func in selected_functions] if selected_functions else [],
            "estimated_execution_time": "1-10 seconds"
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": "Failed to generate API endpoint",
            "user_query": user_query
        }

@app.post("/api/{workflow_name}")
async def execute_custom_workflow(workflow_name: str, request: Request):
    """
    Execute a custom workflow via its generated API endpoint
    """
    try:
        # Parse request body (optional)
        try:
            body = await request.json()
        except:
            body = {}
        
        # Load workflow info
        try:
            with open("./output_file/workflow_registry.json", "r") as f:
                registry = json.load(f)
        except:
            registry = {}
            
        if workflow_name not in registry:
            return {
                "success": False,
                "error": f"Workflow '{workflow_name}' not found. Generate it first using /generate-api-endpoint"
            }
        
        workflow_info = registry[workflow_name]
        state_machine_arn = workflow_info["arn"]
        
        # Execute the workflow
        execution_response = sf_client.start_execution(
            stateMachineArn=state_machine_arn,
            input=json.dumps(body)
        )
        
        execution_arn = execution_response["executionArn"]
        
        # Wait for execution to complete (up to 30 seconds)
        for i in range(30):
            result = sf_client.describe_execution(executionArn=execution_arn)
            if result["status"] != "RUNNING":
                break
            time.sleep(1)
        
        # Parse output
        output = {}
        if "output" in result:
            try:
                output = json.loads(result["output"])
            except:
                output = {"raw_output": result.get("output", "")}
        
        return {
            "success": result["status"] == "SUCCEEDED",
            "status": result["status"],
            "execution_arn": execution_arn,
            "output": output,
            "workflow_name": workflow_name,
            "user_query": workflow_info.get("user_query", ""),
            "execution_time": (result.get("stopDate", result.get("startDate")) - result.get("startDate")).total_seconds() if result.get("stopDate") and result.get("startDate") else None,
            "timestamp": result.get("startDate").isoformat() if result.get("startDate") else None
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "workflow_name": workflow_name
        }

@app.get("/api")
def list_api_endpoints():
    """
    List all generated API endpoints
    """
    try:
        with open("./output_file/workflow_registry.json", "r") as f:
            registry = json.load(f)
        
        api_endpoints = []
        for name, info in registry.items():
            if name.startswith("api_"):
                api_endpoints.append({
                    "workflow_name": name,
                    "api_endpoint": info.get("invoke_url", ""),
                    "user_query": info.get("user_query", ""),
                    "created_at": info.get("timestamp", ""),
                    "description": f"API for: {info.get('user_query', name)}"
                })
        
        return {
            "success": True,
            "total_endpoints": len(api_endpoints),
            "api_endpoints": api_endpoints
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "api_endpoints": []
        }

@app.delete("/api/{workflow_name}")
def delete_api_endpoint(workflow_name: str):
    """
    Delete a generated API endpoint
    """
    try:
        with open("./output_file/workflow_registry.json", "r") as f:
            registry = json.load(f)
        
        if workflow_name not in registry:
            raise HTTPException(status_code=404, detail="API endpoint not found")
        
        # Delete from AWS Step Functions
        try:
            sf_client.delete_state_machine(stateMachineArn=registry[workflow_name]["arn"])
        except:
            pass  # Continue even if AWS deletion fails
        
        # Remove from registry
        del registry[workflow_name]
        
        with open("./output_file/workflow_registry.json", "w") as f:
            json.dump(registry, f, indent=2)
        
        return {
            "success": True,
            "message": f"API endpoint '{workflow_name}' deleted successfully"
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

# to run the FastAPI server, use the command: uvicorn main:app --reload

# example queries:
# user_query = "Create a graffiti-style image from a text prompt, enhance its quality, resize it to 800x600, convert it to a PDF, and send it via email."
# user_query ="It will be perfect if you play music that matches my mood. This is Anna."
# user_query ="Create a workflow that retrieves an image from S3, resizes it to 256x256 and returns the public URL of the resized image for display in the UI"


# "test"