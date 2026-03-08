#!/usr/bin/env python3
"""
API Gatewayへの並列アクセス性能比較 Lambda関数

マルチセッション（マルチスレッド）、マルチプロセス、並列処理なし（シーケンシャル）の
3つのアプローチでAPI Gatewayに大量アクセスし、終了時刻と所要時間を比較します。

標準ライブラリ（urllib.request, concurrent.futures, multiprocessing）と
Lambdaランタイム組み込みのboto3のみを使用しているため、Lambdaレイヤーは不要です。

環境変数またはイベントパラメータで設定を渡します（イベントが優先されます）:
  API_ENDPOINT   : API GatewayのエンドポイントURL
  USER_POOL_ID   : Cognito User Pool ID
  CLIENT_ID      : Cognito User Pool クライアントID
  USERNAME       : テストユーザー名
  PASSWORD       : テストユーザーパスワード
  AWS_REGION     : AWSリージョン（デフォルト: ap-northeast-1）
  NUM_REQUESTS   : 各アプローチのリクエスト数（デフォルト: 20）
  NUM_WORKERS    : スレッド/プロセスの並列数（デフォルト: 5）
  APPROACHES     : 実行するアプローチのカンマ区切りリスト
                   （デフォルト: sequential,multi_session,multi_process）

イベント例:
  {
    "API_ENDPOINT": "https://xxx.execute-api.ap-northeast-1.amazonaws.com/dev",
    "USER_POOL_ID": "ap-northeast-1_XXXXXXXXX",
    "CLIENT_ID": "xxxxxxxxxxxxxxxxxxxxxxxxxx",
    "USERNAME": "testuser",
    "PASSWORD": "TempPass123!",
    "NUM_REQUESTS": "20",
    "NUM_WORKERS": "5",
    "APPROACHES": "sequential,multi_session,multi_process"
  }
"""

import concurrent.futures
import json
import multiprocessing
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


def _fetch(args: Tuple[str, str]) -> int:
    """URLにGETリクエストを送信し、HTTPステータスコードを返す。

    urllib.request を使用しているため requests ライブラリは不要です。
    """
    url, token = args
    req = urllib.request.Request(
        url,
        headers={"Authorization": f"Bearer {token}"},
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as response:
            return response.status
    except urllib.error.HTTPError as e:
        return e.code
    except Exception:
        return 0


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
# 各アプローチの実装
# ─────────────────────────────────────────────


def _run_sequential(url: str, token: str, num_requests: int) -> Dict:
    """並列処理なし（シーケンシャル）でのAPIアクセス"""
    args = [(url, token)] * num_requests
    print(f"[並列処理なし] {num_requests}件のリクエスト開始")

    start_time = time.perf_counter()
    results: List[int] = [_fetch(a) for a in args]
    elapsed = time.perf_counter() - start_time
    end_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]

    success_count = sum(1 for s in results if s == 200)
    print(
        f"[並列処理なし] 終了時刻: {end_timestamp} "
        f"| 所要時間: {elapsed:.2f}秒 "
        f"| 成功: {success_count}/{num_requests}"
    )
    return {
        "approach": "sequential",
        "end_timestamp": end_timestamp,
        "elapsed_seconds": round(elapsed, 3),
        "success_count": success_count,
        "total_requests": num_requests,
    }


def _run_multi_session(url: str, token: str, num_requests: int, num_workers: int) -> Dict:
    """マルチセッション（マルチスレッド）でのAPIアクセス

    ThreadPoolExecutor を使用し、スレッドごとに独立した OpenerDirector を生成します。
    """
    args = [(url, token)] * num_requests
    print(f"[マルチセッション] {num_requests}件のリクエスト開始 (スレッド数: {num_workers})")

    start_time = time.perf_counter()
    with concurrent.futures.ThreadPoolExecutor(max_workers=num_workers) as executor:
        results: List[int] = list(executor.map(_fetch_with_opener, args))
    elapsed = time.perf_counter() - start_time
    end_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]

    success_count = sum(1 for s in results if s == 200)
    print(
        f"[マルチセッション] 終了時刻: {end_timestamp} "
        f"| 所要時間: {elapsed:.2f}秒 "
        f"| 成功: {success_count}/{num_requests}"
    )
    return {
        "approach": "multi_session",
        "end_timestamp": end_timestamp,
        "elapsed_seconds": round(elapsed, 3),
        "success_count": success_count,
        "total_requests": num_requests,
        "num_workers": num_workers,
    }


