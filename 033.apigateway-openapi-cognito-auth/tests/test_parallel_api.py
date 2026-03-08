#!/usr/bin/env python3
"""
API Gatewayへの並列アクセス性能比較テスト

マルチセッション（マルチスレッド）、マルチプロセス、並列処理なし（シーケンシャル）の
3つのアプローチでAPI Gatewayに大量アクセスし、終了時刻を比較します。

使用方法:
  pytest tests/test_parallel_api.py -v -s

環境変数 (`.env` ファイルまたはシステム環境変数):
  API_ENDPOINT   : API GatewayのエンドポイントURL
  USER_POOL_ID   : Cognito User Pool ID
  CLIENT_ID      : Cognito User Pool クライアントID
  USERNAME       : テストユーザー名
  PASSWORD       : テストユーザーパスワード
  AWS_REGION     : AWSリージョン（デフォルト: ap-northeast-1）
  NUM_REQUESTS   : 各アプローチのリクエスト数（デフォルト: 50）
  NUM_WORKERS    : スレッド/プロセスの並列数（デフォルト: 10）
"""

import concurrent.futures
import multiprocessing
import os
import time
from datetime import datetime
from typing import Dict, List, Tuple

import boto3
import pytest
import requests

try:
    from dotenv import load_dotenv

    load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "..", ".env"))
except ImportError:
    pass


# ─────────────────────────────────────────────
# プロセス間で共有するトップレベル関数
# ─────────────────────────────────────────────


def _request_without_session(args: Tuple[str, str]) -> int:
    """セッションを使用せずAPIへの1リクエストを実行する（並列処理なし用）"""
    endpoint, token = args
    headers = {"Authorization": f"Bearer {token}"}
    try:
        response = requests.get(
            f"{endpoint}/public", headers=headers, timeout=30
        )
        return response.status_code
    except Exception:
        return 0


def _request_with_new_session(args: Tuple[str, str]) -> int:
    """新しいセッションを生成してAPIへの1リクエストを実行する（マルチセッション用）"""
    endpoint, token = args
    headers = {"Authorization": f"Bearer {token}"}
    try:
        with requests.Session() as session:
            response = session.get(
                f"{endpoint}/public", headers=headers, timeout=30
            )
            return response.status_code
    except Exception:
        return 0


# ─────────────────────────────────────────────
# 共有フィクスチャ
# ─────────────────────────────────────────────


@pytest.fixture(scope="module")
def api_config() -> Dict:
    """テスト設定を読み込み、Cognitoアクセストークンを取得する"""
    required_vars = ["API_ENDPOINT", "USER_POOL_ID", "CLIENT_ID", "USERNAME", "PASSWORD"]
    missing = [var for var in required_vars if not os.environ.get(var)]
    if missing:
        pytest.skip(f"環境変数が設定されていません: {', '.join(missing)}")

    region = os.environ.get("AWS_REGION", "ap-northeast-1")
    user_pool_id = os.environ["USER_POOL_ID"]
    client_id = os.environ["CLIENT_ID"]
    username = os.environ["USERNAME"]
    password = os.environ["PASSWORD"]
    endpoint = os.environ["API_ENDPOINT"].rstrip("/")
    num_requests = int(os.environ.get("NUM_REQUESTS", "50"))
    num_workers = int(os.environ.get("NUM_WORKERS", "10"))

    cognito = boto3.client("cognito-idp", region_name=region)
    response = cognito.admin_initiate_auth(
        UserPoolId=user_pool_id,
        ClientId=client_id,
        AuthFlow="ADMIN_USER_PASSWORD_AUTH",
        AuthParameters={"USERNAME": username, "PASSWORD": password},
    )
    token = response["AuthenticationResult"]["AccessToken"]

    return {
        "endpoint": endpoint,
        "token": token,
        "num_requests": num_requests,
        "num_workers": num_workers,
    }


# ─────────────────────────────────────────────
# テストクラス
# ─────────────────────────────────────────────


