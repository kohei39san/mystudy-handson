# Redmine MCP Server

## 従来のRedmine利用における課題

- チケット作成・更新のたびにWebブラウザでアクセスが必要で、複数チケットの一括操作や定型作業の自動化が困難
- AIアシスタントがRedmineの情報を直接取得できないため、チケット内容の要約や分析を依頼する際に手動での情報転記が必要
- RedmineのREST APIは機能が限定的で、APIキーの管理・配布が困難な組織環境や2FA認証環境では利用が制約される

## Redmine MCP Serverの概要・目的

Redmine MCP Serverは、Model Context Protocol (MCP) を使用してRedmineと連携するためのサーバーです。

- MCPツールによるチケット操作の自動化、複数チケットの一括処理が可能
- AIアシスタントがRedmine情報を直接取得・操作、手動転記が不要
- WebスクレイピングによりAPI無効化・2FA環境でも動作、APIキー管理不要

### 利用可能なツール一覧

| 概要 | ツール名 | 入力 | 説明 |
|------|----------|------|------|
| Redmineにログインして認証セッションを確立 | `redmine_login` | ユーザー名、パスワード | Webブラウザと同様の認証フローでRedmineにログインする |
| Redmineからログアウトしてセッションを終了 | `logout` | なし | 現在のセッションを終了し、ログアウトする |
| サーバー設定情報と認証状態を取得 | `get_server_info` | なし | Redmineサーバーの設定情報と現在の認証状態を表示する |
| プロジェクト一覧を取得 | `get_projects` | なし | アクセス可能なプロジェクトの一覧を取得する |
| プロジェクトメンバー一覧を取得 | `get_project_members` | プロジェクトID | 指定したプロジェクトに所属するメンバー情報を取得する |
| 様々な条件でチケットを検索 | `search_issues` | プロジェクトID、ステータスID、トラッカーID、担当者ID、件名、全文検索等 | 指定した条件にマッチするチケットを検索し、一覧で返す |
| チケットの詳細情報を取得 | `get_issue_details` | チケットID | 指定したチケットの詳細情報（件名、説明、ステータス等）を取得する |
| 新しいチケットを作成 | `create_issue` | プロジェクトID、トラッカーID、件名、フィールド情報 | 指定した情報で新しいチケットを作成する |
| 既存チケットを更新 | `update_issue` | チケットID、更新フィールド | 指定したチケットの情報を更新する |
| 利用可能なトラッカー一覧を取得 | `get_available_trackers` | プロジェクトID（省略可） | プロジェクトで利用可能なトラッカーとそのフィールド情報を取得する |
| チケットで利用可能なステータス一覧を取得 | `get_available_statuses` | チケットID | 指定したチケットで利用可能なステータス一覧を取得する |
| 新規作成時に利用可能なステータス一覧を取得 | `get_creation_statuses` | プロジェクトID、トラッカーID | 新規チケット作成時に選択可能なステータス一覧を取得する |
| トラッカーで利用可能なフィールド一覧を取得 | `get_tracker_fields` | プロジェクトID、トラッカーID | 指定したトラッカーで利用可能なフィールドとその属性を取得する |

## クイックスタート

### 1. インストール
```bash
# 依存関係をインストール
pip install -r scripts/requirements.txt

# 環境変数を設定
echo "REDMINE_URL=https://your-redmine-server.com" > .env
```

### 2. サーバー起動
```bash
python src/redmine_mcp_server.py
```

## Amazon Q Developerへのインストール

### 設定手順
1. Amazon Q Developer拡張機能をインストール
2. MCP設定ファイルを作成
3. パスを実際の環境に合わせて修正
4. Amazon Q Developerを再起動
5. チャットで「redmine_login」などのツールが利用可能になることを確認

### MCP設定ファイル（~/.amazonq/mcp_servers.json）
```json
{
  "mcpServers": {
    "redmine": {
      "command": "python",
      "args": ["C:\\path\\to\\mystudy-handson\\032.redmine-mcp-server\\src\\redmine_mcp_server.py"],
      "env": {
        "REDMINE_URL": "https://your-redmine-server.com",
        "DEBUG": "false",
        "SESSION_TIMEOUT": "3600"
      }
    }
  }
}
```

## サポートしている環境変数

| 変数名 | 説明 | デフォルト値 | 必須 |
|--------|------|-------------|------|
| `REDMINE_URL` | RedmineサーバーのURL | `http://localhost:3000` | ○ |
| `DEBUG` | デバッグモード（true/false） | `false` | × |
| `SESSION_TIMEOUT` | セッションタイムアウト（秒） | `3600` | × |
| `REQUEST_TIMEOUT` | リクエストタイムアウト（秒） | `30` | × |
| `MAX_RETRIES` | 最大リトライ回数 | `3` | × |
| `RETRY_DELAY` | リトライ間隔（秒） | `1.0` | × |