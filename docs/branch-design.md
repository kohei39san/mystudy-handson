# Branch Design

## ブランチ戦略（AIエージェント編集時の標準）

- 作業は必ずトピックブランチで行うこと
- 直接 `main` ブランチへコミットしないこと

## ブランチ命名規則

- `feature/<ディレクトリ番号>-<要約>`: 新機能追加
- `fix/<ディレクトリ番号>-<要約>`: 不具合修正
- `chore/<ディレクトリ番号>-<要約>`: 設定変更、依存更新、保守作業
- `docs/<ディレクトリ番号>-<要約>`: ドキュメント更新

## 例

- `feature/034-redmine-mcp-server-timeentry-filter`
- `chore/034-update-dependencies`
- `docs/034-update-setup-guide`

## PR運用ルール

- PRタイトルは `type(scope): summary` 形式を推奨
	- 例: `fix(034): correct time entry filter handling`
- 1つのPRには目的が近い変更のみを含めること
- 破壊的変更（ディレクトリ移動、ファイル削除、大規模リネーム）はPR本文に明記すること

## PRラベル

- PRには以下のラベルを必要に応じて付与すること
	- `feature`: 機能追加
	- `fix`: 修正（仕様調整・軽微な不具合修正を含む）
	- `bug`: バグ修正（再現可能な不具合の修正）
