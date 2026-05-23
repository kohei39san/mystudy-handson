---
name: create-pull-request
description: GitHubで「現在のファイル変更をすべて含めて」ブランチ作成、プッシュ、PR作成を行う手順です。キーワード: PR作成, プルリクエスト, ブランチ作成, push, create_pull_request, github-mcp-server
---

# Create GitHub Pull Request Skill

このスキルは、ローカルGit操作と `github-mcp-server` の `create_pull_request` を使って、現在のローカル変更をすべて含めたブランチ作成からPR作成までを完了するための運用ルールです。

## 前提条件

- GitHub MCPサーバ (`github-mcp-server`) が利用可能であること
- 対象リポジトリでGit操作 (branch / commit / push) が可能であること
- 対象リポジトリの `origin` がGitHubリポジトリを指していること

## 入力

- `title`: PRタイトル (基本はエージェントが提案し、ユーザーが必要に応じて修正)
- `base`: ベースブランチ (未指定時は `main`)
- `body`: PR本文 (基本はエージェントが提案し、ユーザーが必要に応じて修正)
- `draft`: ドラフトPRかどうか (未指定時は `true`)
- `labels`: PRラベル (未指定時は必要に応じてエージェントが提案)

## 基本方針

- PR作成は `github-mcp-server` の `create_pull_request` を優先して実行する
- 現在のファイル変更はデフォルトで全件対象とし、`git add -A` を使用してステージする
- ブランチ未作成時は新規ブランチを作成し、そのブランチへコミット・プッシュする
- ブランチ名は `../../../docs/branch-design.md` のブランチ命名規則を参照する
- PRラベルは `../../../docs/branch-design.md` のPRラベルを参照する
- ユーザー入力として `base` (ベースブランチ) を受け付け、未指定時は `main` をデフォルトにする
- ローカルでURLだけ案内して終わらず、可能な限りMCPツールでPR作成まで完了する
- `owner` と `repo` は推測で進めず、まずコマンド実行結果から特定する

## 実行手順

1. リポジトリとブランチ情報を確認する
  - 例: `git remote get-url origin`
  - 例: `git branch --show-current`
  - `owner` と `repo` を remote URL から抽出する
  - `base` はユーザー入力値を優先し、未指定時は `main` を使用する
2. 変更ブランチを準備する
  - 現在ブランチをそのまま使わない場合は新規ブランチを作成する
  - ブランチ名は `../../../docs/branch-design.md` の命名規則に従う
  - 例: `git switch -c <feature-branch>`
3. 現在のファイル変更をすべてステージする
  - 例: `git add -A`
  - 意図しない変更が混ざっていないか `git status --short` で確認する
4. コミットを作成する
  - 例: `git commit -m "<commit message>"`
5. リモートへプッシュする
  - 例: `git push -u origin <feature-branch>`
6. PR作成に必要な情報を最終確認する
   - `owner`
   - `repo`
   - `head` (変更ブランチ)
  - `base` (マージ先ブランチ。ユーザー入力、未指定時は `main`)
  - `title` (基本はエージェント提案)
  - `body` (基本はエージェント提案)
  - `draft` (未指定時は `true`)
  - `labels` (`../../../docs/branch-design.md` のPRラベルを参照)
7. 情報が不足している場合は、最小限の確認質問を行う
  - コマンドから一意に判定できない場合のみ、ユーザーに確認する
8. `create_pull_request` を呼び出してPRを作成する
9. 返却されたPR番号/URLをユーザーへ共有する

## ツール呼び出し例

- `mcp_io_github_git_create_pull_request`
  - `owner`: リポジトリオーナー
  - `repo`: リポジトリ名
  - `head`: 変更元ブランチ
  - `base`: マージ先ブランチ
  - `title`: PRタイトル (基本はエージェント提案)
  - `body`: PR本文 (基本はエージェント提案)
  - `draft`: ドラフトPRかどうか (未指定時は `true`)

## ローカルGitコマンド例

```bash
git remote get-url origin
git switch -c <feature-branch>
git add -A
git commit -m "<commit message>"
git push -u origin <feature-branch>
```

## 補足

- ユーザーが「CopilotにPR作成を委譲したい」と明示した場合のみ、`create_pull_request_with_copilot` の利用を検討する
- 通常のPR作成依頼では `create_pull_request` を第一選択とする
- 既存の未コミット変更を保持したいという指示がある場合は、`git add -A` の前に必ず方針を確認する