# AWS Step Functions ネストされたステートマシン学習

## 概要

このプロジェクトは、AWS Step Functions のネストされたステートマシンの実装方法と、親子間でのデータの受け渡し方法を学習するためのものです。親ステートマシンが子ステートマシンを呼び出し、子ステートマシン内で実行されたLambda関数の出力を親ステートマシンで受け取る構成を実装しています。

## アーキテクチャ

```
[実行開始]
    ↓
[親ステートマシン]
    ↓
[親Lambda関数 (前処理)]
    ↓
[子ステートマシンの呼び出し (同期)]
    ↓
[子ステートマシン]
    ↓
[子Lambda関数 (データ処理)]
    ↓ (出力を返却)
[親ステートマシン]
    ↓
[親Lambda関数 (後処理)]
    ↓
[最終結果の出力]
```

## 構成要素

### ステートマシン

#### 親ステートマシン (parent_state_machine.json)
1. **ParentLambdaPreProcess**: 親Lambda関数で入力データの前処理を実行
2. **InvokeChildStateMachine**: 子ステートマシンを同期的に呼び出し
   - `states:startExecution.sync:2` を使用して同期実行
   - 子ステートマシンの完了を待機
3. **ParentLambdaPostProcess**: 子ステートマシンの出力を受け取り、親Lambda関数で後処理を実行

#### 子ステートマシン (child_state_machine.json)
1. **ChildLambdaTask**: 子Lambda関数でデータ処理を実行
   - 入力値を受け取り、指定された処理を実行
   - 結果を親ステートマシンに返却

### Lambda関数

#### 親Lambda関数 (parent_lambda.py)
- **前処理 (preprocess)**: 
  - 入力データを検証・整形
  - 子ステートマシンへの入力を準備
- **後処理 (postprocess)**:
  - 子ステートマシンの出力を受け取り
  - 最終結果をまとめて返却

#### 子Lambda関数 (child_lambda.py)
- 入力値に対して指定された演算を実行:
  - `multiply`: 値を2倍にする
  - `add`: 値に10を加算する
  - `square`: 値を2乗する

### データフロー

```json
入力例:
{
  "initial_value": 10,
  "processing_type": "multiply"
}

親Lambda前処理の出力:
{
  "statusCode": 200,
  "value": 10,
  "processing_type": "multiply",
  "timestamp": "...",
  "message": "Parent Lambda: Pre-processed with value 10 and type multiply"
}

子Lambdaの出力:
{
  "statusCode": 200,
  "processed_value": 20,
  "original_value": 10,
  "operation": "multiplied by 2",
  "processing_type": "multiply",
  "message": "Child Lambda: multiplied by 2 to get 20"
}

親Lambda後処理の出力 (最終結果):
{
  "statusCode": 200,
  "final_value": 20,
  "original_value": 10,
  "operation_performed": "multiplied by 2",
  "child_output": {...},
  "message": "Parent Lambda: Post-processed result - original: 10, final: 20",
  "summary": "Complete processing chain: 10 -> multiplied by 2 -> 20"
}
```

## クイックスタート

### 前提条件
- AWS CLI が設定済み
- Terraform 1.0以上がインストール済み (Terraformを使用する場合)
- Python 3.x がインストール済み (テストスクリプト実行用)
- 適切なAWS権限を持つIAMユーザーまたはロール

### デプロイ方法

#### 方法1: Terraform を使用

```bash
cd 039.step-functions-nested-state-machine

# Terraformの初期化
terraform init

# デプロイ内容の確認
terraform plan

# デプロイの実行
terraform apply

# 出力の確認
terraform output
```

#### 方法2: CloudFormation を使用

