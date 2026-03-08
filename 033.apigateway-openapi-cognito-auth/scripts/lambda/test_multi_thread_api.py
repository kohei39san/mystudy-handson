#!/usr/bin/env python3
"""
API Gatewayへのマルチスレッド並列アクセス Lambda関数

ThreadPoolExecutor を使用してAPIエンドポイントに並列アクセスし、
スレッドごとに独立した urllib.request.OpenerDirector を生成することで
セッションを分離します。

標準ライブラリ（urllib.request, concurrent.futures）と
Lambdaランタイム組み込みのboto3のみを使用しているため、Lambdaレイヤーは不要です。

環境変数またはイベントパラメータで設定を渡します（イベントが優先されます）:
  API_ENDPOINT   : API GatewayのエンドポイントURL
  USER_POOL_ID   : Cognito User Pool ID
  CLIENT_ID      : Cognito User Pool クライアントID
  USERNAME       : テストユーザー名
  PASSWORD       : テストユーザーパスワード
  AWS_REGION     : AWSリージョン（デフォルト: ap-northeast-1）
  NUM_REQUESTS   : リクエスト数（デフォルト: 20）
  NUM_WORKERS    : スレッドの並列数（デフォルト: 5）

イベント例:
  {
    "API_ENDPOINT": "https://xxx.execute-api.ap-northeast-1.amazonaws.com/dev",
    "USER_POOL_ID": "ap-northeast-1_XXXXXXXXX",
    "CLIENT_ID": "xxxxxxxxxxxxxxxxxxxxxxxxxx",
    "USERNAME": "testuser",
    "PASSWORD": "TempPass123!",
    "NUM_REQUESTS": "20",
    "NUM_WORKERS": "5"
  }
"""

import concurrent.futures
import json
import os
import time
import urllib.error
import urllib.request
from datetime import datetime
from typing import Any, Dict, List, Tuple

import boto3


# ─────────────────────────────────────────────
# HTTPリクエスト関数（標準ライブラリのみ使用）
# ─────────────────────────────────────────────


def _fetch_with_opener(args: Tuple[str, str]) -> int:
    """スレッドごとに独立した OpenerDirector を生成してGETリクエストを送信する。

    urllib.request.build_opener() でスレッド専用のオープナーを生成し、
    マルチスレッド環境でのセッション分離を実現します。
    """
    url, token = args
    req = urllib.request.Request(
        url,
        headers={"Authorization": f"Bearer {token}"},
    )
    opener = urllib.request.build_opener()
    try:
        with opener.open(req, timeout=30) as response:
            return response.status
    except urllib.error.HTTPError as e:
        return e.code
    except Exception:
        return 0


# ─────────────────────────────────────────────
# Lambda ハンドラー
# ─────────────────────────────────────────────


def lambda_handler(event: Dict[str, Any], context: Any) -> Dict:
    """Lambda エントリーポイント

    ThreadPoolExecutor を使用してAPI Gatewayに並列アクセスします。
    環境変数またはイベントパラメータで設定を渡します。
    イベントのパラメータが環境変数より優先されます。
    """

    def _get(key: str, default: str = "") -> str:
        return str(event.get(key) or os.environ.get(key, default))

    endpoint = _get("API_ENDPOINT").rstrip("/")
    user_pool_id = _get("USER_POOL_ID")
    client_id = _get("CLIENT_ID")
    username = _get("USERNAME")
    password = _get("PASSWORD")
    region = _get("AWS_REGION", "ap-northeast-1")
    num_requests = int(_get("NUM_REQUESTS", "20"))
    num_workers = int(_get("NUM_WORKERS", "5"))

    required_params = {
        "API_ENDPOINT": endpoint,
        "USER_POOL_ID": user_pool_id,
        "CLIENT_ID": client_id,
        "USERNAME": username,
        "PASSWORD": password,
    }
    missing = [key for key, value in required_params.items() if not value]
    if missing:
        return {
            "statusCode": 400,
            "body": json.dumps(
                {"error": f"必須パラメータが不足しています: {', '.join(missing)}"},
                ensure_ascii=False,
            ),
        }

    # Cognito で認証してアクセストークンを取得
    cognito = boto3.client("cognito-idp", region_name=region)
    auth_response = cognito.admin_initiate_auth(
        UserPoolId=user_pool_id,
        ClientId=client_id,
        AuthFlow="ADMIN_USER_PASSWORD_AUTH",
        AuthParameters={"USERNAME": username, "PASSWORD": password},
    )
    token = auth_response["AuthenticationResult"]["AccessToken"]
    target_url = f"{endpoint}/public"

    # マルチスレッドでAPIアクセス
    args: List[Tuple[str, str]] = [(target_url, token)] * num_requests
    print(f"[マルチスレッド] {num_requests}件のリクエスト開始 (スレッド数: {num_workers})")

    start_time = time.perf_counter()
    with concurrent.futures.ThreadPoolExecutor(max_workers=num_workers) as executor:
        results: List[int] = list(executor.map(_fetch_with_opener, args))
    elapsed = time.perf_counter() - start_time
    end_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]

    success_count = sum(1 for s in results if s == 200)
    print(
        f"[マルチスレッド] 終了時刻: {end_timestamp} "
        f"| 所要時間: {elapsed:.2f}秒 "
        f"| 成功: {success_count}/{num_requests}"
    )

    return {
        "statusCode": 200,
        "body": json.dumps(
            {
                "approach": "multi_thread",
                "end_timestamp": end_timestamp,
                "elapsed_seconds": round(elapsed, 3),
                "success_count": success_count,
                "total_requests": num_requests,
                "num_workers": num_workers,
            },
            ensure_ascii=False,
        ),
    }
