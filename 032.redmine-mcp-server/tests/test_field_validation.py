#!/usr/bin/env python3
"""
フィールドバリデーション機能テスト
"""

import os
import sys
from dotenv import load_dotenv

# プロジェクトルートをパスに追加
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from redmine_selenium import RedmineSeleniumScraper

def test_field_validation():
    """フィールドバリデーション機能テスト"""
    load_dotenv()
    
    scraper = RedmineSeleniumScraper()
    
    try:
        # ログイン（ブラウザで手動入力）
        print("=== ログインテスト ===")
        print("ブラウザが開きます。手動でログインしてください。")
        print("ログイン完了後、このスクリプトが自動的に続行されます。")
        
        login_result = scraper.login("", "")
        print(f"ログイン結果: {login_result}")
        
        if not login_result.get('success'):
            print("ログインに失敗しました")
            return
        
        # プロジェクトとトラッカー設定
        project_id = "hoge-project"
        tracker_id = 1  # 課題
        
        print(f"\n=== フィールドバリデーションテスト ===")
        print(f"プロジェクト: {project_id}")
        print(f"トラッカー: {tracker_id}")
        
        # 有効なフィールドでチケット作成テスト
        print("\n--- 有効なフィールドでチケット作成 ---")
        valid_fields = {
            'description': 'フィールドバリデーションテスト用の説明',
            'priority_id': 2,  # 高
            'start_date': '2025-01-30',
            'estimated_hours': '2.5'
        }
        
        create_result = scraper.create_issue(
            project_id=project_id,
            tracker_id=tracker_id,
            subject='フィールドバリデーションテスト - 有効フィールド',
            **valid_fields
        )
        
        print(f"作成結果: {create_result}")
        
        # 無効なフィールドでテスト（実際のバリデーションはMCPサーバー側で実行）
        print("\n--- 無効なフィールド例 ---")
        invalid_fields = {
            'invalid_field': 'test',
            'another_invalid': 123
        }
        print(f"無効フィールド例: {invalid_fields}")
        print("注意: 実際のバリデーションはMCPサーバー側で実行されます")
        
        # トラッカー2（タスク）用のフィールドテスト
        print(f"\n--- トラッカー2（タスク）用フィールドテスト ---")
        tracker_2_fields = {
            'description': 'タスク用の説明',
            'start_date': '2025-01-30',
            'done_ratio': 10
        }
        
        create_result_2 = scraper.create_issue(
            project_id=project_id,
            tracker_id=2,  # タスク
            subject='フィールドバリデーションテスト - タスク',
            **tracker_2_fields
        )
        
        print(f"タスク作成結果: {create_result_2}")
        
    except Exception as e:
        print(f"テスト中にエラーが発生しました: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        scraper.logout()

if __name__ == "__main__":
    test_field_validation()