#!/usr/bin/env python3
"""
Demo Image Processing Workflow

This script demonstrates how to create workflows that process image inputs from S3.
It shows different types of image processing operations that can be chained together.
"""

import requests
import json
import time
from PIL import Image
import io
import base64

API_BASE = "http://localhost:8000"

def create_demo_image_workflow():
    """
    Create a demo workflow that processes images:
    1. Upload sample image
    2. Generate workflow for image processing
    3. Execute and display results
    """
    
    # Sample workflow queries for image processing
    demo_queries = [
        {
            "name": "Image Enhancement",
            "query": "Enhance the quality of the uploaded image, apply filters to improve clarity and color balance, then resize it to 1024x768 resolution",
            "image_type": "any"
        },
        {
            "name": "Style Transfer", 
            "query": "Apply artistic style transfer to the uploaded image, make it look like a watercolor painting, and save the result",
            "image_type": "photo"
        },
        {
            "name": "Object Detection",
            "query": "Analyze the uploaded image to detect and label all objects, create a new image with bounding boxes around detected objects",
            "image_type": "any"
        },
        {
            "name": "Background Removal",
            "query": "Remove the background from the uploaded image and replace it with a transparent background, save as PNG",
            "image_type": "photo"
        },
        {
            "name": "Image Analysis Report",
            "query": "Analyze the uploaded image and generate a detailed report including: image properties, color analysis, detected objects, estimated scene type, and quality metrics",
            "image_type": "any"
        }
    ]
    
    print("🖼️  Image Processing Workflow Demo")
    print("=" * 50)
    
    # Show available demo workflows
    print("\n📋 Available Demo Workflows:")
    for i, demo in enumerate(demo_queries, 1):
        print(f"{i}. {demo['name']}")
        print(f"   Query: {demo['query'][:80]}...")
        print(f"   Best for: {demo['image_type']} images")
        print()
    
    # Let user choose or use first one
    choice = input("Select a demo workflow (1-5) or press Enter for default [1]: ").strip()
    if choice.isdigit() and 1 <= int(choice) <= 5:
        selected_demo = demo_queries[int(choice) - 1]
    else:
        selected_demo = demo_queries[0]
    
    print(f"\n✅ Selected: {selected_demo['name']}")
    print(f"Query: {selected_demo['query']}")
    
    # Option to upload custom image or use sample
    use_sample = input("\nUse sample image? (y/n) [y]: ").strip().lower()
    
    if use_sample in ['', 'y', 'yes']:
        # Create a sample image
        image_path = create_sample_image()
        print(f"📷 Created sample image: {image_path}")
    else:
        image_path = input("Enter path to your image file: ").strip()
        if not image_path or not os.path.exists(image_path):
            print("❌ Image file not found. Using sample image instead.")
            image_path = create_sample_image()
    
    # Upload image
    print(f"\n⬆️  Uploading image to S3...")
    file_info = upload_image(image_path)
    
    if not file_info:
        print("❌ Failed to upload image")
        return
    
    print(f"✅ Image uploaded successfully:")
    print(f"   Original filename: {file_info['original_filename']}")
    print(f"   S3 URL: {file_info['s3_url']}")
    print(f"   File size: {format_file_size(file_info['file_size'])}")
    
    # Generate and run workflow
    print(f"\n🚀 Generating workflow...")
    result = generate_workflow_with_files(selected_demo['query'], [file_info['s3_url']])
    
    if result and result.get('execution_arn'):
        print(f"✅ Workflow started successfully!")
        print(f"   Execution ARN: {result['execution_arn']}")
        print(f"   API Endpoint: {result['invoke_api_endpoint']}")
        
        # Monitor execution
        print(f"\n⏳ Monitoring execution...")
        final_status = monitor_execution(result['execution_arn'])
        
        # Display results
        print(f"\n📊 Final Results:")
        display_results(final_status)
        
    else:
        print("❌ Failed to generate workflow")
        if result:
            print(f"Error: {result.get('error', 'Unknown error')}")

def create_sample_image():
    """Create a sample image for testing"""
    import os
    
    # Create a simple colored rectangle image
    img = Image.new('RGB', (800, 600), color='lightblue')
    
    # Add some visual elements (if PIL supports drawing)
    try:
        from PIL import ImageDraw, ImageFont
        draw = ImageDraw.Draw(img)
        
        # Draw some rectangles and text
        draw.rectangle([100, 100, 300, 200], fill='red', outline='darkred', width=3)
        draw.rectangle([400, 300, 600, 400], fill='green', outline='darkgreen', width=3)
        draw.rectangle([200, 350, 500, 450], fill='yellow', outline='orange', width=3)
        
        # Add text
        try:
            font = ImageFont.load_default()
            draw.text((50, 50), "Sample Image for Workflow Demo", fill='black', font=font)
            draw.text((50, 500), "Created by AutomaticWorkflowGeneration", fill='navy', font=font)
        except:
            pass
            
    except ImportError:
        pass
    
    # Save to temp file
    sample_path = 'sample_image_demo.jpg'
    img.save(sample_path, 'JPEG', quality=95)
    return sample_path

