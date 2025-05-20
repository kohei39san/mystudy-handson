import os
import json
import boto3
import logging
import tempfile
import subprocess
import shutil
from datetime import datetime
from typing import Dict, Any, List

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Initialize AWS clients
s3 = boto3.client('s3')
ssm = boto3.client('ssm')

def get_parameter(name: str) -> str:
    """
    Get a parameter from SSM Parameter Store
    """
    response = ssm.get_parameter(
        Name=name,
        WithDecryption=True
    )
    return response['Parameter']['Value']

def clone_repository(repo_url: str, github_token: str, local_path: str) -> bool:
    """
    Clone a GitHub repository to a local path
    """
    try:
        # Format the URL with the token for authentication
        auth_url = repo_url.replace('https://', f'https://{github_token}@')
        
        # Clone the repository
        subprocess.run(
            ['git', 'clone', '--depth', '1', auth_url, local_path],
            check=True,
            capture_output=True
        )
        
        return True
    
    except subprocess.CalledProcessError as e:
        logger.error(f"Error cloning repository: {e.stderr.decode('utf-8')}")
        return False
    
    except Exception as e:
        logger.error(f"Exception cloning repository: {str(e)}")
        return False

def upload_directory_to_s3(local_path: str, bucket_name: str, prefix: str = '') -> List[Dict[str, str]]:
    """
    Upload a directory to S3
    """
    uploaded_files = []
    
    try:
        # Walk through the directory
        for root, dirs, files in os.walk(local_path):
            for file in files:
                # Skip .git files
                if '.git' in root:
                    continue
                
                # Get the full local path
                local_file_path = os.path.join(root, file)
                
                # Get the relative path from the local_path
                relative_path = os.path.relpath(local_file_path, local_path)
                
                # Create the S3 key
                s3_key = os.path.join(prefix, relative_path).replace('\\', '/')
                
                # Upload the file
                s3.upload_file(local_file_path, bucket_name, s3_key)
                
                # Add to the list of uploaded files
                uploaded_files.append({
                    'local_path': local_file_path,
                    's3_key': s3_key
                })
                
                logger.info(f"Uploaded {local_file_path} to s3://{bucket_name}/{s3_key}")
        
        return uploaded_files
    
    except Exception as e:
        logger.error(f"Error uploading to S3: {str(e)}")
        return []

def update_metadata_file(bucket_name: str, prefix: str, uploaded_files: List[Dict[str, str]]) -> bool:
    """
    Update the metadata file in S3
    """
    try:
        # Create metadata
        metadata = {
            'last_updated': datetime.now().isoformat(),
            'file_count': len(uploaded_files),
            'files': uploaded_files
        }
        
        # Convert to JSON
        metadata_json = json.dumps(metadata, indent=2)
        
        # Upload to S3
        s3.put_object(
            Bucket=bucket_name,
            Key=f"{prefix}/metadata.json",
            Body=metadata_json,
            ContentType='application/json'
        )
        
        logger.info(f"Updated metadata file at s3://{bucket_name}/{prefix}/metadata.json")
        return True
    
    except Exception as e:
        logger.error(f"Error updating metadata file: {str(e)}")
        return False

def handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Lambda handler function
    """
    try:
        # Get parameters from environment variables or SSM
        bucket_name = os.environ.get('S3_BUCKET_NAME')
        prefix = os.environ.get('S3_PREFIX', 'github-sync')
        github_repo_url = get_parameter('/slack-mcp-bot/GITHUB_REPO_URL')
        github_token = get_parameter('/slack-mcp-bot/GITHUB_TOKEN')
        
        # Create a temporary directory
        with tempfile.TemporaryDirectory() as temp_dir:
            logger.info(f"Created temporary directory: {temp_dir}")
            
            # Clone the repository
            if not clone_repository(github_repo_url, github_token, temp_dir):
                return {
                    'statusCode': 500,
                    'body': json.dumps({
                        'message': 'Failed to clone repository'
                    })
                }
            
            # Upload the directory to S3
            uploaded_files = upload_directory_to_s3(temp_dir, bucket_name, prefix)
            
            if not uploaded_files:
                return {
                    'statusCode': 500,
                    'body': json.dumps({
                        'message': 'Failed to upload files to S3'
                    })
                }
            
            # Update the metadata file
            update_metadata_file(bucket_name, prefix, uploaded_files)
            
            return {
                'statusCode': 200,
                'body': json.dumps({
                    'message': f'Successfully synced {len(uploaded_files)} files to S3',
                    'file_count': len(uploaded_files)
                })
            }
    
    except Exception as e:
        logger.error(f"Error in Lambda handler: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({
                'message': f'Error: {str(e)}'
            })
        }