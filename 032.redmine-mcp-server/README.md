# Redmine MCP サーバー

## 概要

このプロジェクトは、WebスクレイピングによるRedmine MCPサーバーの実装です。APIキーによる認証ではなく、Webスクレイピングによるブラウザ認証を使用してRedmineのプロジェクト一覧を取得します。

## 機能

- **Webスクレイピング認証**: Redmineのログインフォームを使用した認証
- **2FA対応**: 二要素認証が有効なRedmineサーバーに対応（Selenium使用）
- **プロジェクト一覧取得**: 認証後にプロジェクト一覧をスクレイピングで取得
- **MCPプロトコル対応**: Model Context Protocolに準拠したサーバー実装
- **自動ブラウザ管理**: 認証時は可視ブラウザ、認証後はヘッドレスモードに自動切り替え

## ファイル構成

```
032.redmine-mcp-server/
├── README.md                 # このファイル
├── requirements.txt          # Python依存関係
├── setup.py                  # セットアップスクリプト
├── .env.example              # 環境変数設定例
├── install.sh                # インストールスクリプト
├── run.sh                    # 実行スクリプト
├── test_selenium.py          # Seleniumテストスクリプト
├── validate.py               # 実装検証スクリプト
├── src/
│   ├── __init__.py           # パッケージ初期化
│   ├── redmine_mcp_server.py # MCPサーバーのメイン実装
│   ├── redmine_selenium.py   # Redmineスクレイピング機能（Selenium版）
│   └── config.py             # 設定ファイル
└── examples/
    ├── mcp-config.json       # MCP設定例
    └── vscode-settings.json  # VSCode設定例
```

## 依存関係

- `mcp`: Model Context Protocol実装
- `selenium`: Webブラウザ自動化（2FA対応）
- `webdriver-manager`: ChromeDriver自動管理
- `python-dotenv`: 環境変数管理

## セットアップ

### 自動インストール（推奨）

```bash
# リポジトリをクローンまたはダウンロード
cd 032.redmine-mcp-server

# 自動インストールスクリプトを実行
chmod +x install.sh
./install.sh

# 環境設定ファイルを編集
cp .env.example .env
# .envファイルでREDMINE_URLを設定
```

### 手動インストール

1. 依存関係のインストール:
```bash
pip install -r requirements.txt
```

2. 環境変数の設定:
```bash
# .envファイルを作成して設定
cp .env.example .env
# または環境変数を直接設定
export REDMINE_URL=https://your-redmine-server.com
```

3. MCPサーバーの起動:
```bash
# 実行スクリプトを使用（推奨）
chmod +x run.sh
./run.sh

# または直接実行
python -m src.redmine_mcp_server

# Windowsの場合
python src\redmine_mcp_server.py
```

### テスト実行

```bash
# Seleniumスクレイピング機能のテスト（2FA対応）
python test_selenium.py

# チケット検索機能のテスト
python test_search.py
```

**注意**: テストスクリプトは環境変数に認証情報がない場合、手動入力を求めます。

## 使用方法

### 1. 認証

MCPクライアントから`redmine_login`ツールを使用してRedmineにログイン：

**注意**: 環境変数に認証情報を設定していない場合でも、MCPツールやテストスクリプトで手動入力できます。

```json
{
  "tool": "redmine_login",
  "arguments": {
    "username": "your_username",
    "password": "your_password"
  }
}
```

### 2. プロジェクト一覧取得

認証後、`get_projects`ツールでプロジェクト一覧を取得:

```json
{
  "tool": "get_projects",
  "arguments": {}
}
```

## 利用可能なツール

### redmine_login
- **説明**: Redmineにログインして認証セッションを確立
- **引数**:
  - `username` (string): ユーザー名
  - `password` (string): パスワード
- **戻り値**: ログイン成功/失敗のステータス

### get_projects
- **説明**: 認証済みセッションでプロジェクト一覧を取得
- **引数**: なし
- **戻り値**: プロジェクト一覧（ID、名前、説明等）

### logout
- **説明**: Redmineからログアウトしてセッションを終了
- **引数**: なし
- **戻り値**: ログアウト成功のステータス

