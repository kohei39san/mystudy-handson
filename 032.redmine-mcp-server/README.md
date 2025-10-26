# Redmine MCP サーバー

## 概要

このプロジェクトは、WebスクレイピングによるRedmine MCPサーバーの実装です。APIキーによる認証ではなく、Webスクレイピングによるブラウザ認証を使用してRedmineのプロジェクト一覧を取得します。

## 機能

- **Webスクレイピング認証**: Redmineのログインフォームを使用した認証
- **プロジェクト一覧取得**: 認証後にプロジェクト一覧をスクレイピングで取得
- **MCPプロトコル対応**: Model Context Protocolに準拠したサーバー実装

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
├── test_server.py            # テストスクリプト
├── src/
│   ├── __init__.py           # パッケージ初期化
│   ├── redmine_mcp_server.py # MCPサーバーのメイン実装
│   ├── redmine_scraper.py    # Redmineスクレイピング機能
│   └── config.py             # 設定ファイル
└── examples/
    └── mcp-config.json       # MCP設定例
```

## 依存関係

- `mcp`: Model Context Protocol実装
- `requests`: HTTP通信
- `beautifulsoup4`: HTMLパース
- `lxml`: XMLパーサー

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
python src/redmine_mcp_server.py
```

### テスト実行

```bash
# スクレイピング機能のテスト
python test_server.py
```

## 使用方法

### 1. 認証

MCPクライアントから`redmine_login`ツールを使用してRedmineにログイン:

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
export DEBUG=true
python src/redmine_mcp_server.py
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

## 注意事項

- このツールはWebスクレイピングを使用するため、Redmineのバージョンやカスタマイズによって動作しない場合があります
- 対象のRedmineサーバーの利用規約を確認してから使用してください
- 過度なリクエストを避けるため、適切な間隔でアクセスしてください
- セキュリティ上の理由から、本番環境では適切な認証情報管理を行ってください

## 対応環境

- **Python**: 3.8以降
- **Redmine**: 4.0以降（推奨）
- **OS**: Windows, macOS, Linux

## ライセンス

このプロジェクトはMITライセンスの下で公開されています。