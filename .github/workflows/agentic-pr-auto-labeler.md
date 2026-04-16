---
on:
  pull_request:
    types: [closed]

if: github.event.pull_request.merged == true && github.event.pull_request.user.login != 'dependabot[bot]'

concurrency:
  group: agentic-workflows
  cancel-in-progress: false

engine: copilot

checkout:
  ref: main

permissions:
  contents: read
  pull-requests: read
  issues: read

# Agentic workflow runs with constrained tools and explicit safe outputs.
# Keep write operations limited and reviewable.
safe-outputs:
  add-labels:
    max: 2
    allowed: [ feature, fix, bug, major, minor, patch ]
  add-comment:
    max: 1

tools:
  github:
    min-integrity: merged
    mode: remote
    toolsets:
      - pull_requests
      - repos
      - issues
      - labels
---
# Agentic PR Auto Labeler

目的:
- Pull Request の文脈を分析し、最も適切なラベルを自動で付与する。
- 対象 Pull Request: #${{ github.event.pull_request.number }}

リポジトリポリシー:
- `safe-outputs.add-labels.allowed` に定義されたラベルのみを追加する。
- 影響範囲カテゴリから最大1つ、バージョンカテゴリから最大1つを付与する（合計最大2ラベル）。
- 例外として、dependabot の PR ではバージョンカテゴリのラベルのみを付与する（影響範囲カテゴリは付与しない）。
- 再現率より適合率を優先する。
- 新しいラベルは作成しない。
- すでにカテゴリ内の管理対象ラベルが付与されている場合、そのカテゴリには新規ラベルを追加しない。
- ラベル適用後、選定理由を日本語で Pull Request にコメントする。

ラベルカテゴリ:

影響範囲 (Impact scope) - 最大1つ選択:
- `feature`: 新しい機能や能力の追加。
- `fix`: 仕様調整や軽微な不具合修正を含む、是正のための変更。
- `bug`: ユーザー影響があり再現可能な不具合の修正。

バージョン (Version) - 最大1つ選択:
- `major`: 互換性を壊す破壊的変更。
- `minor`: 後方互換を保った新機能追加。
- `patch`: 後方互換を保った不具合修正。

Dependabot ルール:
- PR 作成者が `dependabot[bot]` の場合、バージョンカテゴリ（major / minor / patch）のみを付与する。影響範囲カテゴリ（feature / fix / bug）は付与しない。

判定ルール:
1. まず PR タイトルと本文を確認し、その後に変更ファイルパスと差分サマリーを参照する。
2. 現在の PR ラベルを読み取り、管理対象セット `feature`, `fix`, `bug`, `major`, `minor`, `patch` に含まれる既存ラベルを特定する。
3. PR 作成者が `dependabot[bot]` の場合、影響範囲カテゴリの選定は行わず、バージョンカテゴリから最大1つのみ選定する。
4. それ以外の場合は、影響範囲カテゴリ（feature / fix / bug）から最大1つ選定する。
5. バージョンカテゴリ（major / minor / patch）から最大1つ選定する。
6. 影響範囲カテゴリに既存の管理対象ラベルがある場合、影響範囲カテゴリへの追加は行わない。
7. バージョンカテゴリに既存の管理対象ラベルがある場合、バージョンカテゴリへの追加は行わない。
8. 確信度が低い場合は、ラベル追加を行わない。

実行手順:
1. PR メタデータ（番号、タイトル、本文、作成者、base/head）を取得する。
2. PR に現在付与されているラベルを取得する。
3. PR 作成者が `dependabot[bot]` の場合は手順6へ進む（バージョンラベル選定のみ）。
4. 変更ファイル一覧を取得し、パッチサマリーを確認して意図を推定する。
5. 影響範囲カテゴリから許可リスト内のラベルを最大1つ選定する（dependabot PR ではこの手順をスキップする）。
6. バージョンカテゴリから許可リスト内のラベルを最大1つ選定する。
7. 各カテゴリで既存の管理対象ラベルがある場合、そのカテゴリの `labels_to_add` には何も入れない。
8. ラベル追加の safe output を出力する。
9. どのラベルを追加したか（または追加しなかったか）とその理由を日本語で PR コメントとして投稿する。

出力契約:
- 厳密に JSON 互換の構造で返すこと:
  - labels_to_add: string[]
  - reason: string（日本語。PR コメントとして投稿）
- `labels_to_add` は `safe-outputs.add-labels.allowed` に含まれるラベルのみとする。
- 各カテゴリで最大1ラベルとする。
- dependabot PR の場合、`labels_to_add` はバージョンカテゴリのラベルのみを含める。

失敗時の扱い:
- 確信度が低い場合はラベル追加を行わない。
- 許可リスト外のラベルは絶対に操作しない。
