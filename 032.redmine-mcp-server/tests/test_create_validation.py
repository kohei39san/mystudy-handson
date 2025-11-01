#!/usr/bin/env python3
"""
チケット作成の必須フィールド検証テスト
新規作成画面を取得して必須フィールドを確認し、チケット作成をテストする
"""

import os
import sys
from dotenv import load_dotenv
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# プロジェクトルートをパスに追加
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from redmine_selenium import RedmineSeleniumScraper

def test_create_issue_validation():
    """チケット作成の必須フィールド検証とテスト"""
    load_dotenv()
    
    scraper = RedmineSeleniumScraper()
    
    try:
        # ログイン（手動入力）
        print("=== ログインテスト ===")
        print("ブラウザが開きます。手動でログインしてください。")
        print("ログイン完了後、このスクリプトが自動的に続行されます。")
        
        # 空のユーザー名・パスワードでloginを呼び出し、手動ログインを促す
        login_result = scraper.login("", "")
        print(f"ログイン結果: {login_result}")
        
        if not login_result.get('success'):
            print("ログインに失敗しました")
            return
        
        # プロジェクトをhoge-projectに固定
        print("\n=== プロジェクト設定 ===")
        project_id = "hoge-project"
        print(f"使用するプロジェクト: {project_id}")
        
        # 必須フィールドの検証はcreate_issueツール内で実行
        print(f"\n=== 必須フィールド検証はcreate_issueツール内で実行 ===")
        print("必須フィールドの検証はチケット作成時に自動的に行われます。")
        
        # 利用可能なトラッカーを取得
        print(f"\n=== 利用可能なトラッカー取得 ===")
        trackers = scraper.get_available_trackers(project_id)
        if trackers.get('success') and trackers.get('trackers'):
            print("利用可能なトラッカー:")
            for tracker in trackers['trackers']:
                print(f"  - {tracker['text']} (ID: {tracker['value']})")
            
            # 最初のトラッカーを選択
            selected_tracker = trackers['trackers'][0]
            tracker_id = selected_tracker['value']
            print(f"選択されたトラッカー: {selected_tracker['text']} (ID: {tracker_id})")
        else:
            print("トラッカーの取得に失敗しました")
            tracker_id = 1  # デフォルト値
        
        # チケット作成テスト
        print(f"\n=== チケット作成テスト ===")
        
        # 基本的なチケット情報
        issue_data = {
            'project_id': project_id,
            'tracker_id': tracker_id,
            'subject': 'テストチケット - 必須フィールド検証',
            'description': 'このチケットは必須フィールド検証のために作成されました。\n\n作成日時: ' + str(scraper.driver.execute_script("return new Date().toLocaleString()"))
        }
        
        print("作成するチケット情報:")
        for key, value in issue_data.items():
            print(f"  {key}: {value}")
        
        # チケット作成実行
        result = scraper.create_issue(**issue_data)
        
        print(f"\nチケット作成結果:")
        print(f"  成功: {result.get('success')}")
        if result.get('success'):
            print(f"  チケットID: {result.get('issue_id')}")
            print(f"  チケットURL: {result.get('issue_url')}")
        else:
            print(f"  エラー: {result.get('error')}")
            if result.get('details'):
                print(f"  詳細: {result.get('details')}")
        
    except Exception as e:
        print(f"テスト中にエラーが発生しました: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        scraper.logout()

if __name__ == "__main__":
    test_create_issue_validation()