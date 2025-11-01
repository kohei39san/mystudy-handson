#!/usr/bin/env python3
"""
Fixed test script for create_issue and update_issue functionality
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

def test_create_and_update_issue():
    """Test create_issue and update_issue functionality"""
    
    # Get credentials from environment with defaults
    username = os.getenv('REDMINE_USERNAME', 'admin')
    password = os.getenv('REDMINE_PASSWORD', 'admin')
    
    print(f"Using credentials: {username}/{password}")
    
    scraper = RedmineSeleniumScraper()
    
    try:
        # Login
        print("=== ログイン ===")
        login_result = scraper.login(username, password)
        print(f"Login result: {login_result}")
        
        if not login_result.get('success'):
            print("Login failed, cannot proceed with test")
            return
        
        # Get projects first
        print("\n=== プロジェクト取得 ===")
        projects_result = scraper.get_projects()
        if not projects_result.get('success') or not projects_result.get('projects'):
            print("No projects available for testing")
            return
        
        # Find hoge-project or use first available project
        project_id = None
        for project in projects_result['projects']:
            if project['id'] == 'hoge-project':
                project_id = project['id']
                break
        
        if not project_id:
            project_id = projects_result['projects'][0]['id']
        
        print(f"Using project: {project_id}")
        
        # Get tracker fields to understand available trackers
        print("\n=== トラッカーフィールド取得 ===")
        tracker_fields_result = scraper.get_tracker_fields(project_id)
        print(f"Tracker fields result: {tracker_fields_result}")
        
        if not tracker_fields_result.get('success'):
            print("Failed to get tracker fields")
            return
        
        # Extract tracker options from the tracker field
        tracker_options = []
        for field in tracker_fields_result.get('fields', []):
            if field.get('id') == 'issue_tracker_id':
                tracker_options = field.get('options', [])
                break
        
        if not tracker_options:
            print("No tracker options found")
            return
        
        tracker_id = tracker_options[0]['value']
        print(f"Using tracker: {tracker_id}")
        
        # Test 1: Basic issue creation
        print("\n=== Test 1: 基本的なチケット作成 ===")
        create_result = scraper.create_issue(
            project_id=project_id,
            subject="テストチケット - 基本作成",
            tracker_id=int(tracker_id)
        )
        print(f"Create result: {create_result}")
        
        created_issue_id = None
        if create_result.get('success'):
            created_issue_id = create_result.get('issue_id')
            print(f"Created issue #{created_issue_id}")
        else:
            print("Basic issue creation failed")
            return
        
        # Test 2: Full issue creation
        print("\n=== Test 2: 全フィールド指定でのチケット作成 ===")
        create_result = scraper.create_issue(
            project_id=project_id,
            subject="テストチケット - 全フィールド作成",
            description="これは全フィールドを指定したテストチケットです。",
            tracker_id=int(tracker_id),
            priority_id=2,  # 高
            start_date="2024-01-15",
            due_date="2024-01-30",
            estimated_hours=8.5,
            done_ratio=10
        )
        print(f"Create result: {create_result}")
        
        full_issue_id = None
        if create_result.get('success'):
            full_issue_id = create_result.get('issue_id')
            print(f"Created issue #{full_issue_id}")
        
        # Test 3: Update issue status
        if created_issue_id:
            print(f"\n=== Test 3: チケット#{created_issue_id}のステータス更新 ===")
            update_result = scraper.update_issue(
                issue_id=str(created_issue_id),
                status_id="2",  # 対応中
                notes="ステータスを対応中に変更しました（テスト）"
            )
            print(f"Update result: {update_result}")
            
            # Verify the update
            if update_result.get('success'):
                print(f"\n=== 更新確認: チケット#{created_issue_id}の詳細取得 ===")
                details_result = scraper.get_issue_details(str(created_issue_id))
                if details_result.get('success'):
                    issue = details_result['issue']
                    print(f"Updated status: {issue.get('status', 'Unknown')}")
                    print(f"Subject: {issue.get('subject', 'Unknown')}")
        
        # Test 4: Update issue with multiple fields
        if full_issue_id:
            print(f"\n=== Test 4: チケット#{full_issue_id}の複数フィールド更新 ===")
            update_result = scraper.update_issue(
                issue_id=str(full_issue_id),
                subject="テストチケット - 更新済み",
                status_id="3",  # 完了確認待ち
                priority_id="3",  # 低
                done_ratio=50,
                notes="複数フィールドを更新しました（テスト）"
            )
            print(f"Update result: {update_result}")
            
            # Verify the update
            if update_result.get('success'):
                print(f"\n=== 更新確認: チケット#{full_issue_id}の詳細取得 ===")
                details_result = scraper.get_issue_details(str(full_issue_id))
                if details_result.get('success'):
                    issue = details_result['issue']
                    print(f"Updated subject: {issue.get('subject', 'Unknown')}")
                    print(f"Updated status: {issue.get('status', 'Unknown')}")
                    print(f"Updated priority: {issue.get('priority', 'Unknown')}")
        
        # Test 5: Invalid field validation
        print("\n=== Test 5: 無効なフィールド値のバリデーション ===")
        create_result = scraper.create_issue(
            project_id=project_id,
            subject="テストチケット - 無効なトラッカー",
            tracker_id=999  # Invalid tracker ID
        )
        print(f"Create result (should fail): {create_result}")
        
        # Test 6: Missing required field
        print("\n=== Test 6: 必須フィールド不足のテスト ===")
        create_result = scraper.create_issue(
            project_id=project_id,
            # subject is missing (required field)
            tracker_id=int(tracker_id)
        )
        print(f"Create result (should fail): {create_result}")
        
    except Exception as e:
        print(f"Test error: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # Logout
        print("\n=== ログアウト ===")
        logout_result = scraper.logout()
        print(f"Logout result: {logout_result}")

if __name__ == "__main__":
    test_create_and_update_issue()