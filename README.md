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


> **Note:** This workflow system is currently designed to run on AWS, leveraging AWS Step Functions, Lambda, and S3 for workflow orchestration, serverless execution, and file storage. With additional development, it could be adapted to other cloud providers (such as Azure Logic Apps, Google Cloud Workflows, etc.).

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

### Step 6: Start the Server the Dashboard (Frontend)
In your project root, run the following command to start the backend server:
```bash
uvicorn main:app --reload
```
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

### Step 7: Lambda Function Deployment


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

**Steps:**
1. Create a new Lambda function named `username2id`
2. Copy the code above
3. Paste it into the Lambda function editor
4. Save and deploy

**Important Notes**

- **Function Names:** The function names in your workflow must match the Lambda function names exactly
- **Input/Output Format:** Ensure your functions handle the expected input format and return the expected output format
- **Permissions:** Ensure your Lambda functions have the necessary IAM permissions for S3, Step Functions, etc.

**Dependencies for Image Processing Functions**

For functions like `resizeimage` that use PIL, you'll need to include the Pillow library. You can either:
- Use a Lambda Layer with Pillow
- Create a deployment package with Pillow included
- Use the AWS-provided Pillow layer


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


---



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



