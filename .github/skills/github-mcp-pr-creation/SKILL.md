---
name: github-mcp-pr-creation
description: GitHubでプルリクエストを作成する依頼時に、github-mcp-serverのcreate_pull_requestを使ってPRを作成するための手順です。キーワード: PR作成, プルリクエスト, create_pull_request, github-mcp-server
---

# GitHub MCP PR Creation Skill

このスキルは、ユーザーからプルリクエスト作成の依頼を受けたときに、`github-mcp-server` の `create_pull_request` を利用してPRを作成するための運用ルールです。

## 基本方針

- PR作成は `github-mcp-server` の `create_pull_request` を優先して実行する
- ローカルでURLだけ案内して終わらず、可能な限りMCPツールでPR作成まで完了する
- `owner` と `repo` は推測で進めず、まずコマンド実行結果から特定する

## 実行手順

1. PR作成に必要な情報を確認する
   - `owner`
   - `repo`
   - `head` (変更ブランチ)
   - `base` (マージ先ブランチ)
   - `title`
   - `body` (任意)
   - `draft` (任意)
2. `owner` と `repo` をコマンドで確認する
  - 例: `git remote get-url origin`
  - HTTPS形式 (`https://github.com/<owner>/<repo>.git`) またはSSH形式 (`git@github.com:<owner>/<repo>.git`) から抽出する
3. 情報が不足している場合は、最小限の確認質問を行う
  - コマンドから一意に判定できない場合のみ、ユーザーに確認する
4. `create_pull_request` を呼び出してPRを作成する
5. 返却されたPR番号/URLをユーザーへ共有する

## ツール呼び出し例

- `mcp_io_github_git_create_pull_request`
  - `owner`: リポジトリオーナー
  - `repo`: リポジトリ名
  - `head`: 変更元ブランチ
  - `base`: マージ先ブランチ
  - `title`: PRタイトル
  - `body`: PR本文 (必要に応じて設定)
  - `draft`: ドラフトPRかどうか (必要に応じて設定)

## 補足

- ユーザーが「CopilotにPR作成を委譲したい」と明示した場合のみ、`create_pull_request_with_copilot` の利用を検討する
- 通常のPR作成依頼では `create_pull_request` を第一選択とする