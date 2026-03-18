"""
CloudWatch Logs キーワード検索スクリプト

CloudWatch Logsのロググループからキーワードでログを検索します。
"""

import argparse
import sys
from datetime import datetime, timedelta, timezone
from typing import Optional

import boto3
from botocore.exceptions import BotoCoreError, ClientError


def build_boto3_session(
    region: Optional[str] = None,
    profile: Optional[str] = None,
) -> boto3.Session:
    """boto3セッションを構築する。"""
    kwargs = {}
    if region:
        kwargs["region_name"] = region
    if profile:
        kwargs["profile_name"] = profile
    return boto3.Session(**kwargs)


def list_log_groups(
    client,
    prefix: Optional[str] = None,
) -> list[str]:
    """ロググループ名の一覧を取得する。"""
    paginator = client.get_paginator("describe_log_groups")
    kwargs = {}
    if prefix:
        kwargs["logGroupNamePrefix"] = prefix

    groups = []
    for page in paginator.paginate(**kwargs):
        for group in page.get("logGroups", []):
            groups.append(group["logGroupName"])
    return groups


def search_log_group(
    client,
    log_group_name: str,
    keyword: str,
    start_time_ms: Optional[int] = None,
    end_time_ms: Optional[int] = None,
    limit: int = 100,
) -> list[dict]:
    """指定したロググループをキーワードで検索する。"""
    kwargs: dict = {
        "logGroupName": log_group_name,
        "filterPattern": keyword,
        "limit": limit,
    }
    if start_time_ms is not None:
        kwargs["startTime"] = start_time_ms
    if end_time_ms is not None:
        kwargs["endTime"] = end_time_ms

    events = []
    try:
        paginator = client.get_paginator("filter_log_events")
        for page in paginator.paginate(**kwargs, PaginationConfig={"MaxItems": limit}):
            for event in page.get("events", []):
                events.append(
                    {
                        "logGroupName": log_group_name,
                        "logStreamName": event.get("logStreamName", ""),
                        "timestamp": event.get("timestamp", 0),
                        "message": event.get("message", ""),
                    }
                )
            if len(events) >= limit:
                break
    except ClientError as exc:
        error_code = exc.response["Error"]["Code"]
        if error_code == "ResourceNotFoundException":
            print(
                f"[WARN] ロググループが見つかりません: {log_group_name}",
                file=sys.stderr,
            )
        else:
            raise
    return events[:limit]


def format_timestamp(ts_ms: int) -> str:
    """ミリ秒タイムスタンプをISO 8601形式の文字列に変換する。"""
    dt = datetime.fromtimestamp(ts_ms / 1000, tz=timezone.utc)
    return dt.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"


def parse_relative_time(value: str) -> datetime:
    """
    '1h', '30m', '7d' などの相対時刻文字列をdatetimeに変換する。
    末尾の単位: h=時間, m=分, d=日
    """
    units = {"h": "hours", "m": "minutes", "d": "days"}
    unit = value[-1].lower()
    if unit not in units:
        raise argparse.ArgumentTypeError(
            f"不正な時刻形式: '{value}'. 例: '1h', '30m', '7d'"
        )
    try:
        amount = int(value[:-1])
    except ValueError as exc:
        raise argparse.ArgumentTypeError(
            f"不正な数値: '{value[:-1]}'"
        ) from exc
    return datetime.now(tz=timezone.utc) - timedelta(**{units[unit]: amount})


def to_epoch_ms(dt: datetime) -> int:
    """datetimeをミリ秒エポック時刻に変換する。"""
    return int(dt.timestamp() * 1000)