```bash
cd 039.step-functions-nested-state-machine

# CloudFormationスタックのデプロイ
aws cloudformation create-stack \
  --stack-name nested-sfn-study-dev \
  --template-body file://cfn/infrastructure.yaml \
  --capabilities CAPABILITY_NAMED_IAM \
  --region ap-northeast-1

# デプロイ完了を待機
aws cloudformation wait stack-create-complete \
  --stack-name nested-sfn-study-dev \
  --region ap-northeast-1

# 出力の確認
aws cloudformation describe-stacks \
  --stack-name nested-sfn-study-dev \
  --region ap-northeast-1 \
  --query 'Stacks[0].Outputs'
```

#### 方法3: デプロイスクリプトを使用

```bash
cd 039.step-functions-nested-state-machine
./scripts/deploy.sh
```

## テスト方法

### 方法1: テストスクリプトを使用

```bash
# ステートマシン名を指定して実行
python scripts/test_execution.py \
  --state-machine-name nested-sfn-study-dev-parent-sfn \
  --initial-value 10 \
  --processing-type multiply

# ARNを直接指定して実行
python scripts/test_execution.py \
  --state-machine-arn arn:aws:states:ap-northeast-1:ACCOUNT_ID:stateMachine:nested-sfn-study-dev-parent-sfn \
  --initial-value 15 \
  --processing-type square
```

### 方法2: AWS CLI を使用

```bash
# ステートマシンの実行
aws stepfunctions start-execution \
  --state-machine-arn <PARENT_STATE_MACHINE_ARN> \
  --input '{"initial_value": 10, "processing_type": "multiply"}' \
  --region ap-northeast-1

# 実行状態の確認
aws stepfunctions describe-execution \
  --execution-arn <EXECUTION_ARN> \
  --region ap-northeast-1
```

### 処理タイプのバリエーション

```bash
# 値を2倍にする
python scripts/test_execution.py \
  --state-machine-name nested-sfn-study-dev-parent-sfn \
  --initial-value 10 \
  --processing-type multiply
# 期待される結果: 20

# 値に10を加算する
python scripts/test_execution.py \
  --state-machine-name nested-sfn-study-dev-parent-sfn \
  --initial-value 5 \
  --processing-type add
# 期待される結果: 15

# 値を2乗する
python scripts/test_execution.py \
  --state-machine-name nested-sfn-study-dev-parent-sfn \
  --initial-value 7 \
  --processing-type square
# 期待される結果: 49
```

## ASLファイルの重要ポイント

### 子ステートマシンの同期呼び出し

```json
{
  "Type": "Task",
  "Resource": "arn:aws:states:::states:startExecution.sync:2",
  "Parameters": {
    "StateMachineArn": "${child_state_machine_arn}",
    "Input": {
      "input_value.$": "$.preprocess_result.preprocessed_data.value",
      "processing_type.$": "$.preprocess_result.preprocessed_data.processing_type"
    }
  }
}
```

- `states:startExecution.sync:2` を使用することで、子ステートマシンの完了を待機
- `.sync:2` は、子ステートマシンの出力を直接取得できる形式

### データの受け渡し

```json
{
  "ResultSelector": {
    "child_output.$": "$.Output"
  },
  "ResultPath": "$.child_result"
}
```

- `ResultSelector`: 子ステートマシンの出力を選択
- `ResultPath`: 親ステートマシンの状態に出力を保存する場所を指定

### Lambda関数への入力設定

```json
{
  "Type": "Task",
  "Resource": "arn:aws:states:::lambda:invoke",
  "Parameters": {
    "FunctionName": "${lambda_function_arn}",
    "Payload": {
      "action": "preprocess",
      "data.$": "$"
    }
  }
}
```

- `Parameters.Payload`: Lambda関数に渡す入力データを定義
- `.$` 記法: JSONPathを使用して動的な値を参照

## ファイル構成

