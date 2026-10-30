# Lambda Layer 実行手順

## 概要

このプロジェクトは、AWS Lambda Layer を使用して pydantic と psycopg2-binary ライブラリを Python 3.13 Lambda 関数で利用できるようにするテスト環境を構築します。

## リソース構成

![Architecture Diagram](src/architecture.svg)

### AWSリソース
- **S3バケット**: Lambda Layer の ZIP ファイルを格納
- **Lambda Layer** (`pydantic-psycopg2-layer`): pydantic および psycopg2-binary を含む Python 3.13 対応レイヤー
- **Lambda関数** (`layer-test-function`): Lambda Layer を使用してライブラリ動作を検証するテスト関数（Python 3.13、タイムアウト30秒）
- **CloudWatch Logs**: Lambda関数のログ出力先（ログ保持期間: 7日）
- **IAMロール**: Lambda 実行に必要な権限（`AWSLambdaBasicExecutionRole` および CloudWatch Logs 書き込み権限）

### デプロイ方式
- **CloudFormation** (`cfn/cloudformation-template.yaml`): S3バケット上の Layer ZIP を参照してリソースをデプロイ
- **PowerShell スクリプト** (`scripts/deploy-complete.ps1`): Docker でレイヤーを作成し S3 アップロード → CloudFormation デプロイ → テスト実行まで自動化

---

## 📋 必要な準備
1. Docker Desktop を起動
2. AWS CLI プロファイル `default` が設定済み
3. PowerShell実行ポリシーが適切に設定済み

## 🚀 ワンコマンド実行
```powershell
.\deploy-complete.ps1
```

## 📝 実行内容
このスクリプトは以下を自動実行します：

1. **Dockerでレイヤー作成** - Linux互換バイナリを生成
2. **S3アップロード** - レイヤーファイルをS3に保存
3. **CloudFormation** - AWS リソースをデプロイ
4. **レイヤー発行** - 新しいバージョンを作成
5. **Lambda更新** - 関数に最新レイヤーを適用
6. **動作テスト** - pydantic/psycopg2の機能確認

## 📊 成功時の出力例
```
=== Test Results ===
Overall Status: PASS
Python Version: 3.13.9 (main, Dec  4 2025, 17:56:55)

Library Versions:
  pydantic: 2.12.4
  psycopg2: 2.9.11 (dt dec pq3 ext lo64)

Test Results:
  pydantic: PASS
  psycopg2: PASS
  integration: PASS

🎉 All tests passed! Lambda Layer deployment successful!
```

## ⚙️ カスタマイズ実行
```powershell
# 異なるプロファイルやスタック名を使用
.\deploy-complete.ps1 -Profile "my-profile" -StackName "my-stack" -BucketName "my-bucket"
```

## 📁 現在の構成
- `scripts/create_layer_docker.ps1` - レイヤー作成スクリプト
- `scripts/lambda_function.py` - テスト用Lambda関数
- `scripts/deploy-complete.ps1` - **完全自動化スクリプト** ⭐
- `cfn/cloudformation-template.yaml` - AWSリソース定義