#!/usr/bin/env python3
"""
Test script for enhanced get_tracker_fields functionality
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from redmine_selenium import RedmineSeleniumScraper

def test_tracker_fields():
    """Test enhanced get_tracker_fields functionality"""
    
    # Get credentials from environment
    username = os.getenv('REDMINE_USERNAME')
    password = os.getenv('REDMINE_PASSWORD')
    
    if not username or not password:
        print("Error: REDMINE_USERNAME and REDMINE_PASSWORD must be set in .env file")
        return
    
    print(f"Using credentials: {username}/{password}")
    
    scraper = RedmineSeleniumScraper()
    
    try:
        # Login
        print("=== ログイン ===")
        login_result = scraper.login(username, password)
        if not login_result['success']:
            print(f"Login failed: {login_result['message']}")
            return
        
        # Test with default tracker
        project_id = 'hoge-project'
        print(f"\n=== プロジェクト {project_id} のデフォルトトラッカーフィールド取得 ===")
        
        fields_result = scraper.get_tracker_fields(project_id)
        
        if fields_result['success']:
            print(f"取得成功: {fields_result['message']}")
            print(f"総フィールド数: {len(fields_result['fields'])}")
            print(f"必須フィールド数: {len(fields_result['required_fields'])}")
            print(f"任意フィールド数: {len(fields_result['optional_fields'])}")
            print(f"カスタムフィールド数: {len(fields_result['custom_fields'])}")
            print(f"標準フィールド数: {len(fields_result['standard_fields'])}")
            
            print("\n=== 必須フィールド ===")
            for field in fields_result['required_fields']:
                print(f"  {field['id']}: {field['name']} ({field['type']}) - {field.get('value_type', 'unknown')}")
            
            print("\n=== カスタムフィールド ===")
            for field in fields_result['custom_fields']:
                print(f"  {field['id']}: {field['name']} ({field['type']}) - {field.get('value_type', 'unknown')}")
                if field.get('options'):
                    options_list = [opt['text'] for opt in field['options'][:3]]
                    print(f"    Options: {options_list}")
            
            print("\n=== 全フィールド詳細 (最初の10個) ===")
            for i, field in enumerate(fields_result['fields'][:10]):
                print(f"  [{i+1}] ID: {field['id']}")
                print(f"      Name: {field['name']}")
                print(f"      Type: {field['type']}")
                print(f"      Value Type: {field.get('value_type', 'unknown')}")
                print(f"      Required: {field['required']}")
                print(f"      Custom: {field.get('custom', False)}")
                print(f"      Visible: {field['visible']}")
                print(f"      Enabled: {field['enabled']}")
                if field.get('options'):
                    print(f"      Options: {len(field['options'])} available")
                print()
        else:
            print(f"取得失敗: {fields_result['message']}")
        
        # Test with specific tracker (課題 = tracker ID 1)
        print(f"\n=== プロジェクト {project_id} のトラッカー1(課題)フィールド取得 ===")
        
        fields_result = scraper.get_tracker_fields(project_id, tracker_id="1")
        
        if fields_result['success']:
            print(f"取得成功: {fields_result['message']}")
            print(f"総フィールド数: {len(fields_result['fields'])}")
            print(f"カスタムフィールド数: {len(fields_result['custom_fields'])}")
            
            print("\n=== カスタムフィールド詳細 ===")
            for field in fields_result['custom_fields']:
                print(f"  {field['id']}: {field['name']}")
                print(f"    Type: {field['type']} ({field.get('value_type', 'unknown')})")
                print(f"    Required: {field['required']}")
                if field.get('options'):
                    options_str = [f"{opt['value']}:{opt['text']}" for opt in field['options'][:5]]
                    print(f"    Options: {options_str}")
                print()
        else:
            print(f"取得失敗: {fields_result['message']}")
        
    finally:
        # Logout
        print("\n=== ログアウト ===")
        logout_result = scraper.logout()
        print(f"Logout result: {logout_result}")

if __name__ == "__main__":
    test_tracker_fields()