def build_parser() -> argparse.ArgumentParser:
    """コマンドライン引数パーサーを構築する。"""
    parser = argparse.ArgumentParser(
        description="CloudWatch Logsをキーワードで検索するスクリプト",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用例:
  # ロググループ名を指定してキーワード検索
  python search_cloudwatch_logs.py --keyword ERROR --log-group-name /aws/lambda/my-function

  # プレフィックスに一致する全ロググループを検索
  python search_cloudwatch_logs.py --keyword ERROR --log-group-prefix /aws/lambda/

  # 過去1時間のログを検索
  python search_cloudwatch_logs.py --keyword ERROR --log-group-prefix /aws/lambda/ --since 1h

  # リージョンとプロファイルを指定
  python search_cloudwatch_logs.py --keyword ERROR --log-group-prefix /aws/ --region ap-northeast-1 --profile my-profile
""",
    )
    parser.add_argument(
        "--keyword",
        required=True,
        help="検索するキーワード（CloudWatch Logs フィルターパターンとして使用）",
    )

    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "--log-group-name",
        help="検索対象のロググループ名（完全一致）",
    )
    group.add_argument(
        "--log-group-prefix",
        help="検索対象のロググループのプレフィックス（前方一致で複数グループを検索）",
    )

    parser.add_argument(
        "--since",
        default="1h",
        help="検索開始時刻（相対時刻: '1h', '30m', '7d' など。デフォルト: 1h）",
    )
    parser.add_argument(
        "--until",
        default=None,
        help="検索終了時刻（相対時刻: '1h', '30m', '7d' など。省略時は現在時刻）",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=100,
        help="取得するログイベントの最大件数（デフォルト: 100）",
    )
    parser.add_argument(
        "--region",
        default=None,
        help="AWSリージョン（省略時は環境変数 AWS_DEFAULT_REGION またはデフォルトリージョン）",
    )
    parser.add_argument(
        "--profile",
        default=None,
        help="AWS CLIプロファイル名（省略時はデフォルトプロファイル）",
    )
    return parser


def run(args: argparse.Namespace) -> int:
    """メイン処理を実行する。成功時は0、エラー時は非0を返す。"""
    try:
        start_dt = parse_relative_time(args.since)
    except argparse.ArgumentTypeError as exc:
        print(f"[ERROR] --since の値が不正です: {exc}", file=sys.stderr)
        return 1

    end_dt: Optional[datetime] = None
    if args.until:
        try:
            end_dt = parse_relative_time(args.until)
        except argparse.ArgumentTypeError as exc:
            print(f"[ERROR] --until の値が不正です: {exc}", file=sys.stderr)
            return 1

    start_ms = to_epoch_ms(start_dt)
    end_ms = to_epoch_ms(end_dt) if end_dt else None

    try:
        session = build_boto3_session(
            region=args.region,
            profile=args.profile,
        )
        client = session.client("logs")
    except (BotoCoreError, Exception) as exc:
        print(f"[ERROR] AWSクライアントの初期化に失敗しました: {exc}", file=sys.stderr)
        return 1

    if args.log_group_name:
        log_groups = [args.log_group_name]
    else:
        try:
            log_groups = list_log_groups(client, prefix=args.log_group_prefix)
        except (BotoCoreError, ClientError) as exc:
            print(f"[ERROR] ロググループの取得に失敗しました: {exc}", file=sys.stderr)
            return 1

    if not log_groups:
        print("[INFO] 対象のロググループが見つかりませんでした。")
        return 0

    total_count = 0
    for log_group in log_groups:
        try:
            events = search_log_group(
                client=client,
                log_group_name=log_group,
                keyword=args.keyword,
                start_time_ms=start_ms,
                end_time_ms=end_ms,
                limit=args.limit,
            )
        except (BotoCoreError, ClientError) as exc:
            print(
                f"[ERROR] ロググループ '{log_group}' の検索中にエラーが発生しました: {exc}",
                file=sys.stderr,
            )
            return 1

        for event in events:
            ts_str = format_timestamp(event["timestamp"])
            print(
                f"[{ts_str}] [{event['logGroupName']}] [{event['logStreamName']}] {event['message']}"
            )

        total_count += len(events)

    print(f"\n{total_count} 件のログが見つかりました。", file=sys.stderr)
    return 0


def main() -> None:
    """エントリーポイント。"""
    parser = build_parser()
    args = parser.parse_args()
    sys.exit(run(args))


if __name__ == "__main__":
    main()
