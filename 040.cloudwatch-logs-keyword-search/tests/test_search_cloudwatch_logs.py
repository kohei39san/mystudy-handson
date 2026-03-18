"""
search_cloudwatch_logs.py のユニットテスト
"""

import argparse
import sys
import os
import time
from datetime import datetime, timezone
from unittest.mock import MagicMock, patch

import pytest
from botocore.exceptions import ClientError
from moto import mock_aws
import boto3

# スクリプトのパスをモジュール検索パスに追加
current_dir = os.path.dirname(os.path.abspath(__file__))
project_dir = os.path.dirname(current_dir)
sys.path.insert(0, project_dir)

from scripts.search_cloudwatch_logs import (
    build_boto3_session,
    build_parser,
    format_timestamp,
    list_log_groups,
    parse_relative_time,
    run,
    search_log_group,
    to_epoch_ms,
)


# ---------------------------------------------------------------------------
# フィクスチャ
# ---------------------------------------------------------------------------


@pytest.fixture()
def logs_client():
    """moto でモックされた CloudWatch Logs クライアントを返す。"""
    with mock_aws():
        client = boto3.client("logs", region_name="ap-northeast-1")
        yield client


@pytest.fixture()
def log_group_with_events(logs_client):
    """
    テスト用のロググループとログストリーム、
    キーワード 'ERROR' を含むイベントを作成して返す。
    """
    group_name = "/test/my-app"
    stream_name = "stream-1"
    logs_client.create_log_group(logGroupName=group_name)
    logs_client.create_log_stream(
        logGroupName=group_name, logStreamName=stream_name
    )
    now_ms = int(time.time() * 1000)
    events = [
        {"timestamp": now_ms - 8000, "message": "INFO: 正常に起動しました"},
        {"timestamp": now_ms - 6000, "message": "ERROR: 予期しないエラーが発生しました"},
        {"timestamp": now_ms - 4000, "message": "WARN: リトライ中です"},
        {"timestamp": now_ms - 2000, "message": "ERROR: データベース接続に失敗しました"},
    ]
    logs_client.put_log_events(
        logGroupName=group_name,
        logStreamName=stream_name,
        logEvents=events,
    )
    return {"group_name": group_name, "stream_name": stream_name, "events": events}


# ---------------------------------------------------------------------------
# parse_relative_time のテスト
# ---------------------------------------------------------------------------


class TestParseRelativeTime:
    """parse_relative_time 関数のテスト"""

    @pytest.mark.unit
    def test_parse_hours(self):
        """時間単位 'h' が正しく解析される。"""
        result = parse_relative_time("2h")
        assert isinstance(result, datetime)
        assert result.tzinfo == timezone.utc

    @pytest.mark.unit
    def test_parse_minutes(self):
        """分単位 'm' が正しく解析される。"""
        result = parse_relative_time("30m")
        assert isinstance(result, datetime)

    @pytest.mark.unit
    def test_parse_days(self):
        """日単位 'd' が正しく解析される。"""
        result = parse_relative_time("7d")
        assert isinstance(result, datetime)

    @pytest.mark.unit
    def test_invalid_unit(self):
        """不正な単位はエラーになる。"""
        with pytest.raises(argparse.ArgumentTypeError):
            parse_relative_time("5x")

    @pytest.mark.unit
    def test_invalid_number(self):
        """数値でない文字列はエラーになる。"""
        with pytest.raises(argparse.ArgumentTypeError):
            parse_relative_time("abch")


# ---------------------------------------------------------------------------
# format_timestamp のテスト
# ---------------------------------------------------------------------------


class TestFormatTimestamp:
    """format_timestamp 関数のテスト"""

    @pytest.mark.unit
    def test_format_timestamp(self):
        """ミリ秒エポック時刻がISO 8601形式に変換される。"""
        # 2023-11-14T22:13:20.000Z
        ts_ms = 1_700_000_000_000
        result = format_timestamp(ts_ms)
        assert result.endswith("Z")
        assert "T" in result
        assert len(result) == 24  # "YYYY-MM-DDTHH:MM:SS.mmmZ"


# ---------------------------------------------------------------------------
# to_epoch_ms のテスト
# ---------------------------------------------------------------------------


class TestToEpochMs:
    """to_epoch_ms 関数のテスト"""

    @pytest.mark.unit
    def test_to_epoch_ms(self):
        """datetime がミリ秒エポック時刻に変換される。"""
        dt = datetime(2023, 11, 14, 22, 13, 20, tzinfo=timezone.utc)
        result = to_epoch_ms(dt)
        assert result == 1_700_000_000_000


