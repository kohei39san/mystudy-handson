import json
import os
import boto3
import requests
import logging
import feedparser
from datetime import datetime, timedelta
import re

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Constants
OPENROUTER_API_URL = "https://openrouter.ai/api/v1/chat/completions"

def lambda_handler(event, context):
    """
    Lambda function handler to fetch RSS feed, summarize it using OpenRouter, and send to Slack.
    """
    try:
        # Get parameters from SSM Parameter Store
        ssm_client = boto3.client('ssm')
        
        openrouter_api_key_param = os.environ.get('OPENROUTER_API_KEY_PARAM', '/rss-summary/openrouter-api-key')
        slack_webhook_url_param = os.environ.get('SLACK_WEBHOOK_URL_PARAM', '/rss-summary/slack-webhook-url')
        rss_feed_url = os.environ.get('RSS_FEED_URL', 'https://aws.amazon.com/about-aws/whats-new/recent/feed/')
        summary_prompt = os.environ.get('SUMMARY_PROMPT', 'AWSの新機能の追加を優先事項として、サービスごとに分類して要約してください。要約は1000文字以内にしてください。')
        
        openrouter_api_key = ssm_client.get_parameter(
            Name=openrouter_api_key_param,
            WithDecryption=True
        )['Parameter']['Value']
        
        slack_webhook_url = ssm_client.get_parameter(
            Name=slack_webhook_url_param,
            WithDecryption=True
        )['Parameter']['Value']
        
        # Fetch and parse RSS feed
        logger.info(f"Fetching RSS feed from {rss_feed_url}")
        rss_content = fetch_rss_feed(rss_feed_url)
        
        # Generate summary using OpenRouter
        logger.info("Generating summary using OpenRouter")
        summary = generate_summary(rss_content, summary_prompt, openrouter_api_key)
        
        # Send summary to Slack
        logger.info("Sending summary to Slack")
        send_to_slack(slack_webhook_url, summary, rss_feed_url)
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'Successfully sent RSS summary to Slack',
                'rss_feed': rss_feed_url
            })
        }
    
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({
                'message': f'Error: {str(e)}'
            })
        }

def fetch_rss_feed(url):
    """
    Fetch and parse RSS feed from the given URL.
    
    Args:
        url (str): URL of the RSS feed
    
    Returns:
        str: Formatted content of the RSS feed
    """
    try:
        feed = feedparser.parse(url)
        
        # Check if feed was parsed successfully
        if not feed or not feed.entries:
            logger.warning(f"No entries found in RSS feed: {url}")
            return "No entries found in RSS feed."
        
        # Format the feed content
        content = f"RSS Feed Title: {feed.feed.title}\n\n"
        
        # Get entries from the last 7 days
        cutoff_date = datetime.now() - timedelta(days=7)
        recent_entries = []
        
        for entry in feed.entries:
            # Parse the published date
            if hasattr(entry, 'published_parsed'):
                pub_date = datetime(*entry.published_parsed[:6])
                if pub_date > cutoff_date:
                    recent_entries.append(entry)
            else:
                # If no date available, include it anyway
                recent_entries.append(entry)
        
        # Limit to most recent 20 entries to avoid token limits
        recent_entries = recent_entries[:20]
        
        for i, entry in enumerate(recent_entries):
            content += f"Entry {i+1}:\n"
            content += f"Title: {entry.title}\n"
            
            if hasattr(entry, 'published'):
                content += f"Published: {entry.published}\n"
            
            if hasattr(entry, 'summary'):
                # Clean HTML tags from summary
                summary = re.sub(r'<[^>]+>', '', entry.summary)
                content += f"Summary: {summary}\n"
            
            if hasattr(entry, 'link'):
                content += f"Link: {entry.link}\n"
            
            content += "\n"
        
        return content
    
    except Exception as e:
        logger.error(f"Error fetching RSS feed: {str(e)}")
        raise

def generate_summary(rss_content, prompt, api_key):
    """
    Generate a summary of the RSS feed content using OpenRouter.
    
    Args:
        rss_content (str): Content of the RSS feed
        prompt (str): Prompt to use for summarization
        api_key (str): OpenRouter API key
    
    Returns:
        str: Generated summary
    """
    try:
        # Add optional headers for OpenRouter API
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        # Create prompt for the AI
        full_prompt = f"""
        以下のRSSフィードの内容を要約してください。

        {prompt}

        RSS内容:
        {rss_content}
        """
        
        payload = {
            "model": "anthropic/claude-3-haiku-20240307:free",
            "messages": [
                {"role": "user", "content": full_prompt}
            ],
            "temperature": 0.3,
            "max_tokens": 1500
        }
        
        response = requests.post(url=OPENROUTER_API_URL, headers=headers, json=payload)
        response.raise_for_status()
        
        # Extract summary from the response
        ai_response = response.json()
        summary = ai_response["choices"][0]["message"]["content"]
        
        return summary
    
    except Exception as e:
        logger.error(f"Error generating summary: {str(e)}")
        raise

def send_to_slack(webhook_url, summary, rss_url):
    """
    Send the summary to Slack via webhook.
    
    Args:
        webhook_url (str): Slack webhook URL
        summary (str): Generated summary
        rss_url (str): URL of the RSS feed
    """
    try:
        # Format current date
        current_date = datetime.now().strftime("%Y-%m-%d")
        
        # Create Slack message payload
        payload = {
            "blocks": [
                {
                    "type": "header",
                    "text": {
                        "type": "plain_text",
                        "text": f"RSS Summary - {current_date}",
                        "emoji": True
                    }
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*Source:* <{rss_url}|RSS Feed>"
                    }
                },
                {
                    "type": "divider"
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": summary
                    }
                }
            ]
        }
        
        response = requests.post(webhook_url, json=payload)
        response.raise_for_status()
        
        logger.info("Successfully sent summary to Slack")
    
    except Exception as e:
        logger.error(f"Error sending to Slack: {str(e)}")
        raise

if __name__ == "__main__":
    # For local testing
    lambda_handler(None, None)