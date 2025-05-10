#!/usr/bin/env python3
"""
Local testing script for the game info Discord notification system.
This script allows testing the Lambda function locally without deploying to AWS.
"""

import argparse
import json
import os
import logging
from lambda_function import get_game_codes, filter_expiring_codes, send_to_discord

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Constants
STAR_RAIL_REFERENCE = "https://gamewith.jp/houkaistarrail/article/show/396232"
GENSHIN_REFERENCE = "https://gamewith.jp/genshin/article/show/231856"

def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='Test game info Discord notification locally')
    
    parser.add_argument('--api-key', required=True, help='OpenRouter API key')
    parser.add_argument('--webhook-url', required=True, help='Discord webhook URL')
    parser.add_argument('--dry-run', action='store_true', help='Run without sending to Discord')
    parser.add_argument('--verbose', action='store_true', help='Enable verbose output')
    
    return parser.parse_args()

return parser.parse_args()

def fetch_game_codes(game_name, reference, api_key):
    """Fetch game codes for a specific game."""
    logger.info(f"Fetching {game_name} codes...")
    return get_game_codes(game_name, reference, api_key)

def process_game_codes(codes, game_name, args):
    """Process and display game codes."""
    filtered_codes = filter_expiring_codes(codes)
    logger.info(f"Found {len(filtered_codes)} {game_name} codes expiring within 2 weeks")
    if args.verbose and filtered_codes:
        print(f"
{game_name} Codes:")
        print(json.dumps(filtered_codes, indent=2, ensure_ascii=False))
    return filtered_codes

def send_codes_to_discord(webhook_url, star_rail_codes, genshin_codes, dry_run):
    """Send codes to Discord if not in dry-run mode."""
    if not dry_run:
        logger.info("Sending codes to Discord...")
        send_to_discord(webhook_url, star_rail_codes, genshin_codes)
        logger.info("Successfully sent codes to Discord")
    else:
        logger.info("Dry run mode - not sending to Discord")

def main():
    """Main function to test the game info notification system."""
    args = parse_arguments()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    try:
        logger.info("Starting local test")
        
        star_rail_codes = fetch_game_codes("崩壊スターレイル", STAR_RAIL_REFERENCE, args.api_key)
        genshin_codes = fetch_game_codes("原神インパクト", GENSHIN_REFERENCE, args.api_key)
        
        logger.info("Filtering codes expiring within 2 weeks...")
        star_rail_codes = process_game_codes(star_rail_codes, "Star Rail", args)
        genshin_codes = process_game_codes(genshin_codes, "Genshin Impact", args)
        
        send_codes_to_discord(args.webhook_url, star_rail_codes, genshin_codes, args.dry_run)
        
        logger.info("Local test completed successfully")
    """Main function to test the game info notification system."""
    args = parse_arguments()
    
    # Set logging level based on verbose flag
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    try:
        logger.info("Starting local test")
        
        # Fetch game codes
        logger.info("Fetching Star Rail codes...")
        star_rail_codes = get_game_codes("崩壊スターレイル", STAR_RAIL_REFERENCE, args.api_key)
        
        logger.info("Fetching Genshin Impact codes...")
        genshin_codes = get_game_codes("原神インパクト", GENSHIN_REFERENCE, args.api_key)
        
        # Filter codes expiring within 2 weeks
        logger.info("Filtering codes expiring within 2 weeks...")
        star_rail_codes = filter_expiring_codes(star_rail_codes)
        genshin_codes = filter_expiring_codes(genshin_codes)
        
        # Print the results
        logger.info(f"Found {len(star_rail_codes)} Star Rail codes expiring within 2 weeks")
        if args.verbose and star_rail_codes:
            print("\nStar Rail Codes:")
            print(json.dumps(star_rail_codes, indent=2, ensure_ascii=False))
        
        logger.info(f"Found {len(genshin_codes)} Genshin Impact codes expiring within 2 weeks")
        if args.verbose and genshin_codes:
            print("\nGenshin Impact Codes:")
            print(json.dumps(genshin_codes, indent=2, ensure_ascii=False))
        
        # Send to Discord if not in dry-run mode
        if not args.dry_run:
            logger.info("Sending codes to Discord...")
            send_to_discord(args.webhook_url, star_rail_codes, genshin_codes)
            logger.info("Successfully sent codes to Discord")
        else:
            logger.info("Dry run mode - not sending to Discord")
        
        logger.info("Local test completed successfully")
    
    except Exception as e:
        logger.error(f"Error during local test: {str(e)}", exc_info=True)
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())