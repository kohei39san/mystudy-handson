# トラブルシューティングガイド

## よくある問題と解決方法

### 1. ログインに失敗する

#### 症状
- `redmine_login`ツールでログインしようとすると失敗する
- "Login failed - invalid credentials or form structure changed"エラーが表示される

#### 解決方法

**A. 認証情報の確認**
```bash
# 正しいユーザー名とパスワードを確認
# Redmineのウェブインターフェースで直接ログインできるか確認
```

**B. RedmineサーバーURLの確認**
```bash
# .envファイルまたは環境変数でRedmineのURLが正しく設定されているか確認
export REDMINE_URL=https://your-redmine-server.com
```

**C. Redmineのバージョン確認**
- 古いバージョンや大幅にカスタマイズされたRedmineでは、ログインフォームの構造が異なる場合があります
- ログインページのHTMLソースを確認し、フォームフィールド名を調べてください

### 2. プロジェクト一覧が取得できない

#### 症状
- ログインは成功するが、`get_projects`でプロジェクトが取得できない
- "No projects found"メッセージが表示される

#### 解決方法

**A. ユーザー権限の確認**
```bash
# ログインしたユーザーにプロジェクト閲覧権限があるか確認
# Redmineの管理画面でユーザーの権限設定を確認
```

**B. プロジェクトページの構造確認**
```bash
# デバッグモードを有効にして詳細なログを確認
export DEBUG=true
python src/redmine_mcp_server.py
```

**C. 手動でのプロジェクトページ確認**
- ブラウザでRedmineにログインし、プロジェクト一覧ページ（/projects）にアクセス
- ページの構造が期待される形式と一致するか確認

### 3. セッションタイムアウト

#### 症状
- しばらく操作しないとセッションが切れる
- "Session expired or not authenticated"エラーが表示される

#### 解決方法

**A. セッションタイムアウトの調整**
```bash
# .envファイルでセッションタイムアウトを延長
SESSION_TIMEOUT=7200  # 2時間に設定
```

**B. 再ログイン**
```bash
# セッションが切れた場合は再度ログインツールを使用
```

### 4. 接続エラー

#### 症状
- "Connection failed"や"Request timeout"エラーが表示される
- サーバーに接続できない

#### 解決方法

**A. ネットワーク接続の確認**
```bash
# RedmineサーバーにPingが通るか確認
ping your-redmine-server.com

# HTTPSアクセスが可能か確認
curl -I https://your-redmine-server.com
```

**B. タイムアウト設定の調整**
```bash
# .envファイルでタイムアウト値を調整
REQUEST_TIMEOUT=60  # 60秒に延長
```

**C. プロキシ設定**
```bash
# 企業環境でプロキシが必要な場合
export HTTP_PROXY=http://proxy.company.com:8080
export HTTPS_PROXY=https://proxy.company.com:8080
```

### 5. SSL証明書エラー

#### 症状
- SSL証明書の検証エラーが発生する
- 自己署名証明書を使用しているRedmineサーバーでエラーが発生

#### 解決方法

**A. 証明書の確認**
```bash
# SSL証明書が有効か確認
openssl s_client -connect your-redmine-server.com:443
```

**B. 証明書検証の無効化（非推奨）**
- セキュリティ上の理由から推奨されませんが、テスト環境では以下の方法があります：
```python
# redmine_scraper.pyで以下を追加（本番環境では使用しないでください）
import ssl
ssl._create_default_https_context = ssl._create_unverified_context
```

### 6. デバッグ情報の取得

#### デバッグモードの有効化
```bash
# 詳細なログを出力
export DEBUG=true
python test_server.py
```

#### ログレベルの調整
```python
# redmine_mcp_server.pyでログレベルを変更
logging.basicConfig(level=logging.DEBUG)
```

### 7. 環境固有の問題

#### Windows環境
```cmd
# PowerShellでの環境変数設定
$env:REDMINE_URL="https://your-redmine-server.com"
$env:DEBUG="true"
```

#### macOS/Linux環境
```bash
# bashでの環境変数設定
export REDMINE_URL="https://your-redmine-server.com"
export DEBUG="true"
```

## サポートが必要な場合

1. **ログの収集**: デバッグモードを有効にしてエラーログを収集
2. **環境情報の確認**: Python版、OS、Redmineバージョンを確認
3. **再現手順の記録**: 問題が発生する具体的な手順を記録
4. **設定ファイルの確認**: .envファイルや設定内容を確認（パスワードは除く）

## 既知の制限事項

- **Redmineバージョン**: 4.0以降で動作確認済み
- **認証方式**: 標準のフォーム認証のみサポート（LDAP、OAuth等は未対応）
- **カスタマイズ**: 大幅にカスタマイズされたRedmineでは動作しない場合があります
- **プラグイン**: 一部のRedmineプラグインがページ構造を変更する場合があります