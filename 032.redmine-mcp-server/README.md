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
├── TROUBLESHOOTING.md        # トラブルシューティングガイド
├── requirements.txt          # Python依存関係
├── setup.py                  # セットアップスクリプト
├── .env.example              # 環境変数設定例
├── install.sh                # インストールスクリプト
├── run.sh                    # 実行スクリプト
├── test_selenium.py          # Seleniumテストスクリプト
├── src/
│   ├── __init__.py           # パッケージ初期化
│   ├── redmine_mcp_server.py # MCPサーバーのメイン実装
│   ├── redmine_scraper.py    # Redmineスクレイピング機能（requests版）
│   ├── redmine_selenium.py   # Redmineスクレイピング機能（Selenium版）
│   └── config.py             # 設定ファイル
└── examples/
    ├── mcp-config.json       # MCP設定例
    └── vscode-settings.json  # VSCode設定例
```

## 依存関係

- `mcp`: Model Context Protocol実装
- `requests`: HTTP通信
- `beautifulsoup4`: HTMLパース
- `lxml`: XMLパーサー
- `selenium`: Webブラウザ自動化（2FA対応用）
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
```

## 使用方法

### 自動ログイン（推奨）

環境変数に認証情報を設定することで、サーバー起動時に自動的にログインします：

```bash
# .envファイルに設定
REDMINE_USERNAME=your_username
REDMINE_PASSWORD=your_password

# 2FA有効な場合はSeleniumを使用
USE_SELENIUM=true
```

### 1. 手動認証（オプション）

自動ログインが設定されていない場合、MCPクライアントから`redmine_login`ツールを使用：

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

## トラブルシューティング

詳細なトラブルシューティング情報については、[TROUBLESHOOTING.md](./TROUBLESHOOTING.md)を参照してください。

### よくある問題

- **ログインに失敗する**: ユーザー名・パスワード、RedmineのURL設定を確認
- **プロジェクトが取得できない**: ユーザーの権限、Redmineのバージョンを確認
- **セッションタイムアウト**: 環境変数`SESSION_TIMEOUT`で調整可能

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
| `REDMINE_USERNAME` | 自動ログイン用ユーザー名 | なし |
| `REDMINE_PASSWORD` | 自動ログイン用パスワード | なし |
| `USE_SELENIUM` | Selenium使用フラグ（2FA対応） | `false` |
| `TWOFA_WAIT` | 2FA認証待機時間（秒） | `300` |
| `TWOFA_POLL_INTERVAL` | 2FA認証確認間隔（秒） | `3` |

## 注意事項

- このツールはWebスクレイピングを使用するため、Redmineのバージョンやカスタマイズによって動作しない場合があります
- 2FA認証が有効な場合、Seleniumを使用してブラウザが自動的に開きます
- 対象のRedmineサーバーの利用規約を確認してから使用してください
- 過度なリクエストを避けるため、適切な間隔でアクセスしてください
- セキュリティ上の理由から、本番環境では適切な認証情報管理を行ってください
- Chromeブラウザがインストールされていることを確認してください（Selenium使用時）

## 対応環境

- **Python**: 3.8以降
- **Redmine**: 4.0以降（推奨）
- **OS**: Windows, macOS, Linux
- **ブラウザ**: Google Chrome（Selenium使用時）

## ライセンス

このプロジェクトはMITライセンスの下で公開されています。