# ---------------------------------------------------------------------------
# build_boto3_session のテスト
# ---------------------------------------------------------------------------


class TestBuildBoto3Session:
    """build_boto3_session 関数のテスト"""

    @pytest.mark.unit
    def test_default_session(self):
        """引数なしでセッションが作成される。"""
        session = build_boto3_session()
        assert isinstance(session, boto3.Session)

    @pytest.mark.unit
    def test_region_is_set(self):
        """リージョンが指定された場合にセッションに反映される。"""
        session = build_boto3_session(region="us-east-1")
        assert session.region_name == "us-east-1"


# ---------------------------------------------------------------------------
# list_log_groups のテスト
# ---------------------------------------------------------------------------


class TestListLogGroups:
    """list_log_groups 関数のテスト"""

    @pytest.mark.unit
    def test_list_all_groups(self, logs_client):
        """全ロググループが取得できる。"""
        logs_client.create_log_group(logGroupName="/app/service-a")
        logs_client.create_log_group(logGroupName="/app/service-b")
        logs_client.create_log_group(logGroupName="/other/service")

        groups = list_log_groups(logs_client)
        assert "/app/service-a" in groups
        assert "/app/service-b" in groups
        assert "/other/service" in groups

    @pytest.mark.unit
    def test_list_groups_with_prefix(self, logs_client):
        """プレフィックス指定でフィルタリングできる。"""
        logs_client.create_log_group(logGroupName="/app/service-a")
        logs_client.create_log_group(logGroupName="/app/service-b")
        logs_client.create_log_group(logGroupName="/other/service")

        groups = list_log_groups(logs_client, prefix="/app/")
        assert "/app/service-a" in groups
        assert "/app/service-b" in groups
        assert "/other/service" not in groups

    @pytest.mark.unit
    def test_empty_when_no_groups(self, logs_client):
        """ロググループが存在しない場合は空リストを返す。"""
        groups = list_log_groups(logs_client, prefix="/nonexistent/")
        assert groups == []


# ---------------------------------------------------------------------------
# search_log_group のテスト
# ---------------------------------------------------------------------------


class TestSearchLogGroup:
    """search_log_group 関数のテスト"""

    @pytest.mark.unit
    def test_search_finds_keyword(self, logs_client, log_group_with_events):
        """キーワードを含むログイベントが返される。"""
        group_name = log_group_with_events["group_name"]
        events = search_log_group(
            client=logs_client,
            log_group_name=group_name,
            keyword="ERROR",
        )
        assert len(events) >= 1
        for event in events:
            assert "ERROR" in event["message"]
            assert event["logGroupName"] == group_name
            assert "logStreamName" in event
            assert "timestamp" in event

    @pytest.mark.unit
    def test_search_returns_empty_for_no_match(self, logs_client, log_group_with_events):
        """マッチするログがない場合は空リストが返される。"""
        group_name = log_group_with_events["group_name"]
        events = search_log_group(
            client=logs_client,
            log_group_name=group_name,
            keyword="NONEXISTENT_KEYWORD_XYZ",
        )
        assert events == []

    @pytest.mark.unit
    def test_search_nonexistent_group(self, logs_client):
        """存在しないロググループは空リストを返す（警告を出力）。"""
        events = search_log_group(
            client=logs_client,
            log_group_name="/nonexistent/group",
            keyword="ERROR",
        )
        assert events == []

    @pytest.mark.unit
    def test_search_respects_limit(self, logs_client, log_group_with_events):
        """limit パラメータが結果件数の上限として機能する。"""
        group_name = log_group_with_events["group_name"]
        # limit=1 を指定しても実際には moto の動作に依存するが、上限は超えない
        events = search_log_group(
            client=logs_client,
            log_group_name=group_name,
            keyword="ERROR",
            limit=1,
        )
        assert len(events) <= 1


# ---------------------------------------------------------------------------
# build_parser のテスト
# ---------------------------------------------------------------------------


