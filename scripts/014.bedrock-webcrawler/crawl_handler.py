import json
import os
from crawl_utils import start_subsequent_crawl

def handler(event, context):
    """
    Lambda関数のメインハンドラー
    """
    try:
        data_source_id = os.environ['DATA_SOURCE_ID']
        
        # 同期クロールの開始
        crawl_id = start_subsequent_crawl(data_source_id)
        print(f"Started subsequent crawl: {crawl_id}")
        
        # 同期結果を待たずに終了
        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'Subsequent crawl started successfully',
                'crawlId': crawl_id
            })
        }
    except Exception as e:
        print(f"Error: {str(e)}")
        raise
