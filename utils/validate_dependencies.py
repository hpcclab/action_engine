import json
from typing import List, Dict, Tuple, Set

def extract_step_dependencies(workflow_definition: Dict) -> Dict[str, Set[str]]:
    """
    Extract dependencies between workflow steps.
    Returns a dict where keys are step IDs and values are sets of step IDs they depend on.
    """
    dependencies = {}
    states = workflow_definition.get("States", {})
    
    for step_id, step_config in states.items():
        deps = set()
        
        # Check if this step uses output from previous steps
        # This is a simplified version - in reality, you'd parse the InputPath/Parameters
        if "Parameters" in step_config:
            params = str(step_config["Parameters"])
            # Look for references to other step outputs (e.g., $.t1.output)
            for other_step_id in states.keys():
                if f"$.{other_step_id}" in params or f"States.{other_step_id}" in params:
                    deps.add(other_step_id)
        
        dependencies[step_id] = deps
    
    return dependencies

def validate_workflow_order(current_order: List[str], dependencies: Dict[str, Set[str]]) -> Tuple[bool, List[str]]:
    """
    Validate if the given order respects all dependencies.
    Returns (is_valid, list_of_errors)
    """
    errors = []
    seen_steps = set()
    
    for step in current_order:
        # Check if all dependencies of this step have been seen
        step_deps = dependencies.get(step, set())
        missing_deps = step_deps - seen_steps
        
        if missing_deps:
            errors.append(f"Step '{step}' depends on {missing_deps} which come after it in the new order")
        
        seen_steps.add(step)
    
    return len(errors) == 0, errors

def can_reorder_workflow(workflow_definition: Dict, new_order: List[str]) -> Tuple[bool, List[str]]:
    """
    Check if a workflow can be reordered to the given order.
    Returns (can_reorder, list_of_reasons_if_not)
    """
    dependencies = extract_step_dependencies(workflow_definition)
    return validate_workflow_order(new_order, dependencies) 