class TestBuildParser:
    """build_parser 関数のテスト"""

    @pytest.mark.unit
    def test_required_keyword(self):
        """--keyword が必須引数である。"""
        parser = build_parser()
        with pytest.raises(SystemExit):
            parser.parse_args(["--log-group-name", "/test/group"])

    @pytest.mark.unit
    def test_required_log_group(self):
        """ロググループ指定が必須である。"""
        parser = build_parser()
        with pytest.raises(SystemExit):
            parser.parse_args(["--keyword", "ERROR"])

    @pytest.mark.unit
    def test_mutually_exclusive_log_group_args(self):
        """--log-group-name と --log-group-prefix は同時指定不可。"""
        parser = build_parser()
        with pytest.raises(SystemExit):
            parser.parse_args([
                "--keyword", "ERROR",
                "--log-group-name", "/test",
                "--log-group-prefix", "/test/",
            ])

    @pytest.mark.unit
    def test_valid_args_with_log_group_name(self):
        """--log-group-name を使った有効な引数が解析される。"""
        parser = build_parser()
        args = parser.parse_args([
            "--keyword", "ERROR",
            "--log-group-name", "/test/group",
        ])
        assert args.keyword == "ERROR"
        assert args.log_group_name == "/test/group"
        assert args.log_group_prefix is None
        assert args.since == "1h"
        assert args.limit == 100

    @pytest.mark.unit
    def test_valid_args_with_log_group_prefix(self):
        """--log-group-prefix を使った有効な引数が解析される。"""
        parser = build_parser()
        args = parser.parse_args([
            "--keyword", "WARN",
            "--log-group-prefix", "/aws/lambda/",
            "--since", "30m",
            "--limit", "50",
            "--region", "ap-northeast-1",
        ])
        assert args.keyword == "WARN"
        assert args.log_group_prefix == "/aws/lambda/"
        assert args.since == "30m"
        assert args.limit == 50
        assert args.region == "ap-northeast-1"


# ---------------------------------------------------------------------------
# run 関数のエンドツーエンドテスト
# ---------------------------------------------------------------------------


class TestRun:
    """run 関数のテスト"""

    @pytest.mark.unit
    def test_run_with_log_group_name(self, logs_client, log_group_with_events, capsys):
        """ロググループ名を指定して run が正常終了する。"""
        group_name = log_group_with_events["group_name"]
        parser = build_parser()
        args = parser.parse_args([
            "--keyword", "ERROR",
            "--log-group-name", group_name,
        ])

        with patch(
            "scripts.search_cloudwatch_logs.build_boto3_session"
        ) as mock_session:
            mock_session.return_value.client.return_value = logs_client
            result = run(args)

        assert result == 0
        captured = capsys.readouterr()
        assert "ERROR" in captured.out

    @pytest.mark.unit
    def test_run_with_log_group_prefix(self, logs_client, log_group_with_events, capsys):
        """プレフィックスを指定して run が正常終了する。"""
        parser = build_parser()
        args = parser.parse_args([
            "--keyword", "ERROR",
            "--log-group-prefix", "/test/",
        ])

        with patch(
            "scripts.search_cloudwatch_logs.build_boto3_session"
        ) as mock_session:
            mock_session.return_value.client.return_value = logs_client
            result = run(args)

        assert result == 0

    @pytest.mark.unit
    def test_run_no_matching_log_groups(self, logs_client, capsys):
        """マッチするロググループがない場合は 0 件で正常終了する。"""
        parser = build_parser()
        args = parser.parse_args([
            "--keyword", "ERROR",
            "--log-group-prefix", "/nonexistent/",
        ])

        with patch(
            "scripts.search_cloudwatch_logs.build_boto3_session"
        ) as mock_session:
            mock_session.return_value.client.return_value = logs_client
            result = run(args)

        assert result == 0
        captured = capsys.readouterr()
        assert "見つかりませんでした" in captured.out

    @pytest.mark.unit
    def test_run_invalid_since(self, capsys):
        """--since に不正な値を渡すと 1 が返る。"""
        parser = build_parser()
        args = parser.parse_args([
            "--keyword", "ERROR",
            "--log-group-name", "/test/group",
        ])
        args.since = "bad_value"

        result = run(args)
        assert result == 1
        captured = capsys.readouterr()
        assert "ERROR" in captured.err

    @pytest.mark.unit
    def test_run_client_error_on_list_groups(self, capsys):
        """ロググループ一覧取得時の ClientError でエラー終了する。"""
        parser = build_parser()
        args = parser.parse_args([
            "--keyword", "ERROR",
            "--log-group-prefix", "/test/",
        ])

        mock_client = MagicMock()
        mock_paginator = MagicMock()
        mock_paginator.paginate.side_effect = ClientError(
            {"Error": {"Code": "AccessDeniedException", "Message": "Access Denied"}},
            "DescribeLogGroups",
        )
        mock_client.get_paginator.return_value = mock_paginator

        with patch(
            "scripts.search_cloudwatch_logs.build_boto3_session"
        ) as mock_session:
            mock_session.return_value.client.return_value = mock_client
            result = run(args)

        assert result == 1
        captured = capsys.readouterr()
        assert "ERROR" in captured.err
