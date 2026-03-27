---
description: Weekly agentic workflow to detect outdated documentation, update files, and open a pull request.
on:
  schedule: weekly
  skip-if-match: 'is:pr is:open in:title "docs: weekly documentation refresh"'
engine: copilot
permissions:
  contents: read
  pull-requests: read
  issues: read
tools:
  github:
    toolsets: [default]
safe-outputs:
  create-pull-request:
    max: 1
---

# Weekly Documentation Refresh

目的:
- リポジトリ内のドキュメントが、実際のコード・設定と乖離していないかを週次で点検する。
- 最新でない内容を見つけた場合に、必要最小限の修正を行い、レビュー可能な Pull Request を作成する。

対象範囲:
- `README.md`（リポジトリ直下）
- 各機能ディレクトリ配下の `README.md`
- `docs/` 配下の markdown ファイル
- 各機能ディレクトリ配下の `src/architecture.drawio`

更新方針:
- 事実ベースで更新する。推測で情報を追加しない。
- 対象ドキュメントに対応する Terraform / CloudFormation / Ansible / scripts / src の実ファイルを確認して差分を判断する。
- まず直近1週間でマージされたPRと主要コミットを確認し、変更が入った機能ディレクトリを優先的に点検する。
- 文章の言語は既存文書の方針に合わせる（既存が日本語中心の場合は日本語で更新）。
- 無関係な整形・大規模リライト・不要な文体変更は避ける。

判定ルール（最新でないとみなす条件）:
1. ドキュメント内のファイル構成・リソース説明が、現行ファイルと一致しない。
2. 手順や設定値の説明が、実装（変数名、リソース名、主要フロー）と明確に矛盾する。
3. 既に削除された構成要素が残っている、または主要な追加要素が説明に欠落している。
4. `src/architecture.drawio` の構成要素名・接続関係が、現行の主要リソース構成と明確に矛盾する。

実行手順:
1. 直近1週間でマージされたPRを検索し、必要に応じてコミット差分も確認して変更点サマリーを作る。
2. 変更点サマリーをもとに、優先点検対象の機能ディレクトリを決める。
3. 対象ドキュメント候補（README / docs配下md / src/architecture.drawio）を列挙する。
4. 各候補について、同一ディレクトリ配下の実ファイル構成と主要設定を確認する。
5. 最新でないと判断したファイルだけを修正する。
6. 変更内容をセルフレビューし、次を満たすことを確認する。
   - 変更は最小限である。
   - 記述は実装と整合している。
   - 機密情報や不確実な情報を追加していない。
7. 変更が1件以上ある場合、`create-pull-request` safe output を使ってPRを作成する。

PR作成ルール:
- タイトルは固定で `docs: weekly documentation refresh` とする。
- 本文には以下を含める。
  - 参照した直近1週間のPR/コミットの要点
  - 更新対象ファイル一覧
  - 各ファイルの更新理由（どこが古く、何に合わせたか）
  - 影響範囲（ドキュメントのみであること）
- ブランチ名の推奨: `fix/docs-weekly-refresh-<YYYYMMDD>`

変更が不要な場合:
- 点検の結果、更新不要であれば `noop` safe output を呼び出し、
  「点検を実施し、更新不要だった」ことを簡潔に記録する。
- 直近1週間に参照したPR/コミットがある場合は、その要点だけを `noop` メッセージにも簡潔に残す。

禁止事項:
- ドキュメント更新と無関係なコード変更をしない。
- 破壊的なファイル削除・移動をしない。
- 直接 main ブランチへコミットする前提で行動しない（PR前提）。