#!/usr/bin/env python3
"""
トラッカーフィールド取得テスト
指定したトラッカーの必須・任意フィールドを入力型を含めて取得するテスト
"""

import os
import sys
from dotenv import load_dotenv

# プロジェクトルートをパスに追加
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from redmine_selenium import RedmineSeleniumScraper

def test_tracker_fields():
    """トラッカーフィールド取得テスト"""
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
        
        # 利用可能なトラッカーを取得
        print(f"\n=== 利用可能なトラッカー取得 ===")
        trackers = scraper.get_available_trackers(project_id)
        if trackers.get('success') and trackers.get('trackers'):
            print("利用可能なトラッカー:")
            for tracker in trackers['trackers']:
                print(f"  - {tracker['text']} (ID: {tracker['value']})")
        else:
            print("トラッカーの取得に失敗しました")
            return
        
        # 各トラッカーのフィールドを取得
        for tracker in trackers['trackers']:
            tracker_id = tracker['value']
            tracker_name = tracker['text']
            
            print(f"\n=== トラッカー '{tracker_name}' (ID: {tracker_id}) のフィールド取得 ===")
            
            fields_result = scraper.get_tracker_fields(project_id, tracker_id)
            
            if fields_result.get('success'):
                fields = fields_result.get('fields', [])
                required_fields = fields_result.get('required_fields', [])
                optional_fields = fields_result.get('optional_fields', [])
                
                print(f"フィールド取得結果: {fields_result['message']}")
                
                # 必須フィールド
                if required_fields:
                    print("\n必須フィールド:")
                    for field in required_fields:
                        print(f"  - {field['name']} ({field['type']})")
                        print(f"    ID: {field['id']}")
                        if field['type'] == 'select' and field.get('options'):
                            print(f"    選択肢: {len(field['options'])}個")
                            for opt in field['options'][:3]:  # 最初の3つを表示
                                print(f"      - {opt['text']} (値: {opt['value']})")
                            if len(field['options']) > 3:
                                print(f"      ... 他 {len(field['options']) - 3}個")
                        elif field['type'] == 'input' and field.get('input_type'):
                            print(f"    入力タイプ: {field['input_type']}")
                        print()
                
                # 任意フィールド
                if optional_fields:
                    print("任意フィールド:")
                    for field in optional_fields:
                        print(f"  - {field['name']} ({field['type']})")
                        print(f"    ID: {field['id']}")
                        if field['type'] == 'select' and field.get('options'):
                            print(f"    選択肢: {len(field['options'])}個")
                            for opt in field['options'][:2]:  # 最初の2つを表示
                                print(f"      - {opt['text']} (値: {opt['value']})")
                            if len(field['options']) > 2:
                                print(f"      ... 他 {len(field['options']) - 2}個")
                        elif field['type'] == 'input' and field.get('input_type'):
                            print(f"    入力タイプ: {field['input_type']}")
                        if field.get('placeholder'):
                            print(f"    プレースホルダー: {field['placeholder']}")
                        print()
                
                print(f"サマリー: 全{len(fields)}フィールド (必須: {len(required_fields)}, 任意: {len(optional_fields)})")
            else:
                print(f"フィールド取得エラー: {fields_result.get('message')}")
        
        # デフォルトトラッカーのフィールドも取得
        print(f"\n=== デフォルトトラッカーのフィールド取得 ===")
        default_fields_result = scraper.get_tracker_fields(project_id)
        
        if default_fields_result.get('success'):
            fields = default_fields_result.get('fields', [])
            print(f"デフォルトトラッカーフィールド取得結果: {default_fields_result['message']}")
            print(f"フィールド数: {len(fields)}")
        else:
            print(f"デフォルトトラッカーフィールド取得エラー: {default_fields_result.get('message')}")
        
    except Exception as e:
        print(f"テスト中にエラーが発生しました: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        scraper.logout()

if __name__ == "__main__":
    test_tracker_fields()