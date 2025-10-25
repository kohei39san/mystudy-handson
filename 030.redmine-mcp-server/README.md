# Redmine MCP Server

RedmineのチケットAPIを利用したMCPサーバーの実装

## 概要

このプロジェクトは、RedmineのREST APIを使用してチケットの一覧取得と詳細取得を行うMCPサーバーです。Model Context Protocol (MCP) を使用して、AIアシスタントがRedmineのチケット情報にアクセスできるようにします。

## 機能

- **チケット一覧検索**: Redmineのチケット一覧を検索条件に基づいて取得
- **チケット詳細取得**: 指定されたチケットIDの詳細情報を取得
- **プロジェクト一覧取得**: Redmineのプロジェクト一覧を取得
- **ロール一覧取得**: Redmineのロール一覧を取得
- **ロール詳細取得**: 指定されたロールIDの詳細情報を取得
- **トラッカー一覧取得**: Redmineのトラッカー一覧を取得
- **優先度一覧取得**: Redmineのチケット優先度一覧を取得
- **ステータス一覧取得**: Redmineのチケットステータス一覧を取得
- **チケット作成**: 新しいRedmineチケットを作成
- **チケット更新**: 既存のRedmineチケットを更新
- **チケット削除**: Redmineチケットを削除
- **AWS Parameter Store統合**: APIキーとベースURLの安全な管理
- **Zod入力検証**: 型安全な入力パラメータ検証

## 前提条件

- Node.js 18以上
- TypeScript
- AWS CLI設定済み（Parameter Store アクセス用）
- RedmineインスタンスとAPIキー

## セットアップ

### 1. 依存関係のインストール

```bash
cd 030.redmine-mcp-server
npm install
```

### 2. 環境変数の設定

`.env.example`をコピーして`.env`ファイルを作成し、適切な値を設定してください。

```bash
cp .env.example .env
```

### 3. AWS Parameter StoreにAPIキーを保存

```bash
aws ssm put-parameter \
  --name "/redmine/api-key" \
  --value "your-redmine-api-key" \
  --type "SecureString" \
  --description "Redmine API Key"
```

### 4. ビルドと実行

```bash
npm run build
npm start
```

## 設定

### 認証

- RedmineのAPIキーを使用した認証
- APIキーはAWSパラメータストアから安全に取得

### 環境変数

- `REDMINE_BASE_URL`: RedmineのベースURL（オプション、REDMINE_BASE_URL_PARAMETERが設定されている場合）
- `REDMINE_BASE_URL_PARAMETER`: AWSパラメータストア内のベースURLのパラメータ名（オプション）
- `AWS_REGION`: AWSリージョン（オプション、デフォルト: us-east-1）
- `REDMINE_API_KEY_PARAMETER`: AWSパラメータストア内のAPIキーのパラメータ名（必須）

## 使用技術

- **TypeScript**: 型安全な開発
- **MCP SDK**: Model Context Protocol実装
- **Zod**: 入力バリデーション
- **AWS SDK**: パラメータストア連携
- **node-fetch**: HTTP リクエスト

## ツール

### search_redmine_tickets

Redmineのチケット一覧を検索条件に基づいて取得します。

**パラメータ:**
- `project_id` (optional): プロジェクトID
- `status_id` (optional): ステータスID
- `assigned_to_id` (optional): 担当者ID
- `limit` (optional): 取得件数制限 (デフォルト: 25, 最大: 100)
- `offset` (optional): オフセット (デフォルト: 0)

**レスポンス:**
- チケット一覧（ID、件名、ステータス、優先度、担当者、プロジェクト、作成日、更新日）
- 総件数、オフセット、制限値

**使用例:**
```json
{
  "project_id": 1,
  "status_id": 1,
  "limit": 10
}
```

### get_redmine_ticket_detail

指定されたチケットIDの詳細情報を取得します。

**パラメータ:**
- `ticket_id` (required): チケットID

**レスポンス:**
- チケットの完全な詳細情報（説明、カスタムフィールド、ジャーナル、添付ファイル、関連チケット等を含む）

**使用例:**
```json
{
  "ticket_id": 123
}
```

### list_redmine_projects

Redmineのプロジェクト一覧を取得します。

**パラメータ:**
- `limit` (optional): 取得件数制限 (デフォルト: 25, 最大: 100)
- `offset` (optional): オフセット (デフォルト: 0)

**レスポンス:**
- プロジェクト一覧（ID、名前、識別子、説明）
- 総件数、オフセット、制限値

**使用例:**
```json
{
  "limit": 50,
  "offset": 0
}
```