```
039.step-functions-nested-state-machine/
├── README.md                          # このファイル
├── provider.tf                        # AWSプロバイダー設定
├── variables.tf                       # 変数定義
├── main.tf                            # メインのTerraform設定
├── outputs.tf                         # 出力定義
├── asl/                               # ASL (Amazon States Language) ファイル
│   ├── parent_state_machine.json     # 親ステートマシン定義
│   └── child_state_machine.json      # 子ステートマシン定義
├── cfn/                               # CloudFormation テンプレート
│   └── infrastructure.yaml           # インフラストラクチャ定義
├── src/                               # Lambda関数ソースコード
│   ├── parent_lambda.py              # 親Lambda関数
│   └── child_lambda.py               # 子Lambda関数
└── scripts/                           # デプロイ・テストスクリプト
    ├── deploy.sh                     # デプロイスクリプト
    └── test_execution.py             # テスト実行スクリプト
```

## ログの確認

### Lambda関数のログ

```bash
# 親Lambda関数のログ
aws logs tail /aws/lambda/nested-sfn-study-dev-parent-lambda --follow

# 子Lambda関数のログ
aws logs tail /aws/lambda/nested-sfn-study-dev-child-lambda --follow
```

### Step Functionsのログ

```bash
# 親ステートマシンのログ
aws logs tail /aws/vendedlogs/states/nested-sfn-study-dev-parent-sfn --follow

# 子ステートマシンのログ
aws logs tail /aws/vendedlogs/states/nested-sfn-study-dev-child-sfn --follow
```

## トラブルシューティング

### 子ステートマシンが呼び出せない

**原因**: IAMロールに必要な権限がない

**解決策**: Step FunctionsのIAMロールに以下の権限が付与されていることを確認
- `states:StartExecution`
- `states:DescribeExecution`
- `states:StopExecution`

### データが正しく渡されない

**原因**: JSONPathの記法が正しくない

**解決策**: ASLファイルの `Parameters` セクションで、`.$` 記法を使用して正しくパスを指定

### タイムアウトが発生する

**原因**: Lambda関数の処理時間が長すぎる、またはStep Functionsのタイムアウト設定が短い

**解決策**: 
- Lambda関数のタイムアウト設定を延長
- ステートマシンのタイムアウト設定を確認

## リソースの削除

### Terraform を使用した場合

```bash
terraform destroy
```

### CloudFormation を使用した場合

```bash
aws cloudformation delete-stack \
  --stack-name nested-sfn-study-dev \
  --region ap-northeast-1
```

## 技術仕様

- **リージョン**: ap-northeast-1 (東京)
- **Terraform**: >= 1.0
- **AWS Provider**: ~> 5.0
- **Lambda Runtime**: Python 3.11
- **Step Functions Type**: STANDARD
- **ログ保持期間**: 7日

## 学習ポイント

1. **ネストされたステートマシンの実装方法**
   - 同期実行 (`sync:2`) と非同期実行の違い
   - 子ステートマシンの出力の受け取り方

2. **ASLファイルでのデータの受け渡し**
   - `Parameters` での入力の指定
   - `ResultSelector` での出力の選択
   - `ResultPath` での状態の保存

3. **Lambda関数の統合**
   - `lambda:invoke` リソースの使用
   - Payload の設定方法

4. **IAM権限の設定**
   - Lambda実行ロールの設定
   - Step Functions実行ロールの設定
   - クロスサービス権限の設定

## セキュリティ

- **最小権限の原則**: IAMロールには必要最小限の権限のみを付与
- **ログの暗号化**: CloudWatch Logsは AWS管理のキーで暗号化
- **実行履歴**: すべての実行がCloudWatch Logsに記録

## 参考資料

- [AWS Step Functions デベロッパーガイド](https://docs.aws.amazon.com/step-functions/latest/dg/)
- [Amazon States Language 仕様](https://states-language.net/spec.html)
- [Step Functions から Step Functions を実行する](https://docs.aws.amazon.com/step-functions/latest/dg/connect-stepfunctions.html)

## ライセンス

このプロジェクトはMITライセンスの下で公開されています。
