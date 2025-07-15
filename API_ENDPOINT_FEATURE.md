# 🚀 Custom API Endpoint Generation Feature

## Overview

This is the **main feature** of the system! It allows users to **generate custom API endpoints** for any workflow described in natural language. Users get a ready-to-use REST API endpoint that they can call to execute their specific workflow.

## 🎯 How It Works

1. **User describes what they want** in natural language
2. **System generates a workflow** automatically 
3. **User gets a custom API endpoint** they can use immediately
4. **Anyone can call the API** to execute that workflow

---

## 📡 API Endpoints

### 1. **Generate API Endpoint** (Main Feature)
```http
POST /generate-api-endpoint
```

**Request:**
```json
{
  "user_query": "Create a graffiti-style image from text, enhance quality, and convert to PDF",
  "description": "Image generation and processing API" // Optional
}
```

**Response:**
```json
{
  "success": true,
  "message": "Custom API endpoint generated successfully!",
  "api_endpoint": "http://localhost:8000/api/api_Create_graffiti_style_image_a1b2c3d4",
  "workflow_name": "api_Create_graffiti_style_image_a1b2c3d4",
  "user_query": "Create a graffiti-style image from text, enhance quality, and convert to PDF",
  "description": "Image generation and processing API",
  "usage": {
    "method": "POST",
    "url": "http://localhost:8000/api/api_Create_graffiti_style_image_a1b2c3d4",
    "body": {
      "input_data": "Optional: any input data for the workflow"
    },
    "example_curl": "curl -X POST \"http://localhost:8000/api/api_Create_graffiti_style_image_a1b2c3d4\" \\\n  -H \"Content-Type: application/json\" \\\n  -d '{\"input_data\": \"your data here\"}'"
  },
  "capabilities": ["Generate graffiti image", "Enhance image quality", "Convert to PDF"],
  "required_functions": ["text_to_image", "enhance_image", "convert_to_pdf"],
  "estimated_execution_time": "1-10 seconds"
}
```

### 2. **Execute Custom Workflow**
```http
POST /api/{workflow_name}
```

**Request:**
```json
{
  "input_data": "Make a graffiti image saying 'Hello World'"
}
```

**Response:**
```json
{
  "success": true,
  "status": "SUCCEEDED",
  "execution_arn": "arn:aws:states:...",
  "output": {
    "message": "Workflow completed successfully",
    "generated_files": ["graffiti_image.pdf"],
    "image_url": "https://example.com/generated-image.jpg"
  },
  "workflow_name": "api_Create_graffiti_style_image_a1b2c3d4",
  "user_query": "Create a graffiti-style image from text, enhance quality, and convert to PDF",
  "execution_time": 3.2,
  "timestamp": "2025-06-12T10:30:00Z"
}
```

### 3. **List All API Endpoints**
```http
GET /api
```

**Response:**
```json
{
  "success": true,
  "total_endpoints": 5,
  "api_endpoints": [
    {
      "workflow_name": "api_Create_graffiti_style_image_a1b2c3d4",
      "api_endpoint": "http://localhost:8000/api/api_Create_graffiti_style_image_a1b2c3d4",
      "user_query": "Create a graffiti-style image from text, enhance quality, and convert to PDF",
      "created_at": "2025-06-12T10:25:00Z",
      "description": "API for: Create a graffiti-style image from text, enhance quality, and convert to PDF"
    }
  ]
}
```

### 4. **Delete API Endpoint**
```http
DELETE /api/{workflow_name}
```

**Response:**
```json
{
  "success": true,
  "message": "API endpoint 'api_Create_graffiti_style_image_a1b2c3d4' deleted successfully"
}
```

---

## 🔥 Use Cases

### **1. Business Process Automation**
```json
{
  "user_query": "Process invoice: extract data, validate, send for approval, and store in database"
}
```
→ Get API: `/api/api_Process_invoice_extract_b2c4d6e8`

### **2. Content Generation**
```json
{
  "user_query": "Generate social media posts from blog articles with hashtags and schedule posting"
}
```
→ Get API: `/api/api_Generate_social_media_posts_c3e5f7g9`

### **3. Data Processing**
```json
{
  "user_query": "Analyze CSV data, generate charts, and send email report to stakeholders"
}
```
→ Get API: `/api/api_Analyze_CSV_data_generate_d4f6h8j0`

