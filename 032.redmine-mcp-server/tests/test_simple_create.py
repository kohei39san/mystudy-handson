#!/usr/bin/env python3
"""
シンプルなチケット作成テスト（バリデーションをスキップ）
"""

import os
import sys
import logging
from dotenv import load_dotenv

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from redmine_selenium import RedmineSeleniumScraper

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def test_simple_create():
    """シンプルなチケット作成テスト"""
    
    username = os.getenv('REDMINE_USERNAME', 'admin')
    password = os.getenv('REDMINE_PASSWORD', 'admin')
    
    print(f"認証情報: {username}/{password}")
    
    scraper = RedmineSeleniumScraper()
    
    try:
        # ログイン
        print("=== ログイン ===")
        login_result = scraper.login(username, password)
        if not login_result.get('success'):
            print("ログインに失敗しました")
            return
        print("ログイン成功")
        
        project_id = "hoge-project"
        
        # プロジェクトメンバーを取得
        print(f"\n=== プロジェクト {project_id} のメンバー取得 ===")
        members_result = scraper.get_project_members(project_id)
        if members_result.get('success'):
            members = members_result.get('members', [])
            print(f"利用可能なメンバー:")
            for member in members:
                print(f"  - {member.get('name')} (ID: {member.get('id')})")
            
            if not members:
                print("メンバーが見つかりません")
                return
                
            # 最初のメンバーを担当者として使用
            assignee = members[0]
            assignee_id = assignee.get('id')
            assignee_name = assignee.get('name')
            
        else:
            print("メンバー取得に失敗しました")
            return
        
        # バリデーションをスキップして直接チケット作成
        print(f"\n=== 直接チケット作成（バリデーションスキップ） ===")
        
        # 新規チケット作成ページに移動
        from selenium.webdriver.common.by import By
        from selenium.webdriver.support.ui import Select
        import time
        import re
        
        new_issue_url = f"http://168.138.42.184/projects/{project_id}/issues/new"
        scraper.driver.get(new_issue_url)
        time.sleep(2)
        
        # トラッカーを設定
        try:
            tracker_select = scraper.driver.find_element(By.ID, "issue_tracker_id")
            select = Select(tracker_select)
            select.select_by_value("1")
            print("トラッカー設定成功")
        except Exception as e:
            print(f"トラッカー設定失敗: {e}")
        
        # 件名を設定
        try:
            subject_field = scraper.driver.find_element(By.ID, "issue_subject")
            subject_field.clear()
            subject_field.send_keys(f"担当者テスト - {assignee_name}")
            print("件名設定成功")
        except Exception as e:
            print(f"件名設定失敗: {e}")
            return
        
        # 説明を設定
        try:
            desc_field = scraper.driver.find_element(By.ID, "issue_description")
            desc_field.clear()
            desc_field.send_keys("担当者が正しく設定されているかのテスト")
            print("説明設定成功")
        except Exception as e:
            print(f"説明設定失敗: {e}")
        
        # 担当者を設定
        try:
            assignee_select = scraper.driver.find_element(By.ID, "issue_assigned_to_id")
            select = Select(assignee_select)
            select.select_by_value(str(assignee_id))
            print(f"担当者設定成功: {assignee_name} (ID: {assignee_id})")
        except Exception as e:
            print(f"担当者設定失敗: {e}")
        
        # フォームを送信
        try:
            submit_button = scraper.driver.find_element(By.CSS_SELECTOR, "input[type='submit'][name='commit']")
            submit_button.click()
            print("フォーム送信成功")
            
            time.sleep(3)
            
            current_url = scraper.driver.current_url
            print(f"送信後のURL: {current_url}")
            
            if '/issues/' in current_url and 'new' not in current_url:
                issue_id_match = re.search(r'/issues/(\d+)', current_url)
                if issue_id_match:
                    issue_id = issue_id_match.group(1)
                    print(f"チケット作成成功: #{issue_id}")
                    
                    # 作成されたチケットの詳細を確認
                    print(f"\n=== チケット #{issue_id} の詳細確認 ===")
                    details_result = scraper.get_issue_details(issue_id)
                    if details_result.get('success'):
                        issue_details = details_result.get('issue', {})
                        print(f"件名: {issue_details.get('subject')}")
                        print(f"担当者: {issue_details.get('assigned_to')}")
                        print(f"ステータス: {issue_details.get('status')}")
                        print(f"優先度: {issue_details.get('priority')}")
                        print(f"トラッカー: {issue_details.get('tracker')}")
                        
                        # 担当者が正しく設定されているか確認
                        actual_assignee = issue_details.get('assigned_to', '').strip()
                        if actual_assignee == assignee_name:
                            print(f"担当者が正しく設定されています: {actual_assignee}")
                        elif actual_assignee:
                            print(f"担当者が異なります - 期待値: {assignee_name}, 実際: {actual_assignee}")
                        else:
                            print("担当者が設定されていません")
                            
                    else:
                        print(f"チケット詳細取得に失敗: {details_result.get('error')}")
                else:
                    print("チケットIDを抽出できませんでした")
            else:
                print(f"チケット作成に失敗した可能性があります: {current_url}")
                
        except Exception as e:
            print(f"フォーム送信失敗: {e}")
        
    except Exception as e:
        print(f"テストエラー: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # ログアウト
        print("\n=== ログアウト ===")
        logout_result = scraper.logout()
        print(f"ログアウト結果: {logout_result}")

if __name__ == "__main__":
    test_simple_create()