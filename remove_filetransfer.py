#!/usr/bin/env python3
"""
Script to remove the FileTransfer function and old lowercase Lambda functions from the Action Engine's function database.
This will prevent interference with Lambda function selection.
"""

import json
import os

def clean_database():
    """Clean the Action Engine's function database by removing problematic functions."""
    
    # Path to the function database
    db_path = "./db/api_info/api_information.json"
    
    # Read the existing database
    with open(db_path, 'r') as f:
        api_info = json.load(f)
    
    print(f"Original database size: {len(api_info)} functions")
    
    # Functions to remove
    functions_to_remove = [
        'FileTransfer',  # Generic function that interferes with image processing
        'getimagefroms3',  # Old lowercase version
        'resizeimage',     # Old lowercase version  
        'uploadimagetos3', # Old lowercase version
        'generatepublicurl' # Old lowercase version
    ]
    
    # Remove the functions
    original_count = len(api_info)
    api_info = [f for f in api_info if f.get('name') not in functions_to_remove]
    new_count = len(api_info)
    
    removed_count = original_count - new_count
    print(f"✅ Removed {removed_count} functions. Database size: {original_count} -> {new_count}")
    
    # Write back to the database
    with open(db_path, 'w') as f:
        json.dump(api_info, f, indent=2)
    
    print("Database cleaned successfully!")

if __name__ == "__main__":
    clean_database() 