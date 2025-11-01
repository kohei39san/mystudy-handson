#!/usr/bin/env python3
"""
担当者を指定してチケットを作成する詳細デバッグテスト
"""

import os
import sys
import logging
import re
from dotenv import load_dotenv

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from redmine_selenium import RedmineSeleniumScraper

# Load environment variables
load_dotenv()

# Set up detailed logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

def test_create_debug():
    """担当者を指定してチケットを作成する詳細デバッグテスト"""
    
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
        
        # 新規チケット作成ページに移動してフィールドを調査
        print(f"\n=== 新規チケット作成ページの調査 ===")
        new_issue_url = f"http://168.138.42.184/projects/{project_id}/issues/new"
        scraper.driver.get(new_issue_url)
        
        import time
        time.sleep(3)
        
        print(f"現在のURL: {scraper.driver.current_url}")
        print(f"ページタイトル: {scraper.driver.title}")
        
        # Byクラスをインポート
        from selenium.webdriver.common.by import By
        
        # 全てのinputフィールドを調査
        print("\n=== 全inputフィールド ===")
        all_inputs = scraper.driver.find_elements(By.TAG_NAME, "input")
        for i, inp in enumerate(all_inputs):
            inp_id = inp.get_attribute('id') or 'no-id'
            inp_name = inp.get_attribute('name') or 'no-name'
            inp_type = inp.get_attribute('type') or 'no-type'
            inp_class = inp.get_attribute('class') or 'no-class'
            inp_value = inp.get_attribute('value') or 'no-value'
            print(f"Input {i}: id='{inp_id}', name='{inp_name}', type='{inp_type}', class='{inp_class}', value='{inp_value}'")
        
        # 全てのselectフィールドを調査
        print("\n=== 全selectフィールド ===")
        all_selects = scraper.driver.find_elements(By.TAG_NAME, "select")
        for i, sel in enumerate(all_selects):
            sel_id = sel.get_attribute('id') or 'no-id'
            sel_name = sel.get_attribute('name') or 'no-name'
            sel_class = sel.get_attribute('class') or 'no-class'
            print(f"Select {i}: id='{sel_id}', name='{sel_name}', class='{sel_class}'")
        
        # 全てのtextareaフィールドを調査
        print("\n=== 全textareaフィールド ===")
        all_textareas = scraper.driver.find_elements(By.TAG_NAME, "textarea")
        for i, ta in enumerate(all_textareas):
            ta_id = ta.get_attribute('id') or 'no-id'
            ta_name = ta.get_attribute('name') or 'no-name'
            ta_class = ta.get_attribute('class') or 'no-class'
            print(f"Textarea {i}: id='{ta_id}', name='{ta_name}', class='{ta_class}'")
        
        # フォームを調査
        print("\n=== フォーム調査 ===")
        forms = scraper.driver.find_elements(By.TAG_NAME, "form")
        for i, form in enumerate(forms):
            form_id = form.get_attribute('id') or 'no-id'
            form_class = form.get_attribute('class') or 'no-class'
            form_action = form.get_attribute('action') or 'no-action'
            print(f"Form {i}: id='{form_id}', class='{form_class}', action='{form_action}'")
        
        # ページソースの一部を確認（subjectフィールド関連）
        print("\n=== ページソース内のsubject関連 ===")
        page_source = scraper.driver.page_source
        import re
        subject_matches = re.findall(r'[^>]*subject[^<]*', page_source, re.IGNORECASE)
        for i, match in enumerate(subject_matches[:10]):  # 最初の10個
            print(f"Subject match {i}: {match}")
        
        # 手動でチケット作成を試行
        print(f"\n=== 手動チケット作成試行 ===")
        
        # トラッカーを設定
        try:
            from selenium.webdriver.support.ui import Select
            tracker_select = scraper.driver.find_element(By.ID, "issue_tracker_id")
            select = Select(tracker_select)
            select.select_by_value("1")
            print("トラッカー設定成功")
        except Exception as e:
            print(f"トラッカー設定失敗: {e}")
        
        # 件名を設定（複数の方法を試行）
        subject_set = False
        subject_methods = [
            ("ID", "issue_subject"),
            ("NAME", "issue[subject]"),
            ("CSS", "input[name='issue[subject]']"),
            ("CSS", "#issue_subject"),
        ]
        
        for method_name, selector in subject_methods:
            try:
                if method_name == "ID":
                    subject_field = scraper.driver.find_element(By.ID, selector)
                elif method_name == "NAME":
                    subject_field = scraper.driver.find_element(By.NAME, selector)
                else:  # CSS
                    subject_field = scraper.driver.find_element(By.CSS_SELECTOR, selector)
                
                subject_field.clear()
                subject_field.send_keys(f"デバッグテスト - {assignee_name}")
                subject_set = True
                print(f"件名設定成功 ({method_name}: {selector})")
                break
            except Exception as e:
                print(f"件名設定失敗 ({method_name}: {selector}): {e}")
        
        if not subject_set:
            print("件名設定に完全に失敗しました")
            return
        
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
                    print(f"✅ チケット作成成功: #{issue_id}")
                    
                    # 作成されたチケットの詳細を確認
                    details_result = scraper.get_issue_details(issue_id)
                    if details_result.get('success'):
                        issue_details = details_result.get('issue', {})
                        print(f"件名: {issue_details.get('subject')}")
                        print(f"担当者: {issue_details.get('assigned_to')}")
                        print(f"ステータス: {issue_details.get('status')}")
                        
                        # 担当者が正しく設定されているか確認
                        actual_assignee = issue_details.get('assigned_to', '').strip()
                        if actual_assignee == assignee_name:
                            print(f"✅ 担当者が正しく設定されています: {actual_assignee}")
                        elif actual_assignee:
                            print(f"⚠️ 担当者が異なります - 期待値: {assignee_name}, 実際: {actual_assignee}")
                        else:
                            print("❌ 担当者が設定されていません")
                    else:
                        print(f"チケット詳細取得失敗: {details_result.get('error')}")
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
    test_create_debug()