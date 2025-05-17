#!/usr/bin/env python3
"""
Local testing script for the RSS summary to Slack system.
This script allows testing the Lambda function locally without deploying to AWS.
"""

import argparse
import json
import os
import logging
from lambda_function import fetch_rss_feed, generate_summary, send_to_slack

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='Test RSS summary to Slack notification locally')
    
    parser.add_argument('--api-key', required=True, help='OpenRouter API key')
    parser.add_argument('--webhook-url', required=True, help='Slack webhook URL')
    parser.add_argument('--rss-url', default='https://aws.amazon.com/about-aws/whats-new/recent/feed/', 
                        help='RSS feed URL')
    parser.add_argument('--prompt', default='AWSの新機能の追加を優先事項として、AWSサービス名ごとに分類して要約してください。要約は1000文字以内にしてください。過去7日分の情報としてください。AWSサービス名は「# *任意のAWSサービス名* 」とすること。リンクURLは<任意のURL|「表示するテキスト」>とすること。リストは「•」を行頭につけること。', 
                        help='Summary prompt')
    parser.add_argument('--dry-run', action='store_true', help='Run without sending to Slack')
    parser.add_argument('--verbose', action='store_true', help='Enable verbose output')
    
    return parser.parse_args()

def main():
    """Main function to test the RSS summary notification system."""
    args = parse_arguments()
    
    # Set logging level based on verbose flag
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    try:
        logger.info("Starting local test")
        
        # Fetch RSS feed
        logger.info(f"Fetching RSS feed from {args.rss_url}...")
        rss_content = fetch_rss_feed(args.rss_url)
        
        if args.verbose:
            print("\nRSS Content (first 500 chars):")
            print(rss_content[:500] + "...\n")
        
        # Generate summary
        logger.info("Generating summary using OpenRouter...")
        summary = generate_summary(rss_content, args.prompt, args.api_key)
        
        print("\nGenerated Summary:")
        print("=" * 80)
        print(summary)
        print("=" * 80)
        
        # Send to Slack if not in dry-run mode
        if not args.dry_run:
            logger.info("Sending summary to Slack...")
            send_to_slack(args.webhook_url, summary, args.rss_url)
            logger.info("Successfully sent summary to Slack")
        else:
            logger.info("Dry run mode - not sending to Slack")
        
        logger.info("Local test completed successfully")
    
    except Exception as e:
        logger.error(f"Error during local test: {str(e)}", exc_info=True)
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())