---
name: repo-description
description: mystudy-handsonリポジトリのファイル・ディレクトリを作成・編集する際の背景知識です
---

# Repository Description Skill

## ディレクトリの命名規則

- リポジトリ直下のディレクトリは機能ごとに、`[番号].[サービス名]-[用途]`の命名とする
  - 例: `014.vpc-web-app`
- リポジトリ直下のscripts,srcは各機能で共通的なファイルを格納している

## 機能ごとのディレクトリのファイル構成

- README.mdファイルに構成の説明をしている

**CloudFormationファイル構成**
- 機能ディレクトリ/cfnディレクトリ内にテンプレートファイルを作成すること

**Ansibleファイル構成**
- 機能ディレクトリ/ansibleディレクトリ内にPlaybookファイルを作成すること

**スクリプトファイル構成**
- 機能ディレクトリ/scriptsディレクトリ内にスクリプトファイル（shファイル、pythonファイルなど）を作成すること
- テストファイルは機能ディレクトリ/testsディレクトリに格納すること
  - Pythonファイルの場合はpytest.iniファイルを作成し、pytestからテストできるようにすること

**OpenAPI定義ファイル**
- 機能ディレクトリ/openapiディレクトリ内にOpenAPI定義ファイル（ymlファイル）を作成すること

## ブランチ戦略（AIエージェント編集時の標準）

- 直接 `main` ブランチへコミットしないこと
- 作業は必ずトピックブランチで行うこと
- ブランチ名は以下の形式を基本とすること
  - `feature/<ディレクトリ番号>-<要約>`: 新機能追加
  - `fix/<ディレクトリ番号>-<要約>`: 不具合修正
  - 例: `feature/034-redmine-mcp-server-timeentry-filter`

### AIエージェントの実行手順

- 編集前に現在のブランチを確認すること
  - `git branch --show-current`
- トピックブランチは必ず最新の `main` から直接作成すること
  - `git switch main`
  - `git pull origin main`
  - `git switch -c <branch-name>`
- 既存トピックブランチで未マージの作業がある場合は、別PRとして継続するか新規ブランチを `main` から作り直すこと

### PR運用ルール

- PRタイトルは `type(scope): summary` 形式を推奨
  - 例: `fix(034): correct time entry filter handling`
- 1つのPRには目的が近い変更のみを含めること
- 破壊的変更（ディレクトリ移動、ファイル削除、大規模リネーム）はPR本文に明記すること

### PRラベル

- PRには以下のラベルを必要に応じて付与すること
  - `feature`: 機能追加
  - `fix`: 修正（仕様調整・軽微な不具合修正を含む）
  - `bug`: バグ修正（再現可能な不具合の修正）