def upload_image(image_path):
    """Upload image to S3 via the API"""
    try:
        with open(image_path, 'rb') as f:
            files = {'files': (image_path, f, 'image/jpeg')}
            response = requests.post(f"{API_BASE}/upload-files", files=files)
        
        if response.status_code == 200:
            result = response.json()
            uploaded_files = result.get('uploaded_files', [])
            if uploaded_files and uploaded_files[0].get('success', True):
                return uploaded_files[0]
        
        print(f"Upload failed: {response.status_code} - {response.text}")
        return None
        
    except Exception as e:
        print(f"Upload error: {e}")
        return None

def generate_workflow_with_files(query, file_urls):
    """Generate and run workflow with file inputs"""
    try:
        payload = {
            "user_query": query,
            "file_urls": file_urls
        }
        
        response = requests.post(
            f"{API_BASE}/generate-and-run-workflow-with-files",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Workflow generation failed: {response.status_code} - {response.text}")
            return {"error": f"HTTP {response.status_code}"}
            
    except Exception as e:
        print(f"Request error: {e}")
        return {"error": str(e)}

def monitor_execution(execution_arn):
    """Monitor workflow execution until completion"""
    max_polls = 20
    poll_interval = 5
    
    for i in range(max_polls):
        try:
            response = requests.get(
                f"{API_BASE}/execution-status",
                params={"executionArn": execution_arn}
            )
            
            if response.status_code == 200:
                status = response.json()
                current_status = status.get("status", "UNKNOWN")
                
                print(f"   Status: {current_status} ({i+1}/{max_polls})")
                
                if current_status in ["SUCCEEDED", "FAILED", "TIMED_OUT", "ABORTED"]:
                    return status
                    
            time.sleep(poll_interval)
            
        except Exception as e:
            print(f"   Polling error: {e}")
            
    print("   ⚠️  Timeout waiting for completion")
    return {"status": "TIMEOUT"}

def display_results(status_result):
    """Display the workflow execution results"""
    status = status_result.get("status", "UNKNOWN")
    
    if status == "SUCCEEDED":
        print("✅ Workflow completed successfully!")
        
        output = status_result.get("output", {})
        if isinstance(output, str):
            try:
                output = json.loads(output)
            except:
                print(f"   Raw output: {output}")
                return
        
        # Display text output
        if output.get("message"):
            print(f"   Message: {output['message']}")
            
        # Display generated files
        files = output.get("generated_files", output.get("files", []))
        if files:
            print(f"\n📁 Generated Files ({len(files)}):")
            for i, file_info in enumerate(files, 1):
                print(f"   {i}. {file_info.get('filename', 'Unknown')}")
                print(f"      Type: {file_info.get('content_type', 'Unknown')}")
                print(f"      URL: {file_info.get('url', 'N/A')}")
                if file_info.get('description'):
                    print(f"      Description: {file_info['description']}")
                print()
        
        # Display metadata
        metadata = output.get("metadata", {})
        if metadata:
            print(f"📋 Execution Metadata:")
            for key, value in metadata.items():
                print(f"   {key}: {value}")
                
    elif status == "FAILED":
        print("❌ Workflow execution failed")
        error = status_result.get("error", "Unknown error")
        print(f"   Error: {error}")
        
    else:
        print(f"⚠️  Workflow status: {status}")
        
    # Display timing info
    start_date = status_result.get("startDate")
    stop_date = status_result.get("stopDate")
    if start_date and stop_date:
        print(f"\n⏱️  Execution Time:")
        print(f"   Started: {start_date}")
        print(f"   Finished: {stop_date}")

def format_file_size(bytes_size):
    """Format file size in human readable format"""
    if bytes_size == 0:
        return "0 B"
    size_names = ["B", "KB", "MB", "GB"]
    i = 0
    while bytes_size >= 1024 and i < len(size_names) - 1:
        bytes_size /= 1024.0
        i += 1
    return f"{bytes_size:.1f} {size_names[i]}"

if __name__ == "__main__":
    import os
    try:
        create_demo_image_workflow()
    except KeyboardInterrupt:
        print("\n\n👋 Demo cancelled by user")
    except Exception as e:
        print(f"\n❌ Demo error: {e}")
        import traceback
        traceback.print_exc() 