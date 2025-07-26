# 🧠⚙️ Action Engine: Automatic Workflow Generation in FaaS

**Authors**: Akiharu Esashi, Pawissanutt Lertpongrujikorn, Mohsen Amini Salehi  
📍 University of North Texas  
🔗 [Project Website](https://hpcclab.org/) | 📜 [Preprint](UnderReview) 

---

## 🚀 Overview

**Action Engine** is an end-to-end system that **automates the generation of serverless (FaaS) workflows** from natural language queries using **Tool-Augmented Large Language Models (LLMs)**.

💡 **Why it matters:**  
Creating FaaS workflows traditionally requires manual effort, specialized platform knowledge (e.g., AWS Step Functions, Google Cloud Composer), and tight coupling with provider-specific APIs. Action Engine **eliminates these challenges** by generating executable, platform-independent workflows from human-readable descriptions — **no manual orchestration needed**.

---

## 📊 Evaluation & Results

We evaluated Action Engine using the Reverse Chain dataset against various baselines including **GPT-4o**, **Qwen-Coder-32B-Instruct**, and **Reverse Chain**.

📈 **Key Metrics:**
- **Function Selection Accuracy**: ~42% (Level 3)
- **Data Dependency F1 Score**: Competitive with GPT-4o Few-Shot CoT
- **Topological Order Accuracy**: Highest LCS among all baselines

🔍 **Insight**: Action Engine offers robust performance **even at higher workflow complexity**, highlighting its scalability and reliability in real-world FaaS systems.

---

## 📚 Citation

If you use this work, please cite:

```bibtex
@article{esashi2025actionengine,
  title={Action Engine: Automatic Workflow Generation in FaaS},
  author={Esashi, Akiharu and Lertpongrujikorn, Pawissanutt and Salehi, Mohsen Amini},
  journal={Preprint submitted to Elsevier},
  year={2025}
}
```

---

## 📬 Contact

- 📧 Akiharu Esashi: [akiharuesashi@my.unt.edu](mailto:akiharuesashi@my.unt.edu)  
- 💼 Mohsen Amini Salehi: [mohsen.aminisalehi@unt.edu](mailto:mohsen.aminisalehi@unt.edu)

---

# 🚀 Action Engine Dashboard Setup & Usage Guide

> **Action Engine UI** is a FastAPI-based platform for automatic workflow generation and execution, supporting file uploads, AWS Step Functions integration, and custom API endpoint creation from natural language queries.
![UI　Dashboard](frontend/public/images/ae_dashboard.png)
---


## System Requirements

### Prerequisites
- **Python 3.8+**
- **AWS Account** with Step Functions and S3 permissions
- **AWS CLI** configured with credentials (`aws configure`)
- **Node.js** (required for developing and building the React-based frontend in `/frontend`)
- **pip** (Python package manager)
- **API Keys/Tokens** (depending on your LLM choice):
  - **OpenAI API Key** (if using OpenAI models like GPT-4o, GPT-3.5) - Get from [OpenAI Platform](https://platform.openai.com/api-keys)
  - **Hugging Face Token** (if using Hugging Face models) - Get from [Hugging Face Settings](https://huggingface.co/settings/tokens)


---

## Setup Guide

### Step 1: Clone and Navigate
```bash
git clone https://github.com/Doonshin/action_engine.git
```

### Step 2: Create Virtual Environment
```bash
# Create virtual environment
# On Linux/macOS:
python3 -m venv venv
# On Windows:
# python -m venv venv

# Activate virtual environment
# On Linux/macOS:
source venv/bin/activate
# On Windows:
# venv\Scripts\activate
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```
### Step 4: Set Required Environment Variables in the `.env` File

Below is an example of what your `.env` file should look like. Replace the placeholder values with your actual credentials:


```
AWS_ACCOUNT_ID=YOUR_ACCOUNT_ID
AWS_ACCESS_KEY_ID=YOUR_AWS_ACCESS_KEY_ID
AWS_SECRET_ACCESS_KEY=YOUR_AWS_SECRET_ACCESS_KEY
AWS_DEFAULT_REGION=us-east-2
AWS_ROLE_ARN=arn:aws:iam::YOUR_ACCOUNT_ID:role/StepFunctionExecutionRole
OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
HUGGINGFACE_TOKEN=hf_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

### Step 5: Configure AWS IAM Permissions

Your AWS user needs the following permissions to run the Action Engine:

**Required IAM Policies:**
- `AWSStepFunctionsFullAccess` - For creating and managing Step Functions
- `AWSLambdaRole` - For Lambda function execution
- `IAMFullAccess` - For IAM role management
- `S3AutomaticWorkflowFilesAccess` - For S3 file operations

**How to attach policies:**

1. **Go to AWS Console** → IAM → Users
2. **Click on your user** (e.g., `action-engine-test`)
3. **Go to "Permissions" tab**
4. **Click "Add permissions"**
5. **Choose "Attach existing policies directly"**
6. **Search and select the required policies:**
   - `AWSStepFunctionsFullAccess`
   - `AWSLambdaRole` 
   - `IAMFullAccess`
7. **Click "Next" and "Add permissions"**

**Alternative: Create a custom policy** for more restrictive access:
```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "states:*",
                "lambda:*",
                "iam:*",
                "s3:*"
            ],
            "Resource": "*"
        }
    ]
}
```


### Step 7: Create Required Directories
```bash
mkdir -p output_file
chmod 755 output_file
```

### Step 8: Set Up S3 Bucket
- Create an S3 bucket named `automatic-workflow-files` (or update the code/config to use your bucket)
- Ensure your IAM role has access to this bucket

### Step 9: Start the Server
In your project root, run the following command to start the backend server:
```bash
uvicorn main:app --reload
```

### Step 10: Step 10: Start the Dashboard (Frontend)

Open a new terminal tab or window, then run the following commands to start the frontend development server:
```bash
cd frontend
npm install
npm start
```

**Access Points:**
- API: `http://127.0.0.1:8000`
- API Documentation: `http://127.0.0.1:8000/docs`
- Frontend: `http://localhost:3000` 

