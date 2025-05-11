import json
import os
import boto3
import requests
import logging
from datetime import datetime, timedelta
import re

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Constants
OPENROUTER_API_URL = "https://openrouter.ai/api/v1/chat/completions"
STAR_RAIL_REFERENCE = "https://gamewith.jp/houkaistarrail/article/show/396232"
GENSHIN_REFERENCE = "https://gamewith.jp/genshin/article/show/231856"

def lambda_handler(event, context):
    """
    Lambda function handler to fetch game codes and send them to Discord.
    """
    try:
        # Get parameters from SSM Parameter Store
        ssm_client = boto3.client('ssm')
        
        openrouter_api_key_param = os.environ.get('OPENROUTER_API_KEY_PARAM', '/game-info/openrouter-api-key')
        discord_webhook_url_param = os.environ.get('DISCORD_WEBHOOK_URL_PARAM', '/game-info/discord-webhook-url')
        
        openrouter_api_key = ssm_client.get_parameter(
            Name=openrouter_api_key_param,
            WithDecryption=True
        )['Parameter']['Value']
        
        discord_webhook_url = ssm_client.get_parameter(
            Name=discord_webhook_url_param,
            WithDecryption=True
        )['Parameter']['Value']
        
        # Fetch game codes
        star_rail_codes = get_game_codes("崩壊スターレイル", STAR_RAIL_REFERENCE, openrouter_api_key)
        genshin_codes = get_game_codes("原神インパクト", GENSHIN_REFERENCE, openrouter_api_key)
        
        # Filter codes expiring within 2 weeks
        star_rail_codes = filter_expiring_codes(star_rail_codes)
        genshin_codes = filter_expiring_codes(genshin_codes)
        
        # Send to Discord
        send_to_discord(discord_webhook_url, star_rail_codes, genshin_codes)
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'Successfully sent game codes to Discord',
                'star_rail_codes_count': len(star_rail_codes),
                'genshin_codes_count': len(genshin_codes)
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

def get_game_codes(game_name, reference_url, api_key):
    """
    Use OpenRouter API to extract game codes from the reference URL.
    
    Args:
        game_name (str): Name of the game
        reference_url (str): URL to extract codes from
        api_key (str): OpenRouter API key
    
    Returns:
        list: List of dictionaries containing code information
    """
    logger.info(f"Fetching codes for {game_name}")
    
    # Add optional headers for OpenRouter API
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    reference_text=requests.get(reference_url).text
    # Create prompt for the AI
    prompt = f"""
    あなたはゲームのリワードコードを抽出するアシスタントです。
    以下のURL（{reference_url}）から{game_name}の最新のリワードコードを抽出してください。
    
    各コードについて以下の情報を抽出してください：
    1. コード文字列
    2. 報酬内容
    3. 有効期限
    
    結果はJSON形式で返してください。例：
    [
      {{
        "code": "ABCD1234",
        "rewards": "原石×100",
        "expiry_date": "2023-12-31"
      }}
    ]
    
    有効期限が不明な場合は "unknown" と記入してください。
    URL（{reference_url}）の内容は以下の通り: {reference_text}
    """
    
    payload = {
        "model": "deepseek/deepseek-chat-v3-0324:free",
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.1
    }
    
    try:
        response = requests.post(url=OPENROUTER_API_URL, headers=headers, json=payload)
        response.raise_for_status()
        
        # Extract JSON from the response
        ai_response = response.json()
        content = ai_response["choices"][0]["message"]["content"]
        
        # Extract JSON from the content (AI might wrap it in markdown code blocks)
        json_match = re.search(r'```(?:json)?\s*([\s\S]*?)\s*```|(\[[\s\S]*?\])', content)
        if json_match:
            json_str = json_match.group(1) or json_match.group(2)
            codes = json.loads(json_str)
        else:
            # Try to find JSON array directly
            json_match = re.search(r'\[\s*{.*}\s*\]', content, re.DOTALL)
            if json_match:
                codes = json.loads(json_match.group(0))
            else:
                logger.warning(f"Could not extract JSON from AI response for {game_name}")
                codes = []
        
        # Add game name to each code
        for code in codes:
            code["game"] = game_name
            
            # Standardize date format if it's not "unknown"
            if code.get("expiry_date") and code["expiry_date"].lower() != "unknown":
                try:
                    # Try to parse the date in various formats
                    for fmt in ["%Y-%m-%d", "%Y/%m/%d", "%Y年%m月%d日", "%Y-%m-%d %H:%M", "%Y/%m/%d %H:%M", "%Y年%m月%d日 %H:%M"]:
                        try:
                            date_obj = datetime.strptime(code["expiry_date"], fmt)
                            code["expiry_date"] = date_obj.strftime("%Y-%m-%d")
                            break
                        except ValueError:
                            continue
                except Exception:
                    # If parsing fails, keep the original string
                    pass
        
        return codes
    
    except Exception as e:
        logger.error(f"Error fetching codes for {game_name}: {str(e)}")
        return []