### get_server_info
- **説明**: Redmineサーバーの設定情報と認証状態を取得
- **引数**: なし
- **戻り値**: サーバー情報（URL、認証状態等）

### search_issues
- **説明**: 様々な条件でRedmineのチケットを検索
- **引数**:
  - `status_id` (string): ステータスIDまたは名前
  - `tracker_id` (string): トラッカーIDまたは名前
  - `assigned_to_id` (string): 担当者IDまたは名前
  - `parent_id` (string): 親チケットID
  - `project_id` (string): プロジェクトIDまたは識別子
  - `subject` (string): 件名テキスト検索
  - `description` (string): 説明テキスト検索
  - `notes` (string): ノートテキスト検索
  - `q` (string): 全般テキスト検索
  - `page` (integer): ページ番号
  - `per_page` (integer): 1ページあたりの件数
- **戻り値**: チケット一覧、総数、ページネーション情報

## トラブルシューティング

### よくある問題

#### ログインに失敗する
- ユーザー名・パスワードが正しいか確認
- RedmineのURL設定を確認
- Redmineのバージョンやカスタマイズを確認
- 2FA認証が有効な場合、ブラウザで手動認証を完了

#### プロジェクトが取得できない
- ユーザーにプロジェクト閲覧権限があるか確認
- Redmineのバージョンを確認（4.0以降推奨）
- プロジェクトページの構造をデバッグモードで確認

#### セッションタイムアウト
- 環境変数`SESSION_TIMEOUT`で調整可能
- 長時間使用しない場合は再ログインが必要

#### 接続エラー
- ネットワーク接続を確認
- `REQUEST_TIMEOUT`を延長
- プロキシ設定が必要な場合は環境変数で設定

#### SSL証明書エラー
- 証明書が有効か確認
- 自己署名証明書の場合は適切な設定が必要

### デバッグモード

```bash
# Linux/macOS
export DEBUG=true
python src/redmine_mcp_server.py

# Windows
set DEBUG=true
python src\redmine_mcp_server.py
```

## 環境変数

| 変数名 | 説明 | デフォルト値 |
|--------|------|-------------|
| `REDMINE_URL` | RedmineサーバーのURL | `http://localhost:3000` |
| `SESSION_TIMEOUT` | セッションタイムアウト（秒） | `3600` |
| `REQUEST_TIMEOUT` | リクエストタイムアウト（秒） | `30` |
| `MAX_RETRIES` | 最大リトライ回数 | `3` |
| `RETRY_DELAY` | リトライ間隔（秒） | `1.0` |
| `DEBUG` | デバッグモード | `false` |
| `TWOFA_WAIT` | 2FA認証待機時間（秒） | `300` |
| `TWOFA_POLL_INTERVAL` | 2FA認証確認間隔（秒） | `3` |

## 注意事項

- このツールはWebスクレイピングを使用するため、Redmineのバージョンやカスタマイズによって動作しない場合があります
- 2FA認証が有効な場合、Seleniumを使用してブラウザが自動的に開きます
- 対象のRedmineサーバーの利用規約を確認してから使用してください
- 過度なリクエストを避けるため、適切な間隔でアクセスしてください
- セキュリティ上の理由から、本番環境では適切な認証情報管理を行ってください
- Chromeブラウザがインストールされていることを確認してください（Selenium使用時）

## 制限事項

- **Redmine依存**: HTMLの構造変更に影響を受ける可能性
- **認証方式**: フォーム認証のみサポート（LDAP、OAuth等は未対応）
- **パフォーマンス**: APIと比較して処理速度が劣る
- **ブラウザ依存**: Chromeブラウザが必要

## 今後の拡張可能性

- チケット詳細取得
- チケット作成・更新
- ファイルダウンロード
- キャッシュ機能
- 並列処理
- 高度な検索フィルター

## 対応環境

- **Python**: 3.8以降
- **Redmine**: 4.0以降（推奨）
- **OS**: Windows, macOS, Linux
- **ブラウザ**: Google Chrome（Selenium使用時）

## ライセンス

このプロジェクトはMITライセンスの下で公開されています。