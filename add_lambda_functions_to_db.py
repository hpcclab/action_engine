#!/usr/bin/env python3
"""
Script to add Lambda functions to the Action Engine's function database with the correct parameter schema.
"""

import json
import os

def add_lambda_functions_to_db():
    """Add the Lambda functions to the Action Engine's function database."""
    
    # Path to the function database
    db_path = "./db/api_info/api_information.json"
    
    # Read the existing database
    with open(db_path, 'r') as f:
        api_info = json.load(f)
    
    # Remove any previous versions of these functions
    camelcase_names = ["GetImageFromS3", "ResizeImage", "UploadImageToS3", "GeneratePublicURL"]
    api_info = [f for f in api_info if f.get('name') not in camelcase_names]
    
    # Get the next available ID
    next_id = max([func.get('Id', 0) for func in api_info]) + 1
    
    # Define the Lambda functions to add with the correct parameter schema
    lambda_functions = [
        {
            "Id": next_id,
            "name": "GetImageFromS3",
            "summary": "Retrieve the image file from S3 using the GetImageFromS3 Lambda function.",
            "description": "This Lambda function retrieves an image file from an S3 bucket given the full S3 URI.",
            "input_parameters_with_datatype": [
                {"name": "s3_key", "datatype": "String", "description": "The full S3 URI of the input image file (e.g., 's3://bucket/key')."}
            ],
            "output_parameters_with_datatype": []
        },
        {
            "Id": next_id + 1,
            "name": "ResizeImage",
            "summary": "Resize the retrieved image to 256x256 pixels using the ResizeImage Lambda function.",
            "description": "This Lambda function resizes an image to 256x256 pixels.",
            "input_parameters_with_datatype": [
                {"name": "image_s3_key", "datatype": "String", "description": "The S3 key of the image to resize."}
            ],
            "output_parameters_with_datatype": []
        },
        {
            "Id": next_id + 2,
            "name": "UploadImageToS3",
            "summary": "Upload the resized image back to S3 using the UploadImageToS3 Lambda function.",
            "description": "This Lambda function uploads an image to an S3 bucket.",
            "input_parameters_with_datatype": [
                {"name": "bucket", "datatype": "String", "description": "The S3 bucket name."},
                {"name": "key", "datatype": "String", "description": "The S3 object key for the uploaded file."},
                {"name": "image_data", "datatype": "String", "description": "The image data to upload (base64-encoded)."}
            ],
            "output_parameters_with_datatype": []
        },
        {
            "Id": next_id + 3,
            "name": "GeneratePublicURL",
            "summary": "Generate a public URL (HTTP link) for an image stored in S3 using the GeneratePublicURL Lambda function.",
            "description": "This Lambda function generates a public URL for an image stored in S3, making it accessible via HTTP.",
            "input_parameters_with_datatype": [
                {"name": "bucket", "datatype": "String", "description": "The S3 bucket name."},
                {"name": "key", "datatype": "String", "description": "The S3 object key for the image."}
            ],
            "output_parameters_with_datatype": []
        }
    ]
    
    # Add the new functions
    api_info.extend(lambda_functions)
    
    # Write back to the database
    with open(db_path, 'w') as f:
        json.dump(api_info, f, indent=2)
    print("Updated Lambda functions in the database with the correct parameter schema.")

if __name__ == "__main__":
    add_lambda_functions_to_db() 