### **4. E-commerce Workflows**
```json
{
  "user_query": "Process order: validate payment, update inventory, ship product, and notify customer"
}
```
→ Get API: `/api/api_Process_order_validate_e5g7i9k1`

---

## 💡 Integration Examples

### **JavaScript/Node.js**
```javascript
// Generate API endpoint
const response = await fetch('http://localhost:8000/generate-api-endpoint', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    user_query: "Resize images to thumbnails and upload to cloud storage",
    description: "Image processing API"
  })
});

const { api_endpoint } = await response.json();

// Use the generated API
const result = await fetch(api_endpoint, {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    input_data: { image_url: "https://example.com/image.jpg" }
  })
});

const workflowResult = await result.json();
console.log(workflowResult.output);
```

### **Python**
```python
import requests

# Generate API endpoint
response = requests.post('http://localhost:8000/generate-api-endpoint', json={
    "user_query": "Convert documents to PDF and extract text content",
    "description": "Document processing API"
})

api_endpoint = response.json()['api_endpoint']

# Use the generated API
result = requests.post(api_endpoint, json={
    "input_data": {"document_url": "https://example.com/doc.docx"}
})

print(result.json()['output'])
```

### **cURL**
```bash
# Generate API endpoint
curl -X POST "http://localhost:8000/generate-api-endpoint" \
  -H "Content-Type: application/json" \
  -d '{
    "user_query": "Scan QR codes from images and store data in spreadsheet",
    "description": "QR code processing API"
  }'

# Use the generated API (replace with actual endpoint from response)
curl -X POST "http://localhost:8000/api/api_Scan_QR_codes_f6h8j0k2" \
  -H "Content-Type: application/json" \
  -d '{"input_data": {"image_urls": ["https://example.com/qr1.jpg"]}}'
```

---

## 🎉 Key Benefits

### **1. Instant API Creation**
- Describe what you want in plain English
- Get a working API endpoint in seconds
- No coding or configuration required

### **2. Ready for Production**
- Generated APIs are fully functional
- Built on AWS Step Functions (scalable & reliable)
- Automatic error handling and retries

### **3. Universal Integration**
- Standard REST API format
- Works with any programming language
- Easy to integrate into existing systems

### **4. Workflow Intelligence**
- Automatically determines required steps
- Optimizes execution order
- Handles dependencies between tasks

### **5. Comprehensive Management**
- List all generated APIs
- Delete unused endpoints
- Track usage and performance

---

## 🛠️ Technical Details

### **Workflow Generation Process**
1. **Natural Language Processing**: Parse user query into tasks
2. **Function Identification**: Map tasks to available functions
3. **Workflow Optimization**: Arrange tasks in optimal order
4. **Dependency Resolution**: Handle inter-task dependencies
5. **AWS Integration**: Deploy as Step Function
6. **API Endpoint Creation**: Generate REST endpoint

### **Unique Naming System**
- Format: `api_{safe_query}_{hash}`
- Safe query: Alphanumeric version of user query (max 30 chars)
- Hash: MD5 hash of original query (8 chars)
- Example: `api_Create_graffiti_style_image_a1b2c3d4`

### **Execution Engine**
- **AWS Step Functions**: Serverless workflow orchestration
- **Automatic Scaling**: Handles any number of concurrent requests
- **Error Handling**: Built-in retry and error management
- **Monitoring**: Full execution tracking and logging

---

## 🚀 Getting Started

### **1. Generate Your First API**
```bash
curl -X POST "http://localhost:8000/generate-api-endpoint" \
  -H "Content-Type: application/json" \
  -d '{
    "user_query": "Send welcome email to new users with attachment",
    "description": "User onboarding API"
  }'
```

### **2. Test the Generated API**
Use the `api_endpoint` from the response:
```bash
curl -X POST "{your_api_endpoint}" \
  -H "Content-Type: application/json" \
  -d '{"input_data": {"user_email": "new@example.com", "username": "John"}}'
```

### **3. Integrate into Your App**
Copy the endpoint URL and integration code from the response!

---

## 🎯 This Is The Power

**Traditional Approach:**
1. Write code for workflow logic
2. Set up infrastructure 
3. Deploy and configure
4. Create API endpoints
5. Handle errors and scaling
6. ⏱️ **Time: Days/Weeks**

**With This System:**
1. Describe what you want
2. ⏱️ **Time: Seconds**
3. ✅ **Ready-to-use API!**

Transform any workflow idea into a production-ready API endpoint instantly! 🚀 