def filter_expiring_codes(codes):
    """
    Filter codes to only include those expiring within 2 weeks.
    
    Args:
        codes (list): List of code dictionaries
    
    Returns:
        list: Filtered list of code dictionaries
    """
    today = datetime.now()
    two_weeks_later = today + timedelta(days=14)
    
    filtered_codes = []
    for code in codes:
        # Exclude codes with unknown expiry date
        if code.get("expiry_date", "9999-12-31").lower() == "unknown":
            continue

        try:
            expiry_date = datetime.strptime(code.get("expiry_date", "9999-12-31"), "%Y-%m-%d")
            # Include codes that expire within 2 weeks
            if today <= expiry_date <= two_weeks_later:
                filtered_codes.append(code)
        except ValueError as e:
            # If date parsing fails, include the code anyway
            #filtered_codes.append(code)
            logger.error(f"Error: {str(e)}")
    
    return filtered_codes

def send_to_discord(webhook_url, star_rail_codes, genshin_codes):
    """
    Send game codes to Discord via webhook.
    
    Args:
        webhook_url (str): Discord webhook URL
        star_rail_codes (list): List of Star Rail code dictionaries
        genshin_codes (list): List of Genshin Impact code dictionaries
    """
    logger.info("Sending codes to Discord")
    
    # Create embeds for Star Rail codes
    star_rail_embeds = []
    if star_rail_codes:
        for code in star_rail_codes:
            # Create auto-input link for Star Rail
            auto_input_url = f"https://hsr.hoyoverse.com/gift?code={code['code']}"
            
            embed = {
                "title": f"崩壊スターレイル: {code['code']}",
                "color": 0x9370DB,  # Purple color
                "fields": [
                    {
                        "name": "コード",
                        "value": f"`{code['code']}`",
                        "inline": True
                    },
                    {
                        "name": "報酬",
                        "value": code.get('rewards', '不明'),
                        "inline": True
                    },
                    {
                        "name": "有効期限",
                        "value": code.get('expiry_date', '不明'),
                        "inline": True
                    },
                    {
                        "name": "自動入力リンク",
                        "value": f"[ここをクリック]({auto_input_url})",
                        "inline": False
                    }
                ]
            }
            star_rail_embeds.append(embed)
    
    # Create embeds for Genshin codes
    genshin_embeds = []
    if genshin_codes:
        for code in genshin_codes:
            # Create auto-input link for Genshin
            auto_input_url = f"https://genshin.hoyoverse.com/en/gift?code={code['code']}"
            
            embed = {
                "title": f"原神インパクト: {code['code']}",
                "color": 0x00BFFF,  # Blue color
                "fields": [
                    {
                        "name": "コード",
                        "value": f"`{code['code']}`",
                        "inline": True
                    },
                    {
                        "name": "報酬",
                        "value": code.get('rewards', '不明'),
                        "inline": True
                    },
                    {
                        "name": "有効期限",
                        "value": code.get('expiry_date', '不明'),
                        "inline": True
                    },
                    {
                        "name": "自動入力リンク",
                        "value": f"[ここをクリック]({auto_input_url})",
                        "inline": False
                    }
                ]
            }
            genshin_embeds.append(embed)
    
    # Combine all embeds
    all_embeds = []
    
    # Add header embed if there are any codes
    if star_rail_codes or genshin_codes:
        header_embed = {
            "title": "期限間近のゲームコード",
            "description": "以下のコードは2週間以内に期限切れになります。お早めにご利用ください。",
            "color": 0xFF9900  # Orange color
        }
        all_embeds.append(header_embed)
    
    # Add game-specific embeds
    all_embeds.extend(star_rail_embeds)
    all_embeds.extend(genshin_embeds)
    
    # If no codes found, send a notification
    if not all_embeds:
        all_embeds.append({
            "title": "期限間近のゲームコード",
            "description": "現在、期限間近のコードはありません。",
            "color": 0x808080  # Gray color
        })
    
    # Send to Discord
    payload = {
        "embeds": all_embeds
    }
    
    response = requests.post(webhook_url, json=payload)
    response.raise_for_status()
    
    logger.info(f"Successfully sent {len(star_rail_codes)} Star Rail codes and {len(genshin_codes)} Genshin codes to Discord")

if __name__ == "__main__":
    # For local testing
    lambda_handler(None, None)