### list_redmine_roles

Redmineのロール一覧を取得します。

**パラメータ:**
- なし

**レスポンス:**
- ロール一覧（ID、名前、割り当て可能フラグ、組み込みロール番号）

**使用例:**
```json
{}
```

### get_redmine_role_detail

指定されたロールIDの詳細情報を取得します。

**パラメータ:**
- `role_id` (required): ロールID

**レスポンス:**
- ロールの完全な詳細情報（権限一覧を含む）

**使用例:**
```json
{
  "role_id": 5
}
```

### list_redmine_trackers

Redmineのトラッカー一覧を取得します。

**パラメータ:**
- なし

**レスポンス:**
- トラッカー一覧（ID、名前、デフォルトステータス、説明）

**使用例:**
```json
{}
```

### list_redmine_priorities

Redmineのチケット優先度一覧を取得します。

**パラメータ:**
- なし

**レスポンス:**
- 優先度一覧（ID、名前、デフォルトフラグ、有効フラグ）

**使用例:**
```json
{}
```

### list_redmine_issue_statuses

Redmineのチケットステータス一覧を取得します。

**パラメータ:**
- なし

**レスポンス:**
- ステータス一覧（ID、名前、クローズフラグ、デフォルトフラグ）

**使用例:**
```json
{}
```

### create_redmine_issue

新しいRedmineチケットを作成します。

**パラメータ:**
- `project_id` (required): プロジェクトID
- `tracker_id` (required): トラッカーID
- `subject` (required): チケット件名
- `description` (optional): チケット説明
- `status_id` (optional): ステータスID
- `priority_id` (optional): 優先度ID
- `assigned_to_id` (optional): 担当者ID

**レスポンス:**
- 作成されたチケットの情報

**使用例:**
```json
{
  "project_id": 1,
  "tracker_id": 2,
  "subject": "新しい機能の実装",
  "description": "ユーザー管理機能を追加する"
}
```

### update_redmine_issue

既存のRedmineチケットを更新します。

**パラメータ:**
- `issue_id` (required): 更新するチケットID
- `subject` (optional): 新しい件名
- `description` (optional): 新しい説明
- `status_id` (optional): 新しいステータスID
- `priority_id` (optional): 新しい優先度ID
- `assigned_to_id` (optional): 新しい担当者ID
- `notes` (optional): 更新メモ

**レスポンス:**
- 更新成功メッセージ

**使用例:**
```json
{
  "issue_id": 123,
  "status_id": 3,
  "notes": "作業完了"
}
```

### delete_redmine_issue

Redmineチケットを削除します。

**パラメータ:**
- `issue_id` (required): 削除するチケットID

**レスポンス:**
- 削除成功メッセージ

**使用例:**
```json
{
  "issue_id": 123
}
```

## 開発

### 開発モード

```bash
npm run dev
```

### ビルド

```bash
npm run build
```

### クリーンアップ

```bash
npm run clean
```

### テスト

```bash
npm test
```

**テスト内容:**
- **スキーマバリデーション**: 各ツールの入力パラメータ検証
- **AWS SDK統合**: Parameter Store連携のモック検証

**テストファイル:**
- `src/server.test.ts`: 全テストケースを含む統合テストファイル

**テスト対象:**
- `SearchRedmineTicketsSchema`: チケット検索パラメータの検証
- `GetRedmineTicketDetailSchema`: チケットID検証
- `ListRedmineProjectsSchema`: プロジェクト一覧パラメータ検証
- `ListRedmineRolesSchema`: ロール一覧パラメータ検証
- `GetRedmineRoleDetailSchema`: ロールID検証
- AWS SSMClient/GetParameterCommandのモック動作

## 構成

```
030.redmine-mcp-server/
├── README.md             # このファイル
├── package.json          # NPM設定
├── tsconfig.json         # TypeScript設定
├── .env.example          # 環境変数テンプレート
├── .gitignore           # Git除外設定
└── src/
    ├── index.ts          # メインサーバーファイル
    ├── types.ts          # Redmine API型定義
    └── schemas.ts        # Zod入力スキーマ
```

## エラーハンドリング

- AWS Parameter Store接続エラー
- Redmine API認証エラー
- 不正な入力パラメータ
- ネットワークエラー

すべてのエラーは適切にキャッチされ、わかりやすいエラーメッセージとして返されます。

## セキュリティ

- APIキーはAWS Parameter Storeで暗号化して保存
- 環境変数による設定管理
- 入力パラメータのバリデーション
- HTTPS通信の使用