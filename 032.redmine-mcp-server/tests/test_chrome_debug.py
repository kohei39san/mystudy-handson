#!/usr/bin/env python3
"""
Chrome起動デバッグテスト
"""

import os
import sys
import traceback
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

def test_chrome_basic():
    """基本的なChrome起動テスト"""
    print("=== Chrome基本起動テスト ===")
    
    try:
        # 基本的なChromeオプション
        chrome_options = Options()
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        
        print("ChromeDriverをダウンロード中...")
        service = Service(ChromeDriverManager().install())
        
        print("Chromeブラウザを起動中...")
        driver = webdriver.Chrome(service=service, options=chrome_options)
        
        print("✓ Chrome起動成功")
        
        # 簡単なテスト
        print("Googleにアクセス中...")
        driver.get("https://www.google.com")
        print(f"ページタイトル: {driver.title}")
        
        driver.quit()
        print("✓ Chrome終了成功")
        return True
        
    except Exception as e:
        print(f"✗ Chrome起動失敗: {e}")
        traceback.print_exc()
        return False

def test_chrome_headless():
    """ヘッドレスChrome起動テスト"""
    print("\n=== Chromeヘッドレス起動テスト ===")
    
    try:
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        
        print("✓ Chromeヘッドレス起動成功")
        
        driver.get("https://www.google.com")
        print(f"ページタイトル: {driver.title}")
        
        driver.quit()
        print("✓ Chromeヘッドレス終了成功")
        return True
        
    except Exception as e:
        print(f"✗ Chromeヘッドレス起動失敗: {e}")
        traceback.print_exc()
        return False

def test_redmine_scraper():
    """RedmineScraperのChrome起動テスト"""
    print("\n=== RedmineScraperのChrome起動テスト ===")
    
    try:
        sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))
        from redmine_selenium import RedmineSeleniumScraper
        
        scraper = RedmineSeleniumScraper()
        
        print("RedmineScraperでChrome起動中...")
        # _create_driverメソッドを直接呼び出し
        driver = scraper._create_driver(headless=False)
        
        print("✓ RedmineScraperでChrome起動成功")
        
        driver.get("https://www.google.com")
        print(f"ページタイトル: {driver.title}")
        
        driver.quit()
        print("✓ RedmineScraperでChrome終了成功")
        return True
        
    except Exception as e:
        print(f"✗ RedmineScraperでChrome起動失敗: {e}")
        traceback.print_exc()
        return False

def check_environment():
    """環境情報チェック"""
    print("=== 環境情報チェック ===")
    
    print(f"Python バージョン: {sys.version}")
    print(f"作業ディレクトリ: {os.getcwd()}")
    
    # 必要なモジュールの確認
    modules = ['selenium', 'webdriver_manager', 'dotenv']
    for module in modules:
        try:
            __import__(module)
            print(f"✓ {module}: インストール済み")
        except ImportError:
            print(f"✗ {module}: インストールされていません")
    
    # Chromeの確認
    try:
        import subprocess
        result = subprocess.run(['chrome', '--version'], capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            print(f"✓ Chrome: {result.stdout.strip()}")
        else:
            print("✗ Chrome: コマンドラインから実行できません")
    except:
        try:
            # Windowsの場合
            result = subprocess.run([r'C:\Program Files\Google\Chrome\Application\chrome.exe', '--version'], 
                                  capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                print(f"✓ Chrome: {result.stdout.strip()}")
            else:
                print("✗ Chrome: 標準パスに見つかりません")
        except:
            print("✗ Chrome: インストールされていないか、パスが通っていません")

if __name__ == "__main__":
    check_environment()
    
    # 基本テスト
    basic_success = test_chrome_basic()
    
    # ヘッドレステスト
    headless_success = test_chrome_headless()
    
    # RedmineScraperテスト
    scraper_success = test_redmine_scraper()
    
    print("\n=== テスト結果サマリー ===")
    print(f"基本Chrome起動: {'✓' if basic_success else '✗'}")
    print(f"ヘッドレスChrome起動: {'✓' if headless_success else '✗'}")
    print(f"RedmineScraperChrome起動: {'✓' if scraper_success else '✗'}")
    
    if not any([basic_success, headless_success, scraper_success]):
        print("\n全てのテストが失敗しました。以下を確認してください:")
        print("1. Google Chromeがインストールされているか")
        print("2. seleniumとwebdriver-managerがインストールされているか")
        print("3. ファイアウォールやセキュリティソフトがブロックしていないか")