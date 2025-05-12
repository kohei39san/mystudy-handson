#!/usr/bin/env python3
"""
ローカルでBedrockウェブクローラーをテストするためのスクリプト
"""

import argparse
import boto3
import json
import time
import os
from botocore.exceptions import ClientError

def setup_argparse():
    """コマンドライン引数の設定"""
    parser = argparse.ArgumentParser(description='Bedrock Web Crawler Local Test')
    parser.add_argument('--region', type=str, default='ap-northeast-1', help='AWS region')
    parser.add_argument('--profile', type=str, help='AWS profile name')
    parser.add_argument('--data-source-id', type=str, required=True, help='Bedrock data source ID')
    parser.add_argument('--wait', action='store_true', help='Wait for crawl completion')
    parser.add_argument('--timeout', type=int, default=300, help='Timeout in seconds when waiting for completion')
    return parser

def get_boto3_client(service, region, profile=None):
    """Boto3クライアントの取得"""
    session = boto3.Session(profile_name=profile) if profile else boto3.Session()
    return session.client(service, region_name=region)

def start_subsequent_crawl(bedrock_client, data_source_id):
    """BedrockデータソースのSubsequent Crawlを開始"""
    try:
        response = bedrock_client.start_data_source_subsequent_crawl(
            dataSourceId=data_source_id
        )
        return response['subsequentCrawlId']
    except ClientError as e:
        print(f"Error starting subsequent crawl: {e}")
        raise

def check_crawl_status(bedrock_client, crawl_id):
    """クロール状態を確認"""
    try:
        response = bedrock_client.get_data_source_subsequent_crawl(
            subsequentCrawlId=crawl_id
        )
        return response['status']
    except ClientError as e:
        print(f"Error checking crawl status: {e}")
        raise

def wait_for_crawl_completion(bedrock_client, crawl_id, timeout=300):
    """クロールの完了を待機"""
    start_time = time.time()
    interval = 10  # 10秒ごとにステータスチェック
    
    while (time.time() - start_time) < timeout:
        status = check_crawl_status(bedrock_client, crawl_id)
        print(f"Crawl status: {status}")
        
        if status == 'COMPLETED':
            print(f"Crawl completed successfully in {int(time.time() - start_time)} seconds")
            return True
        elif status in ['FAILED', 'CANCELLED']:
            print(f"Crawl failed with status: {status}")
            return False
        
        time.sleep(interval)
    
    print(f"Timeout after {timeout} seconds. Crawl is still in progress.")
    return False

def main():
    """メイン関数"""
    parser = setup_argparse()
    args = parser.parse_args()
    
    # Bedrockクライアントの初期化
    bedrock_client = get_boto3_client('bedrock', args.region, args.profile)
    
    try:
        # クロールの開始
        print(f"Starting subsequent crawl for data source: {args.data_source_id}")
        crawl_id = start_subsequent_crawl(bedrock_client, args.data_source_id)
        print(f"Subsequent crawl started with ID: {crawl_id}")
        
        # 完了を待つかどうか
        if args.wait:
            wait_for_crawl_completion(bedrock_client, crawl_id, args.timeout)
        else:
            print("Not waiting for completion. Exiting.")
    
    except Exception as e:
        print(f"Error: {str(e)}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())