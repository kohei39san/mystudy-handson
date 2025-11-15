# Redmine MCP Server 設計指針

## 概要

本ドキュメントは、Redmine MCP Serverの実装から読み取れる設計指針と設計思想をまとめたものです。

## アーキテクチャ設計

### 1. レイヤー分離

**原則**: 責務の明確な分離により保守性と拡張性を確保

- **MCPサーバー層** (`032.redmine-mcp-server/src/redmine_mcp_server.py`)
  - Model Context Protocolの実装
  - ツール定義とリクエストハンドリング
  - 入力バリデーションとエラーハンドリング

- **Webスクレイピング層** (`032.redmine-mcp-server/src/redmine_selenium.py`)
  - Selenium WebDriverによるブラウザ操作
  - HTML解析とデータ抽出
  - セッション管理と認証処理

- **設定管理層** (`032.redmine-mcp-server/src/config.py`)
  - 環境変数の一元管理
  - デフォルト値の定義
  - 設定の型安全性確保

### 2. 非同期処理設計

**原則**: MCPプロトコルの非同期要件に対応しつつ、同期的なSelenium操作を適切にラップ

```python
async def _handle_login(self, arguments: Dict[str, Any]) -> List[TextContent]:
    # 同期的なSelenium操作を非同期ハンドラー内で実行
    result = self.scraper.login(username, password)
    return [TextContent(type="text", text=str(result))]
```

## 認証とセッション管理

### 1. 2要素認証対応

**原則**: ユーザーの手動操作が必要な認証フローに柔軟に対応

- 可視ブラウザでの認証開始
- URL変化の監視による認証完了検知
- 認証完了後のヘッドレスモードへの自動切り替え

```python
def _switch_to_headless(self):
    # クッキーとセッション状態を保持したままヘッドレスモードに移行
    cookies = self.driver.get_cookies()
    self.driver.quit()
    self.driver = self._create_driver(headless=True)
    # クッキーを復元
    for cookie in cookies:
        self.driver.add_cookie(cookie)
```

### 2. セッション永続化

**原則**: 認証状態を維持し、不要な再認証を回避

- クッキーベースのセッション管理
- セッション有効性の自動チェック
- ログインページへのリダイレクト検知

## データ抽出戦略

### 1. 柔軟なフィールド検出

**原則**: 動的にフォーム要素をスキャンし、利用可能なフィールドを自動検出

- 全フォーム要素の動的スキャン
- 必須/任意フィールドの自動判定
- カスタムフィールドの自動認識

## バリデーション設計

### 1. 事前バリデーション

**原則**: 操作実行前にデータの妥当性を検証し、早期エラー検出

```python
def _validate_fields(self, project_id: str, tracker_id: str, fields: Dict[str, Any]):
    # トラッカーフィールド定義を取得
    tracker_fields_result = self.get_tracker_fields(project_id, str(tracker_id))
    
    # 必須フィールドチェック
    for req_field in required_fields:
        if field_id not in fields:
            missing_required.append(field_id)
    
    # フィールド存在チェック
    for field_name in fields:
        if field_name not in field_map:
            invalid_fields.append(field_name)
```

### 2. コンテキスト依存バリデーション

**原則**: プロジェクトやトラッカーに応じた動的バリデーション

- トラッカーの利用可能性検証
- プロジェクトメンバーの検証
- フィールド値の妥当性検証

## エラーハンドリング

### 1. 段階的エラー処理

**原則**: エラーを適切なレベルでキャッチし、有用なエラーメッセージを提供

```python
try:
    # 主要処理
    result = self.scraper.create_issue(...)
except Exception as e:
    logger.error(f"Error creating issue: {e}")
    return {
        'success': False,
        'message': f"Error creating issue: {str(e)}"
    }
```

### 2. グレースフルデグラデーション

**原則**: 一部の機能が失敗しても、可能な範囲で処理を継続

- フィールド設定の部分的失敗を許容
- データ抽出の代替手段を試行
- バリデーション失敗時の処理継続オプション

