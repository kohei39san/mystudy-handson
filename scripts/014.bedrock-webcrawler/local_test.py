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

def get_knowledge_base_info(kb_id):
    """
    Knowledge Baseの情報を取得
    """
    bedrock = boto3.client('bedrock')
    try:
        response = bedrock.get_knowledge_base(
            knowledgeBaseId=kb_id
        )
        return response
    except ClientError as e:
        print(f"Error getting knowledge base: {e}")
        raise

def get_data_source_info(ds_id):
    """
    Data Sourceの情報を取得
    """
    bedrock = boto3.client('bedrock')
    try:
        response = bedrock.get_data_source(
            dataSourceId=ds_id
        )
        return response
    except ClientError as e:
        print(f"Error getting data source: {e}")
        raise

def start_crawl(ds_id):
    """
    クロールを開始
    """
    bedrock = boto3.client('bedrock')
    try:
        response = bedrock.start_data_source_subsequent_crawl(
            dataSourceId=ds_id
        )
        return response['subsequentCrawlId']
    except ClientError as e:
        print(f"Error starting crawl: {e}")
        raise

def check_crawl_status(crawl_id):
    """
    クロール状態を確認
    """
    bedrock = boto3.client('bedrock')
    try:
        response = bedrock.get_data_source_subsequent_crawl(
            subsequentCrawlId=crawl_id
        )
        return response
    except ClientError as e:
        print(f"Error checking crawl status: {e}")
        raise

def wait_for_crawl_completion(crawl_id, timeout_seconds=300, check_interval=10):
    """
    クロールの完了を待機
    """
    start_time = time.time()
    while time.time() - start_time < timeout_seconds:
        status_response = check_crawl_status(crawl_id)
        status = status_response['status']
        print(f"Crawl status: {status}")
        
        if status == 'COMPLETED':
            print("Crawl completed successfully!")
            return True
        elif status in ['FAILED', 'CANCELLED']:
            print(f"Crawl failed with status: {status}")
            if 'failureReasons' in status_response:
                print(f"Failure reasons: {status_response['failureReasons']}")
            return False
        
        print(f"Waiting {check_interval} seconds...")
        time.sleep(check_interval)
    
    print(f"Timeout after {timeout_seconds} seconds. Crawl is still in progress.")
    return False

def main():
    parser = argparse.ArgumentParser(description='Test Bedrock Web Crawler locally')
    parser.add_argument('--data-source-id', required=True, help='Bedrock Data Source ID')
    parser.add_argument('--wait', action='store_true', help='Wait for crawl completion')
    parser.add_argument('--timeout', type=int, default=300, help='Timeout in seconds for crawl completion')
    
    args = parser.parse_args()
    
    # Data Source情報の取得
    print(f"Getting information for Data Source: {args.data_source_id}")
    ds_info = get_data_source_info(args.data_source_id)
    print(f"Data Source Name: {ds_info['name']}")
    print(f"Knowledge Base ID: {ds_info['knowledgeBaseId']}")
    
    # Knowledge Base情報の取得
    kb_id = ds_info['knowledgeBaseId']
    print(f"\nGetting information for Knowledge Base: {kb_id}")
    kb_info = get_knowledge_base_info(kb_id)
    print(f"Knowledge Base Name: {kb_info['name']}")
    print(f"Storage Type: {kb_info['storageConfiguration']['type']}")
    
    # クロールの開始
    print("\nStarting subsequent crawl...")
    crawl_id = start_crawl(args.data_source_id)
    print(f"Crawl started with ID: {crawl_id}")
    
    # クロール完了を待機する場合
    if args.wait:
        print(f"\nWaiting for crawl completion (timeout: {args.timeout} seconds)...")
        wait_for_crawl_completion(crawl_id, timeout_seconds=args.timeout)
    else:
        print("\nCrawl is running in the background. Use the following command to check status:")
        print(f"aws bedrock get-data-source-subsequent-crawl --subsequent-crawl-id {crawl_id}")

if __name__ == "__main__":
    main()