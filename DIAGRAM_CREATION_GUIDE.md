# インフラストラクチャ図作成・README更新ガイド

このガイドは、リポジトリ内のインフラストラクチャ図の作成と README.md ファイルの更新方法を説明します。

## 目次

1. [概要](#概要)
2. [図作成の前提条件](#図作成の前提条件)
3. [アーキテクチャ図の作成手順](#アーキテクチャ図の作成手順)
4. [README.md の更新手順](#readmemd-の更新手順)
5. [検証チェックリスト](#検証チェックリスト)
6. [ベストプラクティス](#ベストプラクティス)

## 概要

このリポジトリでは、各インフラストラクチャディレクトリに以下のファイルを配置することが標準となっています：

```
XXX.directory-name/
├── src/
│   ├── architecture.drawio    # Draw.io 形式のアーキテクチャ図（手動作成）
│   └── architecture.svg        # SVG 形式（GitHub Actions で自動生成）
├── README.md                   # 日本語の構成説明書
└── （その他の Terraform/CloudFormation ファイル）
```

## 図作成の前提条件

### 必要なツール

1. **Draw.io Desktop または Web版**
   - Desktop版: [https://github.com/jgraph/drawio-desktop/releases](https://github.com/jgraph/drawio-desktop/releases)
   - Web版: [https://app.diagrams.net/](https://app.diagrams.net/)

2. **テンプレートファイル**
   - AWS構成: `src/aws-template.drawio`
   - OCI構成: `src/oci-template.drawio`

### 重要な注意事項

⚠️ **既存の .drawio ファイルは参照しないこと**

- 他のディレクトリの既存 `.drawio` ファイルは古い可能性があります
- 必ず `src/aws-template.drawio` または `src/oci-template.drawio` をテンプレートとして使用してください
- これらのテンプレートには最新のアイコンセットとレイアウトガイドラインが含まれています

## アーキテクチャ図の作成手順

### ステップ 1: インフラコードの分析

図を作成する前に、対象ディレクトリのインフラコードを確認します：

**Terraform の場合:**
```bash
# ディレクトリ内の .tf ファイルを確認
cd XXX.directory-name
grep -r "resource \"" *.tf
grep -r "module \"" *.tf
```

**CloudFormation の場合:**
```bash
# Resources セクションを確認
grep -A 5 "Resources:" cfn/*.yaml
```

確認すべき主要リソース：
- VPC、サブネット、IGW、NAT Gateway などのネットワークリソース
- EC2、RDS、Lambda などのコンピューティングリソース
- S3、DynamoDB などのストレージリソース
- IAM ロール、セキュリティグループなどのセキュリティリソース
- リソース間の依存関係と接続

### ステップ 2: テンプレートを開く

1. Draw.io でテンプレートファイルを開く：
   - AWS構成の場合: `src/aws-template.drawio`
   - OCI構成の場合: `src/oci-template.drawio`

2. 「名前を付けて保存」で対象ディレクトリに保存：
   ```
   XXX.directory-name/src/architecture.drawio
   ```

### ステップ 3: 図の編集

#### 使用するアイコン

**AWS の場合:**
- AWS 2025 アイコンセットを使用
- Draw.io の「More Shapes」から「AWS 19」または「AWS 2025」を有効化
- サービスカテゴリ別にグループ化（Compute、Database、Storage等）

**OCI の場合:**
- OCI公式アイコンを使用
- テンプレートに含まれるアイコンライブラリを活用

#### レイアウトのベストプラクティス

1. **階層構造を明確に**
   - リージョン → VPC → サブネット → リソース の順で配置
   - 外側から内側へと階層を表現

2. **接続を明示**
   - リソース間の通信経路を矢印で表現
   - セキュリティグループやネットワークACLの境界を点線で表現

3. **ラベルは日本語で**
   - すべてのリソースに日本語の名称を付与
   - CIDR ブロックやポート番号などの技術情報も併記

4. **色の使い分け**
   - パブリックサブネット: 明るい色（水色など）
   - プライベートサブネット: 暗めの色（灰色など）
   - 重要なリソース: 強調色（赤やオレンジ）

### ステップ 4: SVG の自動生成

`.drawio` ファイルを保存してコミット・プッシュすると、GitHub Actions が自動的に `.svg` ファイルを生成します。

```bash
git add XXX.directory-name/src/architecture.drawio
git commit -m "Add architecture diagram for XXX.directory-name"
git push
```

GitHub Actions ワークフロー（`.github/workflows/drawio-to-svg.yml`）が自動実行され、SVG ファイルが生成されます。

## README.md の更新手順

### ステップ 1: 既存の README.md を確認

他のディレクトリの README.md を参考にします：
```bash
# 良い例を確認
cat 001.ec2-ec2-ec2/README.md
cat 011.cfn-project/README.md
cat 028.oci-bucket-tfstate/README.md
```

### ステップ 2: README.md の基本構成

```markdown
# [構成名を日本語で記述]

[この構成の概要を1-2文で説明]

![Architecture Diagram](src/architecture.svg)

## リソース構成

### ネットワークリソース
- **VPC**: [CIDR ブロックと説明]
- **サブネット**: [サブネットの説明]
- ...

### コンピューティングリソース
- **EC2インスタンス**: [インスタンスの説明]
- ...

### その他のリソース
- **IAM ロール**: [ロールの説明]
- ...

## 使用方法

この構成をデプロイするには、メインの README.md に記載されている手順に従ってください。

（追加の手順があれば記載）
```

### ステップ 3: リソース構成の正確な記述

README.md の内容がインフラコードと一致していることを確認：

1. **Terraform の場合:**
   ```bash
   # 実際に作成されるリソースを確認
   terraform plan
   ```

2. **CloudFormation の場合:**
   ```bash
   # テンプレートを検証
   aws cloudformation validate-template --template-body file://cfn/template.yaml
   ```

3. README.md に記載する情報：
   - リソースの種類と数
   - CIDR ブロック、ポート番号などの設定値
   - リソース間の関係性
   - セキュリティ設定（セキュリティグループ、IAM ポリシー等）

## 検証チェックリスト

新しいディレクトリまたは既存ディレクトリを更新する際は、以下を確認してください：

### アーキテクチャ図

- [ ] `src/architecture.drawio` ファイルが存在する
- [ ] テンプレート（`src/aws-template.drawio` または `src/oci-template.drawio`）を基に作成されている
- [ ] すべてのリソースが図に含まれている
- [ ] リソース間の接続が正確に表現されている
- [ ] ラベルがすべて日本語で記述されている
- [ ] AWS 2025 アイコン（または OCI アイコン）を使用している
- [ ] GitHub Actions により `src/architecture.svg` が自動生成されている

### README.md

- [ ] README.md ファイルが存在する
- [ ] 図の参照 `![Architecture Diagram](src/architecture.svg)` が含まれている
- [ ] すべての内容が日本語で記述されている
- [ ] リソース構成の説明が実際のコードと一致している
- [ ] 使用方法のセクションが含まれている
- [ ] 特殊な設定や注意事項が記載されている（該当する場合）

### コード連携

- [ ] README.md の内容が Terraform/CloudFormation コードと一致している
- [ ] リソース数、種類、設定値が正確に記載されている
- [ ] 依存関係が正しく説明されている

## ベストプラクティス

### 図作成時

1. **シンプルさを保つ**: 過度に複雑な図は避け、重要な情報に焦点を当てる
2. **一貫性を保つ**: 同じ種類のリソースは同じアイコンとスタイルを使用
3. **更新を忘れない**: インフラコードを変更したら図も更新する

### README.md 更新時

1. **正確性を最優先**: コードと一致した情報のみを記載
2. **読みやすさ**: 箇条書きとセクション分けを活用
3. **実用的な情報**: デプロイ手順や注意事項を明記

### 保守管理

1. **定期的な見直し**: 四半期ごとに README.md と図の内容を確認
2. **バージョン管理**: 大きな変更時はコミットメッセージに詳細を記載
3. **レビュー**: プルリクエストで図と README の変更も確認
