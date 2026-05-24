# Directory Structure

## ディレクトリの命名規則

- リポジトリ直下のディレクトリは機能ごとに、`[番号].[サービス名]-[用途]`の命名とする
  - 例: `014.vpc-web-app`
- リポジトリ直下のscripts,srcは各機能で共通的なファイルを格納している

## リポジトリ直下の共通・運用ディレクトリ

- `docs`: 共通ドキュメント
- `scripts`: 共通スクリプト
- `src`: 共通ソース
- `wsl-old`: 旧環境向けの保管ディレクトリ（レガシー）

## ツール・生成物ディレクトリ

- `.github`, `.vscode`, `.devcontainer`, `.amazonq`, `.pytest_cache`: ツール設定
- `node_modules`, `htmlcov`: 生成物

## リポジトリ直下の主要ファイル

- `README.md`: リポジトリ全体の概要と利用手順
- `package.json`, `package-lock.json`: Node.js依存関係とスクリプト定義
- `requirements.txt`: Python依存関係定義
- `tsconfig.base.json`: TypeScript共通設定
- `ansible.cfg`: Ansible実行設定
- `coverage.xml`: テストカバレッジ出力
- `.gitignore`: Git管理除外設定
- `.gitattributes`: Git属性設定
- `.gitmodules`: Gitサブモジュール設定

## 機能ごとのディレクトリのファイル構成

- README.mdファイルに構成の説明をしている

### CloudFormationファイル構成

- 機能ディレクトリ/cfnディレクトリ内にテンプレートファイルを作成すること

### Azure ARMテンプレートファイル構成

- 機能ディレクトリ/armディレクトリ内にARMテンプレートファイルを作成すること

### Ansibleファイル構成

- 機能ディレクトリ/ansibleディレクトリ内にPlaybookファイルを作成すること

### スクリプトファイル構成

- 機能ディレクトリ/scriptsディレクトリ内にスクリプトファイル（shファイル、pythonファイルなど）を作成すること
- テストファイルは機能ディレクトリ/testsディレクトリに格納すること
  - Pythonファイルの場合はpytest.iniファイルを作成し、pytestからテストできるようにすること

### OpenAPI定義ファイル

- 機能ディレクトリ/openapiディレクトリ内にOpenAPI定義ファイル（ymlファイル）を作成すること

### ドキュメントファイル構成

- 機能固有のドキュメントは機能ディレクトリ/docsディレクトリに格納してよい
- 構成図（drawioファイル、svgファイルなど）も機能ディレクトリ/docsディレクトリに格納すること