**Important:** Remember to activate your virtual environment before running the server:
```bash
source venv/bin/activate  # Linux/macOS
# or
# venv\Scripts\activate  # Windows
```

---

## Running the System

### Start the FastAPI Server
```bash
uvicorn main:app --reload
```


## Action Engine Dashboard Usage Guide

> This guide explains how to use the Action Engine web-based dashboard to generate, run, and manage workflows through the graphical interface.

### 1. Dashboard Access
- Open your browser and navigate to the dashboard
- View recent workflows, execution results, and recent queries

### 2. File Uploads
- Use the "Add File Inputs" button to upload files
- Files are uploaded to S3 and their URLs are returned for use in workflows

### 3. Workflow Generation
- Enter a natural language description of your workflow
- Optionally attach files
- Click "Generate & Run Workflow"
- The backend will:
  - Parse your query
  - Generate a workflow
  - Compile it to AWS Step Functions
  - Start execution and return the result

### 4. Manual Execution
- Use the "Manual Execution" section to invoke a workflow by URL with custom JSON input
---

## Demo Workflows

### Demo 1: Music Recommendation Workflow

**Prerequisites:**
> **Important:** Before running this demo, you must deploy the required Lambda functions to AWS. The workflow will fail if these functions don't exist in your AWS account.

**Required Lambda Functions:**
- `username2id` - Converts user name to user ID
- `getusermood` - Determines user's mood
- `recommendsong` - Recommends song based on mood
- `playmusic` - Returns music playing message

**Setup:**
1. Deploy the Lambda functions to AWS (see code examples below)
2. Open the Action Engine Dashboard
3. Enter the following query in the workflow box:
   > It will be perfect if you play music that matches my mood. This is Anna.
4. Click 'Generate & Run Workflow'
5. Wait for execution