class TestParallelAPIAccess:
    """API Gatewayへの並列アクセス性能比較テスト

    3つのアプローチでそれぞれ `NUM_REQUESTS` 件のリクエストを送信し、
    各アプローチの所要時間を出力して比較します。

    アプローチ:
        - 並列処理なし  : シーケンシャルにリクエストを送信
        - マルチセッション: ThreadPoolExecutor を使用したマルチスレッド処理
                         スレッドごとに独立した requests.Session を生成
        - マルチプロセス  : multiprocessing.Pool を使用したマルチプロセス処理
    """

    def test_sequential(self, api_config: Dict) -> None:
        """並列処理なし（シーケンシャル）でのAPIアクセス"""
        endpoint = api_config["endpoint"]
        token = api_config["token"]
        num_requests = api_config["num_requests"]
        args = [(endpoint, token)] * num_requests

        print(f"\n{'='*60}")
        print(f"[並列処理なし] {num_requests}件のリクエスト開始")

        start_time = time.perf_counter()
        results: List[int] = [_request_without_session(a) for a in args]
        elapsed = time.perf_counter() - start_time
        end_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]

        success_count = sum(1 for s in results if s == 200)
        print(
            f"[並列処理なし] 終了時刻: {end_timestamp} "
            f"| 所要時間: {elapsed:.2f}秒 "
            f"| 成功: {success_count}/{num_requests}"
        )

        assert success_count > 0, (
            f"リクエストが全て失敗しました（ステータス: {set(results)}）"
        )

    def test_multi_session(self, api_config: Dict) -> None:
        """マルチセッション（マルチスレッド）でのAPIアクセス

        ThreadPoolExecutor を使用してリクエストを並列実行します。
        各スレッドが独立した requests.Session を生成するため、
        セッション（TCP接続）レベルで並列化されます。
        """
        endpoint = api_config["endpoint"]
        token = api_config["token"]
        num_requests = api_config["num_requests"]
        num_workers = api_config["num_workers"]
        args = [(endpoint, token)] * num_requests

        print(f"\n{'='*60}")
        print(
            f"[マルチセッション] {num_requests}件のリクエスト開始 "
            f"(スレッド数: {num_workers})"
        )

        start_time = time.perf_counter()
        with concurrent.futures.ThreadPoolExecutor(max_workers=num_workers) as executor:
            results: List[int] = list(executor.map(_request_with_new_session, args))
        elapsed = time.perf_counter() - start_time
        end_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]

        success_count = sum(1 for s in results if s == 200)
        print(
            f"[マルチセッション] 終了時刻: {end_timestamp} "
            f"| 所要時間: {elapsed:.2f}秒 "
            f"| 成功: {success_count}/{num_requests}"
        )

        assert success_count > 0, (
            f"リクエストが全て失敗しました（ステータス: {set(results)}）"
        )

    def test_multi_process(self, api_config: Dict) -> None:
        """マルチプロセスでのAPIアクセス

        multiprocessing.Pool を使用してリクエストを並列実行します。
        プロセスレベルで並列化されるため、GILの制約を受けません。
        """
        endpoint = api_config["endpoint"]
        token = api_config["token"]
        num_requests = api_config["num_requests"]
        num_workers = api_config["num_workers"]
        args = [(endpoint, token)] * num_requests

        actual_workers = min(num_workers, multiprocessing.cpu_count())
        print(f"\n{'='*60}")
        print(
            f"[マルチプロセス] {num_requests}件のリクエスト開始 "
            f"(プロセス数: {actual_workers})"
        )

        start_time = time.perf_counter()
        with multiprocessing.Pool(processes=actual_workers) as pool:
            results: List[int] = pool.map(_request_without_session, args)
        elapsed = time.perf_counter() - start_time
        end_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]

        success_count = sum(1 for s in results if s == 200)
        print(
            f"[マルチプロセス] 終了時刻: {end_timestamp} "
            f"| 所要時間: {elapsed:.2f}秒 "
            f"| 成功: {success_count}/{num_requests}"
        )

        assert success_count > 0, (
            f"リクエストが全て失敗しました（ステータス: {set(results)}）"
        )
