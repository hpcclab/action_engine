#!/usr/bin/env python3
"""
Debug script to test the function identifier and see what's happening
"""

import sys
import os
sys.path.append(os.path.abspath('.'))

from utils.func_identifier import func_identifier, find_topk_functions, read_json_to_dict
from utils.subtask_div import subtask_diviser
from utils.llms import get_model

def test_function_selection():
    """Test the function selection process"""
    
    print("🔍 Debugging Function Selection")
    print("=" * 50)
    
    # Test query
    test_query = "Using the input image file, create a workflow to: 1. Get the image from S3. 2. Resize the image to 256x256 pixels. 3. Upload the resized image to S3. 4. Generate a public URL for the resized image."
    
    print(f"Test Query: {test_query}")
    print()
    
    # Load the database
    print("📊 Loading function database...")
    api_info = read_json_to_dict("./db/api_info/api_information.json")
    print(f"Total functions in database: {len(api_info)}")
    
    # Check if our Lambda functions are in the database
    print("\n🔍 Checking for Lambda functions in database:")
    lambda_functions = ["getimagefroms3", "resizeimage", "uploadimagetos3", "generatepublicurl"]
    for func_name in lambda_functions:
        found = any(func["name"] == func_name for func in api_info)
        print(f"  {func_name}: {'✅ Found' if found else '❌ Not found'}")
    
    # Test similarity search
    print("\n🔍 Testing similarity search for 'resize image':")
    top_functions = find_topk_functions("resize image", api_info, 10)
    print("Top 10 functions for 'resize image':")
    for i, func in enumerate(top_functions, 1):
        print(f"  {i}. {func['name']} - {func['summary'][:100]}...")
    
    # Test the full function identifier
    print("\n🔍 Testing full function identifier:")
    try:
        model_result = get_model("gpt-4o")
        if isinstance(model_result, tuple):
            model = model_result[0]
        else:
            model = model_result
            
        task_list = subtask_diviser(model, test_query)
        print(f"Task list: {task_list}")
        
        selected_functions, NO_FUNC, non_func_list = func_identifier(model, task_list["Tasks"], test_query)
        
        print(f"\nSelected functions: {len(selected_functions)}")
        for i, func in enumerate(selected_functions, 1):
            print(f"  {i}. {func.get('name', 'N/A')} - {func.get('task_description', 'N/A')}")
        
        print(f"NO_FUNC: {NO_FUNC}")
        print(f"Non-function list: {non_func_list}")
        
    except Exception as e:
        print(f"❌ Error in function identifier: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_function_selection() 