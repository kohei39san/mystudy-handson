#!/usr/bin/env python3
"""
修正トラッカーで親チケット、担当者、指摘者を指定してチケット作成テスト
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from redmine_selenium import RedmineSeleniumScraper
import config

def test_create_fix_ticket_with_all_fields():
    """修正トラッカーで親チケット、担当者、指摘者を指定してチケット作成"""
    scraper = RedmineSeleniumScraper()
    
    try:
        # Login
        print("ログイン中...")
        username = os.getenv('REDMINE_USERNAME', 'kohei')
        password = os.getenv('REDMINE_PASSWORD', 'ariari_ssKK3')
        login_result = scraper.login(username, password)
        if not login_result['success']:
            print(f"ログイン失敗: {login_result['message']}")
            return
        print("ログイン成功")
        
        project_id = "hoge-project"
        tracker_id = "4"  # 修正トラッカー
        
        print("\n=== 修正トラッカーで親チケット、担当者、指摘者を指定してチケット作成 ===")
        
        # 完全なフィールド指定
        ticket_fields = {
            'issue_subject': '修正チケット - 親チケット、担当者、指摘者付き',
            'issue_description': 'このチケットは修正トラッカーで作成され、親チケット、担当者、指摘者が指定されています。',
            'issue_status_id': '1',  # 新規
            'issue_priority_id': '2',  # 通常
            'issue_assigned_to_id': '1',  # admin (担当者)
            'issue_parent_issue_id': '140',  # 親チケット (既存のチケットID)
            'issue_custom_field_values_3': '5'  # 指摘者 (k s)
        }
        
        print(f"作成するチケットの詳細:")
        print(f"  プロジェクト: {project_id}")
        print(f"  トラッカー: {tracker_id} (修正)")
        print(f"  題名: {ticket_fields['issue_subject']}")
        print(f"  担当者: {ticket_fields['issue_assigned_to_id']} (admin)")
        print(f"  親チケット: {ticket_fields['issue_parent_issue_id']}")
        print(f"  指摘者: {ticket_fields['issue_custom_field_values_3']} (k s)")
        
        result = scraper.create_issue(project_id, tracker_id, **ticket_fields)
        
        if result['success']:
            print(f"\n✅ チケット作成成功!")
            print(f"   チケットID: #{result['issue_id']}")
            print(f"   URL: {result['issue_url']}")
            
            # 作成されたチケットの詳細を確認
            print(f"\n=== 作成されたチケットの詳細確認 ===")
            details_result = scraper.get_issue_details(result['issue_id'])
            if details_result['success']:
                issue = details_result['issue']
                print(f"題名: {issue.get('subject', 'N/A')}")
                print(f"トラッカー: {issue.get('tracker', 'N/A')}")
                print(f"ステータス: {issue.get('status', 'N/A')}")
                print(f"優先度: {issue.get('priority', 'N/A')}")
                print(f"担当者: {issue.get('assigned_to', 'N/A')}")
                print(f"親チケット: {issue.get('parent', 'N/A')}")
                print(f"指摘者: {issue.get('指摘者', 'N/A')}")
            else:
                print(f"チケット詳細取得失敗: {details_result['message']}")
        else:
            print(f"\n❌ チケット作成失敗: {result['message']}")
        
    except Exception as e:
        print(f"エラー: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        if scraper.driver:
            scraper.driver.quit()

if __name__ == "__main__":
    test_create_fix_ticket_with_all_fields()