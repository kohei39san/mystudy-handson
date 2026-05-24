---
name: unit-test-spec
description: '単体テストの仕様書・テストケースを作成する。キーワード: 単体テスト仕様書, テストケース作成, unit test specification, test spec, テスト仕様, README にテストケースを書く, テスト観点'
---

# Unit Test Specification Skill

## 目的

対象コード（Pythonスクリプト、関数、クラスなど）を解析し、体系的な単体テスト仕様書を生成する。

## いつ使うか

- 新規スクリプト・関数に対してテストケースを洗い出したいとき
- README.md にテストケースのセクションを追加したいとき
- テスト観点（正常系・異常系・境界値）を網羅的に整理したいとき

---

## 手順

### Step 1: 対象コードの把握

対象ファイルを読み込み、以下を特定する。

- **公開関数・メソッド**: テスト対象となる関数/クラスメソッドを列挙
- **入力パラメータ**: 型・制約・必須/任意
- **出力・副作用**: 戻り値の型、ファイル書き込み、例外送出、外部 API 呼び出しなど
- **外部依存**: ファイル I/O、ネットワーク、DB、ブラウザ操作など（モック対象）

### Step 2: テスト観点の洗い出し

各関数について以下の観点でテストケースを導出する。

| 観点 | 内容 |
|------|------|
| **正常系** | 典型的な有効入力で期待通りの出力が得られること |
| **異常系** | 無効入力・不正な状態で適切なエラー/例外が発生すること |
| **境界値** | 最小値・最大値・空・0 などの境界条件 |
| **副作用** | ファイル生成、ログ出力、外部呼び出しが正しく行われること |
| **組み合わせ** | 複数コード・複数ステップのシナリオ |

### Step 3: テストケース表の生成

以下のフォーマットで出力する。

```markdown
### <関数名 / モジュール名>

| # | テストケース | 入力 | 期待結果 |
|---|------------|------|---------|
| T01 | 〇〇が正常に動作する | ～ | ～ |
| T02 | 〇〇が失敗する場合 | ～ | ～ |
```

- テスト ID は `T01`, `T02`, ... の連番
- グループ（正常系・異常系など）はサブセクション（`####`）で区切る
- 外部依存がある場合はモック対象を `> モック: xxx` として明記する

### Step 4: 出力先の決定

| 出力先 | 条件 |
|--------|------|
| `README.md` の `## テストケース` セクション | 既存 README.md がある場合は追記・更新 |
| 新規 `README.md` | README.md がない場合は新規作成 |
| 別ファイル指定 | ユーザーが出力先を明示した場合はそれに従う |

---

## テンプレート

詳細なテーブルフォーマットは [./references/test-case-template.md](./references/test-case-template.md) を参照。

---

## 注意事項

- **ブラウザ・ネットワーク・ファイル I/O を使う関数** はモックが必要なため、テストケース表にモック対象を明記する
- テストケース ID は README.md 内で一意になるよう連番を引き継ぐ
- 実装コードを書くのではなく、仕様書（テストケース表）の生成のみを行う

---

## 単体テスト実行コマンド

### Python (pytest)

```bash
pytest
```

```bash
pytest -q
```

```bash
pytest tests/test_xxx.py -v
```

### npm (Node.js)

```bash
npm test
```

```bash
npm run test
```

```bash
npm run test -- --watch
```

## 単体テスト/結合テストのコマンド分離

### Python (pytest)

- 単体テスト: `pytest -m unit`
- 結合テスト: `pytest -m integration`
- マーカー運用例（`pytest.ini`）

```ini
[pytest]
markers =
	unit: unit tests
	integration: integration tests
```

### npm (Node.js)

- 単体テスト: `npm run test:unit`
- 結合テスト: `npm run test:integration`
- `package.json` の script 名で分離して運用する

## 単体テスト実行に必要なファイル

### Python (pytest)

- `pytest.ini` (必須): pytest の設定（探索パス、マーカー、オプション）
- `tests/test_*.py`: 単体テストファイル
- テスト対象のソースコード（例: `src/`, `scripts/` 配下）
- `.env` / `.env.example` (必要な場合): 実行時に必要な環境変数
- 依存関係定義はルートディレクトリの `requirements.txt` に統合済みのため、必要な場合はルートのファイルを参照する
- `pyproject.toml` は単体テスト実行の必須条件にしない

### npm (Node.js)

- `package.json`: テストスクリプト（`test`）と依存関係定義
- `package-lock.json` または `pnpm-lock.yaml` / `yarn.lock`: 依存固定ファイル
- テストランナー設定ファイル（いずれか）
	- `jest.config.js` / `jest.config.ts`
	- `vitest.config.ts` / `vitest.config.js`
	- `.mocharc.*`
- テストファイル（例: `*.test.js`, `*.spec.ts`, `tests/` 配下）
- テスト対象のソースコード（例: `src/` 配下）
