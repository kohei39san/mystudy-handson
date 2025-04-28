import json
import os
import time
from crawl_utils import start_subsequent_crawl, check_crawl_status

def handler(event, context):
    """
    Lambda関数のメインハンドラー
    """
    try:
        data_source_id = os.environ['DATA_SOURCE_ID']
        
        # 同期クロールの開始
        crawl_id = start_subsequent_crawl(data_source_id)
        print(f"Started subsequent crawl: {crawl_id}")
        
        # 同期状態の確認（最大4分間）
        max_attempts = 24  # 10秒ごとに24回 = 4分
        attempts = 0
        while attempts < max_attempts:
            status = check_crawl_status(crawl_id)
            print(f"Crawl status: {status}")
            
            if status == 'COMPLETED':
                return {
                    'statusCode': 200,
                    'body': json.dumps({
                        'message': 'Subsequent crawl completed successfully',
                        'crawlId': crawl_id
                    })
                }
            elif status in ['FAILED', 'CANCELLED']:
                raise Exception(f"Subsequent crawl failed with status: {status}")
            
            time.sleep(10)
            attempts += 1
        
        # タイムアウトの場合
        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'Subsequent crawl is still in progress',
                'crawlId': crawl_id
            })
        }
    except Exception as e:
        print(f"Error: {str(e)}")
        raise
