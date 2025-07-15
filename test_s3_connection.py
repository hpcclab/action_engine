#!/usr/bin/env python3
"""Test S3 connection and bucket creation"""

import boto3
from utils.s3_handler import S3FileHandler
import os

print("Testing S3 Connection...")
print("=" * 50)

# Check AWS credentials
try:
    # Test if credentials are available
    session = boto3.Session()
    credentials = session.get_credentials()
    
    if credentials:
        print("✅ AWS credentials found")
        print(f"   Access Key ID: {credentials.access_key[:10]}...")
    else:
        print("❌ No AWS credentials found")
        print("\nPlease configure AWS credentials using one of these methods:")
        print("1. Run: aws configure")
        print("2. Set environment variables:")
        print("   export AWS_ACCESS_KEY_ID=your_key")
        print("   export AWS_SECRET_ACCESS_KEY=your_secret")
        print("   export AWS_DEFAULT_REGION=us-east-2")
        exit(1)
        
except Exception as e:
    print(f"❌ Error checking credentials: {e}")
    exit(1)

# Test S3 access
try:
    s3_client = boto3.client('s3', region_name='us-east-2')
    
    # List buckets
    response = s3_client.list_buckets()
    print(f"\n📦 Found {len(response['Buckets'])} existing buckets")
    
    # Test S3Handler
    print("\n🔧 Testing S3FileHandler...")
    s3_handler = S3FileHandler()
    
    # Try to upload a test file
    test_content = b"Hello from AutomaticWorkflowGeneration!"
    result = s3_handler.upload_file(
        file_content=test_content,
        filename="test_file.txt",
        content_type="text/plain"
    )
    
    if result["success"]:
        print("✅ Successfully uploaded test file!")
        print(f"   S3 Key: {result['s3_key']}")
        print(f"   S3 URL: {result['s3_url']}")
        
        # Try to get presigned URL
        presigned_url = s3_handler.get_presigned_url(result['s3_key'])
        if presigned_url:
            print(f"   Presigned URL: {presigned_url[:80]}...")
            
        # Clean up test file
        if s3_handler.delete_file(result['s3_key']):
            print("   ✅ Test file cleaned up")
    else:
        print(f"❌ Failed to upload test file: {result['error']}")
        
except Exception as e:
    print(f"❌ S3 error: {e}")
    print("\nPossible issues:")
    print("1. Check your AWS credentials")
    print("2. Ensure your AWS account has S3 permissions")
    print("3. Check if the region is correct (currently: us-east-2)")

print("\n" + "=" * 50)
print("Test complete!") 