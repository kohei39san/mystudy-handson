# Docker Compose Test Runner

このディレクトリには、Amazon Linux 2023コンテナ内でAPIテストを実行するためのDocker Compose設定が含まれています。

## セットアップ

1. 環境変数ファイルを作成:

```bash
cp .env.example .env
```

2. `.env` ファイルを編集して実際の値を設定:

```ini
API_ENDPOINT=https://yz14ppfme3.execute-api.ap-northeast-1.amazonaws.com/dev
USER_POOL_ID=ap-northeast-1_y0tYTypg2
CLIENT_ID=65f8linv00m2vpem93bnk404vu
USERNAME=testuser
PASSWORD=YourActualPassword
```

## 使用方法

### Bashスクリプトテスト (test-login-user.sh)

```bash
docker-compose run --rm test-runner
```

### Pythonテスト (test-login.py)

```bash
docker-compose run --rm python-test-runner
```

### カスタムコマンド実行

特定のテストを実行する場合:

```bash
# test-api.py を実行
docker-compose run --rm python-test-runner sh -c "
  dnf install -y python3 python3-pip &&
  pip3 install boto3 requests &&
  python3 /workspace/tests/test-api.py --api-endpoint $API_ENDPOINT --user-pool-id $USER_POOL_ID --client-id $CLIENT_ID
"

# test-revoke-api.py を実行
docker-compose run --rm python-test-runner sh -c "
  dnf install -y python3 python3-pip &&
  pip3 install boto3 requests &&
  python3 /workspace/tests/test-revoke-api.py --endpoint $API_ENDPOINT --username targetuser
"
```

### 環境変数を直接指定

```bash
API_ENDPOINT=https://your-api.amazonaws.com/dev \
USERNAME=testuser \
PASSWORD=YourPassword \
docker-compose run --rm test-runner
```

## コンテナの詳細

### test-runner
- **イメージ**: amazonlinux:2023
- **用途**: Bashスクリプトテスト
- **インストールパッケージ**: curl, jq
- **マウント**: scripts/tests, scripts/lambda (読み取り専用)

### python-test-runner
- **イメージ**: amazonlinux:2023
- **用途**: Pythonベースのテスト
- **インストールパッケージ**: python3, boto3, requests
- **マウント**: scripts/tests, scripts, ~/.aws (読み取り専用)

## トラブルシューティング

### AWS認証情報エラー

Python テストで AWS SDK (boto3) を使用する場合、AWS認証情報が必要です:

```bash
# AWS認証情報を環境変数で渡す
AWS_ACCESS_KEY_ID=your-key \
AWS_SECRET_ACCESS_KEY=your-secret \
docker-compose run --rm python-test-runner
```

または、`docker-compose.yml` の volumes セクションで `~/.aws` をマウント済みです。

### パスワードエラー

パスワードに特殊文字が含まれる場合は、`.env` ファイルで引用符で囲んでください:

```ini
PASSWORD='YourP@ssw0rd!'
```

## クリーンアップ

```bash
docker-compose down
docker rmi amazonlinux:2023
```
