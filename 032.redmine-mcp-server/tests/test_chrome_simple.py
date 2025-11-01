#!/usr/bin/env python3
"""
Chrome起動簡単テスト
"""

import os
import sys
import traceback

def test_chrome():
    """Chrome起動テスト"""
    print("Chrome起動テスト開始")
    
    try:
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options
        from selenium.webdriver.chrome.service import Service
        from webdriver_manager.chrome import ChromeDriverManager
        
        print("必要なモジュールのインポート完了")
        
        # Chrome設定
        chrome_options = Options()
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        
        print("ChromeDriverダウンロード中...")
        service = Service(ChromeDriverManager().install())
        
        print("Chrome起動中...")
        driver = webdriver.Chrome(service=service, options=chrome_options)
        
        print("Chrome起動成功")
        print("Googleにアクセス中...")
        driver.get("https://www.google.com")
        print(f"ページタイトル: {driver.title}")
        
        driver.quit()
        print("Chrome終了完了")
        return True
        
    except Exception as e:
        print(f"エラー発生: {e}")
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_chrome()
    if success:
        print("テスト成功")
    else:
        print("テスト失敗")