**Expected Result:**
- The workflow will:
  - Convert the user name to a user ID
  - Detect the user's mood
  - Recommend a song
  - Return a message like: `Now playing: Happy Tune`

**Lambda Function Code Examples:**
> See the complete Lambda function code examples in the [Lambda Function Code Examples](#lambda-function-code-examples) section at the bottom of this README.

### Demo 2: S3 Image Resize Workflow

**Setup:**
1. Open the Action Engine Dashboard
2. Upload an image file using the 'Add File Inputs' button
3. Enter the following query in the workflow box:
   > Create a workflow that retrieves an image from S3, resizes it to 256x256 and returns the public URL of the resized image for display in the UI
4. Click 'Generate & Run Workflow'
5. Wait for execution

**Expected Result:**
- The workflow will:
  - Retrieve the uploaded image from S3
  - Resize it to 256x256
  - Upload the resized image
  - Return a public URL for the resized image

---

## Lambda Function Deployment

### How to Deploy Lambda Functions

1. **Create Lambda Functions in AWS Console:**
   - Go to AWS Lambda Console
   - Click "Create function"
   - Choose "Author from scratch"
   - Give your function a name (e.g., `username2id`, `getusermood`)
   - Select Python 3.9+ as runtime
   - Click "Create function"

2. **Copy & Paste Function Code:**
   - In the Lambda function editor, replace the default code with the function code from the demos
   - Each function should have the exact structure shown in the demo sections
   - Make sure to include all necessary imports (e.g., `import boto3`, `from PIL import Image`)

3. **Install Dependencies (if needed):**
   - For functions using external libraries (like PIL for image processing), you may need to create a deployment package
   - Use Lambda Layers or include dependencies in your deployment package

### Example: Copying the `username2id` Function

```python
def lambda_handler(event, context):
    user_name = event.get("user_name", "unknown")
    user_id = f"{user_name.lower()}_123"
    return {
        "user_id": user_id,
        "name": user_name  # Pass through
    }
```

**Steps:**
1. Create a new Lambda function named `username2id`
2. Copy the code above
3. Paste it into the Lambda function editor
4. Save and deploy

### Important Notes

- **Function Names:** The function names in your workflow must match the Lambda function names exactly
- **Input/Output Format:** Ensure your functions handle the expected input format and return the expected output format
- **Permissions:** Ensure your Lambda functions have the necessary IAM permissions for S3, Step Functions, etc.

### Dependencies for Image Processing Functions

For functions like `resizeimage` that use PIL, you'll need to include the Pillow library. You can either:
- Use a Lambda Layer with Pillow
- Create a deployment package with Pillow included
- Use the AWS-provided Pillow layer

---

## Lambda Function Code Examples

### Demo 1: Music Recommendation Workflow Functions

<details>
<summary><strong>username2id</strong> (Click to expand)</summary>

```python
def lambda_handler(event, context):
    user_name = event.get("user_name", "unknown")
    user_id = f"{user_name.lower()}_123"
    return {
        "user_id": user_id,
        "name": user_name  # Pass through
    }
```
</details>

<details>
<summary><strong>getusermood</strong> (Click to expand)</summary>

```python
def lambda_handler(event, context):
    user_id = event.get("user_id", "unknown_id")
    user_name = event.get("name", "unknown")
    mood = "happy" if "anna" in user_name.lower() else "neutral"
    return {
        "mood": mood,
        "name": user_name  # Pass through
    }
```
</details>

<details>
<summary><strong>recommendsong</strong> (Click to expand)</summary>

```python
def lambda_handler(event, context):
    mood = event.get("mood", "neutral")
    if mood == "happy":
        song = "Happy Tune"
    elif mood == "sad":
        song = "Melancholy Melody"
    else:
        song = "Lo-fi Chill"
    return {
        "recommended_song": song
    }
```
</details>

<details>
<summary><strong>playmusic</strong> (Click to expand)</summary>

```python
def lambda_handler(event, context):
    song_title = event.get("recommended_song", "unknown song")
    name = event.get("name", "someone")
    return {
        "message": f"Now playing: {song_title}",
        "name": name
    }
```
</details>

### Demo 2: S3 Image Resize Workflow Functions

<details>
<summary><strong>getimagefroms3</strong> (Click to expand)</summary>

```python
import boto3
import os
import json
import uuid
import base64 

s3_client = boto3.client('s3')

def lambda_handler(event, context):
    """
    1. Gets an image from S3 by intelligently handling input from the Action Engine or direct tests.
    2. Packages it into a JSON with metadata.
    3. Saves this JSON to a temporary key in S3 (the "claim check").
    4. Returns the temporary S3 key to keep the payload small.
    """
    
    bucket_name = None
    original_s3_key = None

    # Handle input from Action Engine UI ('input_files') or direct invocation ('s3_key')
    if 'input_files' in event and isinstance(event['input_files'], list) and event['input_files']:
        s3_uri = event['input_files'][0]  # Take the first file from the list
        # s3_uri is expected in the format 's3://bucket-name/key'
        if s3_uri.startswith("s3://"):
            uri_parts = s3_uri.replace("s3://", "").split('/', 1)
            if len(uri_parts) == 2:
                bucket_name, original_s3_key = uri_parts
    elif 's3_key' in event:
        # Fallback for direct testing
        original_s3_key = event.get('s3_key')
        bucket_name = event.get('bucket_name', 'automatic-workflow-files')  # Default bucket if not provided

    # Validate that we have the necessary details
    if not original_s3_key or not bucket_name:
        return {
            "success": False, 
            "error": "Input is invalid. It must include 'input_files' (as s3://bucket/key) or both 's3_key' and 'bucket_name'."
        }

    try:
        # Step 1: Get the original image
        response = s3_client.get_object(Bucket=bucket_name, Key=original_s3_key)
        image_data = response['Body'].read()
        
        # Step 2: Create the data package (this would be too large to return directly)
        data_package = {
            "image_data_b64": base64.b64encode(image_data).decode('utf-8'),
            "content_type": response.get('ContentType', 'image/jpeg'),
            "original_s3_key": original_s3_key,
            "bucket_name": bucket_name
        }
        
        # Step 3: Save this package to a new temporary key in S3
        temp_key = f"temp/{uuid.uuid4().hex}.json"
        s3_client.put_object(
            Bucket=bucket_name,
            Key=temp_key,
            Body=json.dumps(data_package),
            ContentType='application/json'
        )
        
        # Step 4: Return the "claim check" (the reference to the temp file)
        return {
            "success": True,
            "claim_check_s3_key": temp_key,
            "bucket_name": bucket_name
        }

    except Exception as e:
        return {"success": False, "error": str(e)}
```
</details>

<details>
<summary><strong>resizeimage</strong> (Click to expand)</summary>

```python
import boto3
import json
import base64
from PIL import Image
import io

s3_client = boto3.client('s3')

def lambda_handler(event, context):
    """
    1. Receives a "claim check" (an S3 key to a JSON file).
    2. Downloads and reads the JSON file to get the image data.
    3. Resizes the image.
    4. Returns the RESIZED image data as a Base64 string.
    """
    claim_check_s3_key = event.get('claim_check_s3_key')
    bucket_name = event.get('bucket_name')

    if not claim_check_s3_key or not bucket_name:
        return {"success": False, "error": "Input missing 'claim_check_s3_key' or 'bucket_name'."}

    try:
        # Step 1: Use the claim check to get the data package from S3
        response = s3_client.get_object(Bucket=bucket_name, Key=claim_check_s3_key)
        data_package = json.loads(response['Body'].read())
        
        image_bytes = base64.b64decode(data_package['image_data_b64'])
        image = Image.open(io.BytesIO(image_bytes))

        # Step 2: Resize the image
        target_width, target_height = 256, 256
        new_image = Image.new('RGB', (target_width, target_height), 'white')
        image.thumbnail((target_width, target_height), Image.Resampling.LANCZOS)
        new_image.paste(image, ((target_width - image.width) // 2, (target_height - image.height) // 2))

        # Step 3: Save resized image to a buffer and encode to Base64
        output_buffer = io.BytesIO()
        new_image.save(output_buffer, format='JPEG', quality=95)
        resized_b64 = base64.b64encode(output_buffer.getvalue()).decode('utf-8')

        # Clean up the temporary file from S3
        s3_client.delete_object(Bucket=bucket_name, Key=claim_check_s3_key)

        # Step 4: Return the resized data, which should be small enough
        return {
            "success": True,
            "resized_image_data_b64": resized_b64,
            "content_type": "image/jpeg",
            "bucket_name": bucket_name,
            "original_s3_key": data_package['original_s3_key']
        }

    except Exception as e:
        return {"success": False, "error": str(e)}
```
</details>

<details>
<summary><strong>uploadimagetos3</strong> (Click to expand)</summary>

```python
import boto3
import base64
import os

s3_client = boto3.client('s3')

def lambda_handler(event, context):
    """
    1. Receives the Base64-encoded RESIZED image data.
    2. Decodes it and uploads it to a final destination in S3.
    3. Returns the final S3 key.
    """
    # This is the Base64 data from the 'resizeimage' function
    resized_b64 = event.get('resized_image_data_b64') # <--- We expect this key
    
    # Get the other necessary info from the event payload
    bucket_name = event.get('bucket_name')
    original_s3_key = event.get('original_s3_key')

    if not resized_b64 or not bucket_name or not original_s3_key:
        # Construct a detailed error message for easier debugging
        missing = []
        if not resized_b64: missing.append("'resized_image_data_b64'")
        if not bucket_name: missing.append("'bucket_name'")
        if not original_s3_key: missing.append("'original_s3_key'")
        return {"success": False, "error": f"Input missing required keys: {', '.join(missing)}."}
        
    try:
        image_bytes = base64.b64decode(resized_b64)
        
        # Create the new, final key for the resized image
        base, ext = os.path.splitext(original_s3_key)
        final_s3_key = f"resized/{os.path.basename(base)}_256x256{ext or '.jpg'}"
        
        s3_client.put_object(
            Bucket=bucket_name,
            Key=final_s3_key,
            Body=image_bytes,
            ContentType=event.get('content_type', 'image/jpeg')
        )
        
        # Pass the final key to the next function
        return {
            "success": True,
            "final_s3_key": final_s3_key, 
            "bucket_name": bucket_name
        }
        
    except Exception as e:
        return {"success": False, "error": str(e)}
```
</details>

<details>
<summary><strong>generatepublicurl</strong> (Click to expand)</summary>

```python
import boto3
import os

def lambda_handler(event, context):
    """
    Receives the final S3 key from the previous step and generates a 
    public URL for it.
    """
    # Look for 'final_s3_key' from the event payload.
    final_s3_key = event.get('final_s3_key')
    
    if not final_s3_key:
        # This error message is more specific to help with future debugging.
        return {"success": False, "error": "Input did not include 'final_s3_key'."}
        
    bucket_name = event.get('bucket_name')
    region = os.environ.get('AWS_REGION', 'us-east-2')
    
    try:
        # Construct the public URL
        public_url = f"https://{bucket_name}.s3.{region}.amazonaws.com/{final_s3_key}"
        
        # This is the final output of the entire workflow
        return {
            "success": True,
            "public_url": public_url,
            "s3_key": final_s3_key
        }
        
    except Exception as e:
        return {"success": False, "error": str(e)}
```
</details>

---

## Cloud Provider Note

> **Note:** This workflow system is currently designed to run on AWS, leveraging AWS Step Functions, Lambda, and S3 for workflow orchestration, serverless execution, and file storage. With additional development, it could be adapted to other cloud providers (such as Azure Logic Apps, Google Cloud Workflows, etc.).