## ロギング戦略

### 1. レベル別ロギング

**原則**: デバッグモードと本番モードで適切なログレベルを使い分け

```python
logging.basicConfig(level=logging.INFO if config.debug else logging.WARNING)
logger.info("重要な操作")
logger.debug("詳細なデバッグ情報")
logger.error("エラー情報")
```

### 2. 構造化ログ

**原則**: 問題追跡に必要な情報を含む構造化されたログ出力

- 操作の開始と完了をログ
- パラメータと結果をログ
- エラー時のコンテキスト情報をログ

## 設定管理

### 1. 環境変数ベース設定

**原則**: 環境に応じた柔軟な設定変更を可能にする

```python
class RedmineConfig:
    def __init__(self):
        self.base_url = os.getenv('REDMINE_URL', 'http://localhost:3000')
        self.session_timeout = int(os.getenv('SESSION_TIMEOUT', '3600'))
        self.debug = os.getenv('DEBUG', 'false').lower() == 'true'
```

### 2. デフォルト値の提供

**原則**: 設定が省略された場合でも動作する合理的なデフォルト値

- タイムアウト値のデフォルト
- リトライ設定のデフォルト
- User-Agentのデフォルト

## Selenium操作のベストプラクティス

### 1. 明示的待機

**原則**: ページロード完了を確実に待機

```python
time.sleep(2)  # ページロード待機
wait = WebDriverWait(self.driver, 10)
element = wait.until(EC.presence_of_element_located((By.ID, "username")))
```

### 2. 自動化検知回避

**原則**: Webサイトの自動化検知を回避する設定

```python
chrome_options.add_argument('--disable-blink-features=AutomationControlled')
chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
```

## 拡張性設計

### 1. ツールの追加容易性

**原則**: 新しいツールを簡単に追加できる構造

- ツール定義の一元管理
- ハンドラーメソッドの命名規則
- 統一されたレスポンス形式

### 2. プラグイン可能な設計

**原則**: 将来的な機能拡張を見据えた設計

- スクレイパーの交換可能性
- 設定の拡張可能性
- ログ出力のカスタマイズ可能性

## セキュリティ考慮事項

### 1. 認証情報の取り扱い

**原則**: 認証情報をログに出力しない

```python
logger.info(f"Login attempt for user: {username}")  # パスワードはログに出力しない
```

### 2. セッション管理

**原則**: セッションの適切なクリーンアップ

```python
def __del__(self):
    if self.driver:
        try:
            self.driver.quit()
        except:
            pass
```

## パフォーマンス最適化

### 1. ヘッドレスモード活用

**原則**: 認証後はヘッドレスモードで高速動作

- 認証時のみ可視ブラウザ使用
- 認証完了後の自動切り替え
- リソース消費の最小化

### 2. 効率的なデータ抽出

**原則**: 必要最小限のページアクセスでデータ取得

- 一度のページロードで複数情報を抽出
- キャッシュ可能な情報の再利用
- 不要なページ遷移の回避

## テスタビリティ

### 1. 依存性の分離

**原則**: テストしやすい構造

- 各レイヤーの独立性
- モック可能な外部依存
- 明確なインターフェース定義

### 2. エラー再現性

**原則**: デバッグモードでの詳細情報出力

- ページソースのスニペット出力
- URL遷移の追跡
- 要素検出の詳細ログ

## まとめ

Redmine MCP Serverの設計は以下の原則に基づいています：

1. **堅牢性**: 多様な環境とエラー状況に対応
2. **保守性**: 明確な責務分離と構造化されたコード
3. **拡張性**: 新機能追加が容易な設計
4. **ユーザビリティ**: 直感的なツール定義と有用なエラーメッセージ
5. **セキュリティ**: 認証情報の適切な取り扱い
6. **パフォーマンス**: 効率的なブラウザ操作とデータ抽出

これらの設計指針により、実用的で信頼性の高いRedmine連携ツールを実現しています。
