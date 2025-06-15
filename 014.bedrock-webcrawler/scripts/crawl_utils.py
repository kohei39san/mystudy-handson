import boto3
import json

bedrock = boto3.client('bedrock')

def start_subsequent_crawl(data_source_id):
    """
    BedrockデータソースのSubsequent Crawlを開始
    """
    try:
        response = bedrock.start_data_source_subsequent_crawl(
            dataSourceId=data_source_id
        )
        return response['subsequentCrawlId']
    except Exception as e:
        print(f"Failed to start subsequent crawl: {str(e)}")
        raise

def check_crawl_status(crawl_id):
    """
    クロール状態を確認
    """
    try:
        response = bedrock.get_data_source_subsequent_crawl(
            subsequentCrawlId=crawl_id
        )
        return response['status']
    except Exception as e:
        print(f"Failed to check crawl status: {str(e)}")
        raise