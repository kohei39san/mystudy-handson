# Redmine MCP Server

RedmineのチケットAPIを利用したMCPサーバーの実装

## 概要

このプロジェクトは、RedmineのREST APIを使用してチケットの一覧取得と詳細取得を行うMCPサーバーです。Model Context Protocol (MCP) を使用して、AIアシスタントがRedmineのチケット情報にアクセスできるようにします。

## 機能

- **チケット一覧検索**: Redmineのチケット一覧を検索条件に基づいて取得
- **チケット詳細取得**: 指定されたチケットIDの詳細情報を取得
- **AWS Parameter Store統合**: APIキーの安全な管理
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

- `REDMINE_BASE_URL`: RedmineのベースURL（必須）
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

**使用例:**
```json
{
  "ticket_id": 123
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