def _run_multi_process(url: str, token: str, num_requests: int, num_workers: int) -> Dict:
    """マルチプロセスでのAPIアクセス

    multiprocessing.Pool は Lambda 環境で SemLock 関連エラーになる場合があるため、
    Process + Pipe を使って子プロセスに処理を分割します。
    """
    # Lambda では cpu_count() が小さく固定されることがあるため、
    # ベンチマーク用途ではユーザー指定の並列数を優先する。
    actual_workers = max(1, min(num_workers, num_requests))
    print(f"[マルチプロセス] {num_requests}件のリクエスト開始 (プロセス数: {actual_workers})")

    def _worker(worker_url: str, worker_token: str, worker_requests: int, conn: Any) -> None:
        statuses: List[int] = []
        try:
            for _ in range(worker_requests):
                statuses.append(_fetch((worker_url, worker_token)))
            conn.send({"statuses": statuses})
        except Exception as e:
            conn.send({"error": str(e)})
        finally:
            conn.close()

    base, remainder = divmod(num_requests, actual_workers)
    request_counts = [base + (1 if i < remainder else 0) for i in range(actual_workers)]

    start_time = time.perf_counter()

    processes: List[multiprocessing.Process] = []
    parent_conns: List[Any] = []
    for req_count in request_counts:
        parent_conn, child_conn = multiprocessing.Pipe(duplex=False)
        proc = multiprocessing.Process(target=_worker, args=(url, token, req_count, child_conn))
        processes.append(proc)
        parent_conns.append(parent_conn)

    for proc in processes:
        proc.start()

    results: List[int] = []
    for parent_conn in parent_conns:
        msg = parent_conn.recv()
        if "error" in msg:
            raise RuntimeError(msg["error"])
        results.extend(msg.get("statuses", []))

    for proc in processes:
        proc.join(timeout=60)
        if proc.is_alive():
            proc.terminate()
            proc.join()
            raise RuntimeError("子プロセスの終了待機がタイムアウトしました")

    elapsed = time.perf_counter() - start_time
    end_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]

    success_count = sum(1 for s in results if s == 200)
    print(
        f"[マルチプロセス] 終了時刻: {end_timestamp} "
        f"| 所要時間: {elapsed:.2f}秒 "
        f"| 成功: {success_count}/{num_requests}"
    )
    return {
        "approach": "multi_process",
        "end_timestamp": end_timestamp,
        "elapsed_seconds": round(elapsed, 3),
        "success_count": success_count,
        "total_requests": num_requests,
        "num_workers": actual_workers,
    }


# ─────────────────────────────────────────────
# Lambda ハンドラー
# ─────────────────────────────────────────────


def lambda_handler(event: Dict[str, Any], context: Any) -> Dict:
    """Lambda エントリーポイント

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
    approaches = [a.strip() for a in _get("APPROACHES", "sequential,multi_session,multi_process").split(",")]

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

    approach_map = {
        "sequential": lambda: _run_sequential(target_url, token, num_requests),
        "multi_session": lambda: _run_multi_session(target_url, token, num_requests, num_workers),
        "multi_process": lambda: _run_multi_process(target_url, token, num_requests, num_workers),
    }

    results = []
    for approach in approaches:
        if approach in approach_map:
            try:
                results.append(approach_map[approach]())
            except Exception as e:
                results.append(
                    {
                        "approach": approach,
                        "error": str(e),
                    }
                )

    return {
        "statusCode": 200,
        "body": json.dumps({"results": results}, ensure_ascii=False),
    }
