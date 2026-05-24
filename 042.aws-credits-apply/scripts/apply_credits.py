#!/usr/bin/env python3
"""
AWS Credit Code Bulk Applicator

新規ブラウザを起動し、.env に指定したログイン URL へ遷移した後、
ユーザーの手動ログインを待機します。
指定した準備完了 URL が表示されたら、
config/credits.csv の AWS プロモーションクレジットコードを順番に適用します。
"""

import asyncio
import fnmatch
import json
import os
import sys
from datetime import datetime
from pathlib import Path

from playwright.async_api import async_playwright
from dotenv import load_dotenv

# ── 設定 ──────────────────────────────────────────────────────────────────────

# scripts/ の親ディレクトリ（プロジェクトルート）を基準にパスを解決する
_PROJECT_ROOT = Path(__file__).parent.parent
CREDITS_CSV = _PROJECT_ROOT / "config" / "credits.csv"
LOGS_DIR = _PROJECT_ROOT / "logs"

REDEEM_URL = (
    "https://us-east-1.console.aws.amazon.com/costmanagement/home"
    "?region=us-east-1#/credits/redeemCredits"
)

INPUT_SELECTOR = 'input[name="creditsRedeemCode"]'
SUBMIT_SELECTOR = 'button[data-testid="credits-redeem-button"]'

# API レスポンスを待機する最大時間 (ミリ秒)
RESPONSE_TIMEOUT_MS = 15_000

# 各コード適用後の待機時間 (秒)
WAIT_BETWEEN_CODES_SEC = 3

# 手動ログイン待機の既定タイムアウト (ミリ秒)
DEFAULT_LOGIN_TIMEOUT_MS = 300_000

# アナリティクス / テレメトリ URL に含まれるノイズキーワード
_NOISE_KEYWORDS = ("analytics", "telemetry", "beacon", "metrics", "rum", "ping")

# AWS コンソールのエラーフラッシュ判定用セレクタ
ERROR_FLASH_SELECTOR = 'div[data-analytics-flashbar="error"], div.awsui_flash-type-error'


# ── ヘルパー関数 ──────────────────────────────────────────────────────────────

def load_credit_codes(path: Path) -> list[str]:
    """
    CSV ファイルからクレジットコードを読み込む。
    空行および # で始まる行はスキップする。
    """
    if not path.exists():
        print(f"[ERROR] クレジットコードファイルが見つかりません: {path}", file=sys.stderr)
        sys.exit(1)

    codes: list[str] = []
    with path.open(encoding="utf-8") as f:
        for line in f:
            stripped = line.strip()
            if stripped and not stripped.startswith("#"):
                codes.append(stripped)
    return codes


