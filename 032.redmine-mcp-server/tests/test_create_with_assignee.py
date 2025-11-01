#!/usr/bin/env python3
"""
担当者を指定してチケットを作成し、担当者が設定されているか確認するテスト
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

def test_create_with_assignee():
    """担当者を指定してチケットを作成し、担当者が設定されているか確認"""
    
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
        
        # チケット作成
        print(f"\n=== 担当者付きチケット作成 ===")
        print(f"担当者: {assignee_name} (ID: {assignee_id})")
        
        create_result = scraper.create_issue(
            project_id=project_id,
            subject=f"担当者テスト - {assignee_name}",
            description="担当者が正しく設定されているかのテスト",
            tracker_id=1,
            assigned_to_id=assignee_id
        )
        
        print(f"チケット作成結果の詳細: {create_result}")
        
        if not create_result.get('success'):
            print(f"チケット作成に失敗: {create_result.get('error')}")
            print(f"完全な結果: {create_result}")
            return
            
        issue_id = create_result.get('issue_id')
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
                print(f"✅ 担当者が正しく設定されています: {actual_assignee}")
            elif actual_assignee:
                print(f"⚠️ 担当者が異なります - 期待値: {assignee_name}, 実際: {actual_assignee}")
            else:
                print("❌ 担当者が設定されていません")
                
        else:
            print(f"チケット詳細取得に失敗: {details_result.get('error')}")
        
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
    test_create_with_assignee()