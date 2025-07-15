import boto3
import os
import uuid
import time
from botocore.exceptions import ClientError
from typing import Optional, Dict, Any
import mimetypes
from urllib.parse import unquote
import re

class S3FileHandler:
    def __init__(self, bucket_name: str = "automatic-workflow-files", region: str = "us-east-2"):
        self.bucket_name = bucket_name
        self.region = region
        self.s3_client = boto3.client('s3', region_name=region)
        self._ensure_bucket_exists()
    
    def _ensure_bucket_exists(self):
        """Create bucket if it doesn't exist"""
        try:
            self.s3_client.head_bucket(Bucket=self.bucket_name)
            print(f"✅ S3 bucket exists: {self.bucket_name}")
        except ClientError as e:
            error_code = e.response['Error']['Code']
            
            if error_code == '404':
                # Bucket doesn't exist, try to create it
                try:
                    if self.region == 'us-east-1':
                        self.s3_client.create_bucket(Bucket=self.bucket_name)
                    else:
                        self.s3_client.create_bucket(
                            Bucket=self.bucket_name,
                            CreateBucketConfiguration={'LocationConstraint': self.region}
                        )
                    print(f"✅ Created S3 bucket: {self.bucket_name}")
                except ClientError as create_error:
                    error_code = create_error.response['Error']['Code']
                    if error_code == 'BucketAlreadyOwnedByYou':
                        print(f"✅ S3 bucket already exists: {self.bucket_name}")
                    elif error_code == 'BucketAlreadyExists':
                        # Try a unique bucket name
                        import time
                        self.bucket_name = f"{self.bucket_name}-{int(time.time())}"
                        print(f"⚠️ Bucket name taken, using: {self.bucket_name}")
                        self._ensure_bucket_exists()  # Recursive call with new name
                    else:
                        print(f"⚠️ Could not create bucket: {create_error}")
                        # Continue anyway - bucket might exist but we can't check
            elif error_code == '403':
                # Access denied - bucket might exist but we can't check
                print(f"⚠️ Cannot verify bucket existence (permission denied), continuing anyway...")
            else:
                print(f"⚠️ Error checking bucket: {e}")
    
    def _to_ascii(self, s: str) -> str:
        # Remove or replace non-ASCII characters
        return re.sub(r'[^\x00-\x7F]+', '', s)

    def upload_file(self, file_content: bytes, filename: str, content_type: str = None) -> Dict[str, Any]:
        """Upload file to S3 and return file info"""
        try:
            # Generate unique filename
            file_extension = os.path.splitext(filename)[1]
            unique_filename = f"{uuid.uuid4()}{file_extension}"
            
            # Determine content type
            if not content_type:
                content_type, _ = mimetypes.guess_type(filename)
                if not content_type:
                    content_type = 'application/octet-stream'
            
            # Sanitize original filename for S3 metadata
            safe_filename = self._to_ascii(filename)
            
            # Upload to S3
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=unique_filename,
                Body=file_content,
                ContentType=content_type,
                Metadata={
                    'original-filename': safe_filename,
                    'upload-timestamp': str(int(time.time()) if hasattr(time, 'time') else 0)
                }
            )
            
            # Generate S3 URL
            s3_url = f"s3://{self.bucket_name}/{unique_filename}"
            public_url = f"https://{self.bucket_name}.s3.{self.region}.amazonaws.com/{unique_filename}"
            
            return {
                "success": True,
                "s3_key": unique_filename,
                "s3_url": s3_url,
                "public_url": public_url,
                "original_filename": filename,
                "content_type": content_type,
                "file_size": len(file_content)
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_presigned_url(self, s3_key: str, expiration: int = 3600) -> Optional[str]:
        """Generate a presigned URL for secure file access"""
        try:
            response = self.s3_client.generate_presigned_url(
                'get_object',
                Params={'Bucket': self.bucket_name, 'Key': s3_key},
                ExpiresIn=expiration
            )
            return response
        except Exception as e:
            print(f"Error generating presigned URL: {e}")
            return None
    
    def delete_file(self, s3_key: str) -> bool:
        """Delete file from S3"""
        try:
            self.s3_client.delete_object(Bucket=self.bucket_name, Key=s3_key)
            return True
        except Exception as e:
            print(f"Error deleting file: {e}")
            return False
    
    def list_workflow_files(self, workflow_id: str) -> list:
        """List all files associated with a workflow"""
        try:
            response = self.s3_client.list_objects_v2(
                Bucket=self.bucket_name,
                Prefix=f"workflows/{workflow_id}/"
            )
            
            files = []
            for obj in response.get('Contents', []):
                files.append({
                    'key': obj['Key'],
                    'size': obj['Size'],
                    'last_modified': obj['LastModified'].isoformat(),
                    'url': self.get_presigned_url(obj['Key'])
                })
            return files
        except Exception as e:
            print(f"Error listing files: {e}")
            return []

    def get_file_info(self, s3_key: str) -> Optional[Dict[str, Any]]:
        """Get metadata about a file in S3"""
        try:
            response = self.s3_client.head_object(Bucket=self.bucket_name, Key=s3_key)
            return {
                'content_type': response.get('ContentType'),
                'content_length': response.get('ContentLength'),
                'last_modified': response.get('LastModified'),
                'metadata': response.get('Metadata', {})
            }
        except Exception as e:
            print(f"Error getting file info: {e}")
            return None 