def save_log(results: list[dict]) -> Path:
    """処理結果を JSON ファイルに保存する。"""
    LOGS_DIR.mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_path = LOGS_DIR / f"credit_application_{ts}.json"
    with log_path.open("w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    return log_path


def _parse_int_env(name: str, default: int) -> int:
    value = os.getenv(name)
    if value is None:
        return default
    try:
        return int(value)
    except ValueError as e:
        raise ValueError(f"{name} は整数で指定してください: {value}") from e


def load_runtime_settings() -> dict:
    """.env と環境変数から実行時設定を読み込む。"""
    load_dotenv(_PROJECT_ROOT / ".env")

    login_url = os.getenv("LOGIN_URL")
    if not login_url:
        raise ValueError("LOGIN_URL が未設定です。.env に LOGIN_URL を設定してください。")

    settings = {
        "login_url": login_url,
        "ready_url": os.getenv("READY_URL", REDEEM_URL),
        "browser_channel": os.getenv("BROWSER_CHANNEL", "chrome"),
        "login_timeout_ms": _parse_int_env("LOGIN_TIMEOUT_MS", DEFAULT_LOGIN_TIMEOUT_MS),
    }
    return settings


def _is_ready_url(current_url: str, ready_url_pattern: str) -> bool:
    """READY_URL パターンに現在 URL が一致するか判定する。"""
    if not current_url:
        return False
    if "*" in ready_url_pattern:
        return fnmatch.fnmatch(current_url, ready_url_pattern)
    return current_url == ready_url_pattern


async def wait_for_ready_page(context, ready_url_pattern: str, timeout_ms: int):
    """ブラウザコンテキスト内の全タブを監視し、READY_URL 一致ページを返す。"""
    deadline = asyncio.get_running_loop().time() + (timeout_ms / 1000)

    while asyncio.get_running_loop().time() < deadline:
        for candidate in context.pages:
            if _is_ready_url(candidate.url, ready_url_pattern):
                return candidate
        await asyncio.sleep(0.5)

    raise asyncio.TimeoutError(
        f"READY_URL に一致するタブが {timeout_ms} ms 以内に見つかりませんでした"
    )


# ── コア処理 ──────────────────────────────────────────────────────────────────

def _is_billing_api_response(response) -> bool:
    """
    クレジット適用 API の POST レスポンスかどうかを判定する。
    アナリティクス系の POST は除外する。
    """
    if response.request.method != "POST":
        return False
    url = response.url.lower()
    return not any(noise in url for noise in _NOISE_KEYWORDS)


async def apply_credit(page, code: str) -> dict:
    """
    1 つのクレジットコードを適用し、結果を返す。

    Returns:
        dict: {
            "code": str,
            "http_status": int | None,
            "status": "success" | "failed" | "error" | "timeout",
            "error": str | None,
            "timestamp": str (ISO 8601),
        }
    """
    result: dict = {
        "code": code,
        "http_status": None,
        "status": "unknown",
        "error": None,
        "timestamp": datetime.now().isoformat(),
    }

    try:
        # クレジット適用ページへ遷移
        await page.goto(REDEEM_URL, wait_until="domcontentloaded")
        await page.wait_for_selector(INPUT_SELECTOR, timeout=15_000)

        # コードを入力
        await page.fill(INPUT_SELECTOR, code)

        # 適用ボタンをクリックし、API レスポンスを待機
        async with page.expect_response(
            _is_billing_api_response,
            timeout=RESPONSE_TIMEOUT_MS,
        ) as resp_info:
            await page.click(SUBMIT_SELECTOR)

        response = await resp_info.value
        result["http_status"] = response.status
        result["status"] = "success" if response.status == 200 else "failed"

        # HTTP 200 でもエラーフラッシュが出た場合は失敗扱いにする
        has_error_flash, flash_message = await detect_error_flash(page)
        if has_error_flash:
            result["status"] = "failed"
            result["error"] = flash_message or "クレジット適用時にエラーフラッシュが表示されました"

    except asyncio.TimeoutError:
        has_error_flash, flash_message = await detect_error_flash(page)
        if has_error_flash:
            result["status"] = "failed"
            result["error"] = flash_message or "クレジット適用時にエラーフラッシュが表示されました"
        else:
            result["status"] = "timeout"
            result["error"] = f"API レスポンスが {RESPONSE_TIMEOUT_MS} ms 以内に返りませんでした"

    except Exception as e:
        result["status"] = "error"
        result["error"] = str(e)

    return result


async def detect_error_flash(page, timeout_ms: int = 2_000) -> tuple[bool, str | None]:
    """エラーフラッシュ表示を検知し、メッセージがあれば返す。"""
    try:
        locator = page.locator(ERROR_FLASH_SELECTOR).first
        await locator.wait_for(state="visible", timeout=timeout_ms)
        message = (await locator.inner_text()).strip()
        return True, message if message else None
    except Exception:
        return False, None


# ── エントリポイント ───────────────────────────────────────────────────────────

async def main() -> None:
    try:
        settings = load_runtime_settings()
    except ValueError as e:
        print(f"[ERROR] 設定エラー: {e}", file=sys.stderr)
        sys.exit(1)

    codes = load_credit_codes(CREDITS_CSV)
    if not codes:
        print("[WARN] credits.csv にクレジットコードが見つかりません。終了します。")
        return

    print(f"クレジットコード {len(codes)} 件を読み込みました: {CREDITS_CSV}")
    print("-" * 50)

    results: list[dict] = []

    async with async_playwright() as pw:
        try:
            browser = await pw.chromium.launch(
                channel=settings["browser_channel"],
                headless=False,
            )
        except Exception as e:
            print(
                f"[ERROR] ブラウザ起動に失敗しました（channel={settings['browser_channel']}）。\n"
                "BROWSER_CHANNEL は chrome または msedge を指定してください。\n"
                f"詳細: {e}",
                file=sys.stderr,
            )
            sys.exit(1)

        context = await browser.new_context()
        page = await context.new_page()

        print(f"ログインページを開きます: {settings['login_url']}")
        await page.goto(settings["login_url"], wait_until="domcontentloaded")
        print(
            "手動ログインを完了してください。"
            f"いずれかのタブで URL が {settings['ready_url']} になったら自動で処理を開始します。"
        )

        try:
            page = await wait_for_ready_page(
                context,
                settings["ready_url"],
                settings["login_timeout_ms"],
            )
        except asyncio.TimeoutError:
            print(
                "[ERROR] ログイン待機がタイムアウトしました。"
                f"指定URL: {settings['ready_url']}\n"
                "MFA/SSO 完了後にいずれかのタブで URL が一致することを確認してください。",
                file=sys.stderr,
            )
            await browser.close()
            sys.exit(1)

        for i, code in enumerate(codes, start=1):
            print(f"[{i}/{len(codes)}] 適用中: {code!r} ... ", end="", flush=True)

            result = await apply_credit(page, code)
            results.append(result)

            http = result["http_status"]
            http_label = f"HTTP {http} → " if http is not None else ""
            print(f"{http_label}{result['status'].upper()}")

            if result["error"]:
                print(f"          エラー: {result['error']}")

            # 最後のコード以外は待機
            if i < len(codes):
                await asyncio.sleep(WAIT_BETWEEN_CODES_SEC)

        await browser.close()

    # 結果をログファイルに保存
    log_path = save_log(results)

    # サマリー表示
    success = sum(1 for r in results if r["status"] == "success")
    failed = len(results) - success

    print("-" * 50)
    print(f"  合計    : {len(results)} 件")
    print(f"  成功    : {success} 件")
    print(f"  失敗    : {failed} 件")
    print(f"  ログ    : {log_path}")


if __name__ == "__main__":
    asyncio.run(main())
