---
name: create-github-pull-request
description: GitHubでPull Requestを作成する際の標準手順とチェック項目を定義します。ブランチ作成、差分整理、PR本文作成、レビュー依頼時に利用してください。
---

# Create GitHub Pull Request

## 目的

このスキルは、`mystudy-handson` リポジトリでPull Request (PR) を作成する際の手順と品質基準を統一するためのガイドラインです。

## 前提ルール

- `main` ブランチへ直接コミットしない
- 作業は必ずトピックブランチで行う
- ブランチ名は以下を基本とする
	- `feature/<ディレクトリ番号>-<要約>`
	- `fix/<ディレクトリ番号>-<要約>`

## PR作成手順

1. 最新の `main` からブランチを作成する

```bash
git remote -v
git switch main
git pull origin main
git switch -c <branch-name>
```

2. 変更を実装し、差分を確認する

```bash
git status
git diff
```

3. 変更目的ごとにコミットを整理する

```bash
git add <files>
git commit -m "<type>(<scope>): <summary>"
```

4. リモートへプッシュする

```bash
git push -u origin <branch-name>
```

5. GitHubでPRを作成する
	- Base: `main`
	- Compare: `<branch-name>`

## PRタイトル規約

- `type(scope): summary` を推奨
- 例
	- `feat(031): add PostgreSQL bootstrap script`
	- `fix(034): correct Redmine issue status mapping`
	- `docs(015): update EKS setup notes`

## PR本文テンプレート

以下の項目を最低限記載すること。

```markdown
## 概要
- 何を変更したか
- なぜ変更したか

## 変更内容
- 主要な変更点1
- 主要な変更点2

## 影響範囲
- 影響を受けるディレクトリ/機能
- 破壊的変更の有無

## 動作確認
- 実施した確認内容
- 未実施の場合は理由

```

## レビュー前チェック

- 1つのPRに目的が近い変更のみ含まれている
- 不要な差分（整形だけの変更、デバッグコードなど）がない
- 機密情報（鍵、トークン、認証情報）を含んでいない
- `README.md` など関連ドキュメントが必要に応じて更新されている
- 破壊的変更（ファイル削除・大規模リネーム等）がある場合はPR本文に明記している

## ラベル運用

PRには必要に応じて以下ラベルを付与する。

- `feature`: 機能追加
- `fix`: 修正（仕様調整・軽微な不具合修正を含む）
- `bug`: 再現可能な不具合修正

## 注意点

- 既存の未マージブランチがある場合は、同一PRで混在させない
- レビューコメント対応時は、何をどう直したかをPRコメントで明確にする
- 大きな変更は早めにDraft PRを作成して方向性レビューを依頼する
