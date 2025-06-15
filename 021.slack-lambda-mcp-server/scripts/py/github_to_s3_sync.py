import os
import json
import boto3
import tempfile
import shutil
import logging
import requests
import zipfile
import re
from datetime import datetime

# ロギングの設定
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# 環境変数
S3_BUCKET_NAME = os.environ.get('S3_BUCKET_NAME')
S3_PREFIX = os.environ.get('S3_PREFIX', 'docs/')
GITHUB_REPO_URL_PARAM = os.environ.get('GITHUB_REPO_URL_PARAM', '/github/repo-url')
GITHUB_USERNAME_PARAM = os.environ.get('GITHUB_USERNAME_PARAM', '/github/username')
GITHUB_TOKEN_PARAM = os.environ.get('GITHUB_TOKEN_PARAM', '/github/token')

# AWS クライアント
ssm_client = boto3.client('ssm')
s3_client = boto3.client('s3')
bedrock_client = boto3.client('bedrock')

def get_parameter(param_name):
    """SSM パラメータストアから値を取得"""
    try:
        response = ssm_client.get_parameter(
            Name=param_name,
            WithDecryption=True
        )
        return response['Parameter']['Value']
    except Exception as e:
        logger.error(f"Error retrieving parameter {param_name}: {str(e)}")
        raise

def clone_github_repo(repo_url, username, token, temp_dir):
    """GitHub リポジトリをクローン (Python実装)"""
    try:
        # リポジトリURLからオーナーとリポジトリ名を抽出
        match = re.match(r'https://github\.com/([^/]+)/([^/]+)(\.git)?/?$', repo_url)
        if not match:
            logger.error(f"Invalid GitHub repository URL: {repo_url}")
            return False
            
        owner, repo = match.groups()[0:2]
        if repo.endswith('.git'):
            repo = repo[:-4]
        
        # GitHub APIを使用してZIPファイルをダウンロード
        zip_url = f"https://api.github.com/repos/{owner}/{repo}/zipball/main"
        headers = {
            "Authorization": f"token {token}",
            "Accept": "application/vnd.github.v3+json"
        }
        
        logger.info(f"Downloading repository: {owner}/{repo}")
        
        # 一時ファイルにZIPをダウンロード
        with tempfile.NamedTemporaryFile(suffix='.zip', delete=False) as temp_file:
            zip_path = temp_file.name
            
            response = requests.get(zip_url, headers=headers, stream=True)
            if response.status_code != 200:
                logger.error(f"Failed to download repository: HTTP {response.status_code}")
                logger.error(f"Response: {response.text}")
                return False
                
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    temp_file.write(chunk)
        
        # ZIPファイルを展開
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            # ZIPファイルの最初のディレクトリ名を取得（通常は {owner}-{repo}-{commit}）
            root_dir = zip_ref.namelist()[0].split('/')[0]
            zip_ref.extractall(os.path.dirname(temp_dir))
            
            # 展開されたディレクトリを指定のディレクトリにリネーム
            extracted_path = os.path.join(os.path.dirname(temp_dir), root_dir)
            if os.path.exists(temp_dir):
                shutil.rmtree(temp_dir)
            shutil.move(extracted_path, temp_dir)
        
        # 一時ZIPファイルを削除
        os.unlink(zip_path)
        
        logger.info(f"Successfully cloned repository: {repo_url}")
        return True
        
    except Exception as e:
        logger.error(f"Error cloning repository: {str(e)}")
        return False

def upload_to_s3(local_dir, bucket, prefix):
    """ディレクトリ内のファイルを S3 にアップロード"""
    try:
        file_count = 0
        
        # ディレクトリを再帰的に走査
        for root, dirs, files in os.walk(local_dir):
            for file in files:
                # 隠しファイルとバイナリファイルをスキップ
                if file.startswith('.') or is_binary_file(os.path.join(root, file)):
                    continue
                
                # ローカルファイルパスと S3 キーを取得
                local_path = os.path.join(root, file)
                relative_path = os.path.relpath(local_path, local_dir)
                s3_key = os.path.join(prefix, relative_path)
                
                # S3 にアップロード
                s3_client.upload_file(local_path, bucket, s3_key)
                file_count += 1
                
                logger.debug(f"Uploaded {local_path} to s3://{bucket}/{s3_key}")
        
        logger.info(f"Successfully uploaded {file_count} files to S3")
        return file_count
    except Exception as e:
        logger.error(f"Error uploading files to S3: {str(e)}")
        raise

def is_binary_file(file_path):
    """ファイルがバイナリかどうかを判定"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            f.read(1024)
            return False
    except UnicodeDecodeError:
        return True

def start_bedrock_ingestion(knowledge_base_id):
    """Bedrock ナレッジベースの取り込みジョブを開始"""
    try:
        response = bedrock_client.start_ingestion_job(
            knowledgeBaseId=knowledge_base_id,
            dataSourceId='s3-data-source'
        )
        logger.info(f"Started Bedrock ingestion job: {response['ingestionJobId']}")
        return response['ingestionJobId']
    except Exception as e:
        logger.error(f"Error starting Bedrock ingestion job: {str(e)}")
        return None

def lambda_handler(event, context):
    """Lambda ハンドラー関数"""
    try:
        # パラメータを取得
        repo_url = get_parameter(GITHUB_REPO_URL_PARAM)
        username = get_parameter(GITHUB_USERNAME_PARAM)
        token = get_parameter(GITHUB_TOKEN_PARAM)
        
        # 一時ディレクトリを作成
        with tempfile.TemporaryDirectory() as temp_dir:
            logger.info(f"Created temporary directory: {temp_dir}")
            
            # GitHub リポジトリをクローン
            if not clone_github_repo(repo_url, username, token, temp_dir):
                return {
                    'statusCode': 500,
                    'body': json.dumps('Failed to clone GitHub repository')
                }
            
            # S3 にアップロード
            file_count = upload_to_s3(temp_dir, S3_BUCKET_NAME, S3_PREFIX)
            
            # CloudFormation スタックから Knowledge Base ID を取得
            # 注: 実際の環境では、CloudFormation スタックの出力から取得する必要があります
            # ここでは簡略化のためにハードコードしています
            knowledge_base_id = 'YOUR_KNOWLEDGE_BASE_ID'
            
            # Bedrock 取り込みジョブを開始
            ingestion_job_id = start_bedrock_ingestion(knowledge_base_id)
            
            return {
                'statusCode': 200,
                'body': json.dumps({
                    'message': f'Successfully synced {file_count} files from GitHub to S3',
                    'ingestionJobId': ingestion_job_id
                })
            }
    
    except Exception as e:
        logger.error(f"Error in lambda_handler: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps(f'Error: {str(e)}')
        }