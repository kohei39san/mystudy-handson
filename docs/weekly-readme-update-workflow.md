# 週次README更新ワークフロー

このドキュメントでは、リポジトリ内のREADME.mdファイルを週次で自動更新するためのGitHub Actionsワークフローについて説明します。

## 概要

このワークフローは、毎週月曜日に自動的に実行され、リポジトリ内のREADME.mdファイルを最新の状態に保つためのIssueを作成します。作成されたIssueには「Amazon Q development agent」ラベルが付与され、Amazon Q開発エージェントが自動的に対応します。

## 仕組み

1. 毎週月曜日の午前9時（UTC）に自動実行されます
2. リポジトリ変数に設定されたプロンプトを使用してIssueを作成します
3. 作成されたIssueに「Amazon Q development agent」ラベルを付与します
4. Amazon Q開発エージェントがIssueに対応し、必要なREADME.mdの更新を行います

## セットアップ方法

### 1. リポジトリ変数の設定

1. GitHubリポジトリの「Settings」タブに移動します
2. 左側のメニューから「Secrets and variables」→「Variables」を選択します
3. 「New repository variable」ボタンをクリックします
4. 以下の情報を入力します：
   - Name: `README_UPDATE_PROMPT`
   - Value: 
   ```
   リポジトリにあるREADME.mdをリストアップしてください。
   それぞれのREADME.mdには同一ディレクトリで定義されたリソース構成の説明が書かれています。
   同一ディレクトリのリソース構成を読み取り、それぞれのREADME.mdと内容が異なっていた場合、README.mdを修正してください。
   README.mdへの記載は基本的に日本語でお願いします。
   ```
5. 「Add variable」ボタンをクリックして保存します

### 2. Amazon Q開発エージェントの設定

リポジトリにAmazon Q開発エージェントが正しく設定されていることを確認してください。設定方法については、AWSのドキュメントを参照してください。

## 手動実行方法

ワークフローは週次で自動実行されますが、必要に応じて手動で実行することもできます：

1. GitHubリポジトリの「Actions」タブに移動します
2. 左側のワークフローリストから「Weekly README Update」を選択します
3. 「Run workflow」ボタンをクリックします
4. 「Run workflow」ボタンをクリックして実行を開始します

## トラブルシューティング

### Issueが作成されない場合

1. GitHub Actionsのログを確認して、エラーメッセージを確認します
2. リポジトリの権限設定が正しいことを確認します（`issues: write`権限が必要です）
3. リポジトリ変数`README_UPDATE_PROMPT`が正しく設定されているか確認します

### Amazon Q開発エージェントが応答しない場合

1. Issueに「Amazon Q development agent」ラベルが正しく付与されているか確認します
2. Amazon Q開発エージェントの設定が正しいことを確認します
3. Amazon Q開発エージェントのログを確認して、エラーがないか確認します

## カスタマイズ

### 実行スケジュールの変更

ワークフローファイル（`.github/workflows/weekly-readme-update.yml`）内の`cron`式を変更することで、実行スケジュールをカスタマイズできます：

```yaml
on:
  schedule:
    # 現在の設定: 毎週月曜日の午前9時（UTC）
    - cron: '0 9 * * 1'
```

cron式の形式は `分 時 日 月 曜日` です。例えば、毎週水曜日の午後3時（UTC）に実行する場合は `0 15 * * 3` となります。

### プロンプトの変更

プロンプトを変更する場合は、リポジトリ変数`README_UPDATE_PROMPT`の値を更新してください。