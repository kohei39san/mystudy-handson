import asyncio
import importlib.util
import json
import sys
from pathlib import Path

import pytest


PROJECT_ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = PROJECT_ROOT / "scripts" / "apply_credits.py"

spec = importlib.util.spec_from_file_location("apply_credits", MODULE_PATH)
apply_credits = importlib.util.module_from_spec(spec)
sys.modules["apply_credits"] = apply_credits
assert spec.loader is not None
spec.loader.exec_module(apply_credits)


class DummyRequest:
    def __init__(self, method: str):
        self.method = method


class DummyResponse:
    def __init__(self, status: int, method: str = "POST", url: str = "https://example.com/redeem"):
        self.status = status
        self.request = DummyRequest(method)
        self.url = url


class FakeRespInfo:
    def __init__(self, response):
        loop = asyncio.get_running_loop()
        self.value = loop.create_future()
        self.value.set_result(response)


class FakeExpectResponse:
    def __init__(self, page):
        self.page = page

    async def __aenter__(self):
        if self.page.mode == "timeout_enter":
            raise asyncio.TimeoutError()
        return FakeRespInfo(self.page.response)

    async def __aexit__(self, exc_type, exc, tb):
        return False


class FakePage:
    def __init__(self, response=None, mode="ok"):
        self.response = response or DummyResponse(200)
        self.mode = mode

    async def goto(self, *_args, **_kwargs):
        if self.mode == "error_goto":
            raise RuntimeError("goto failed")

    async def wait_for_selector(self, *_args, **_kwargs):
        if self.mode == "error_wait":
            raise RuntimeError("selector not found")

    async def fill(self, *_args, **_kwargs):
        if self.mode == "error_fill":
            raise RuntimeError("fill failed")

    def expect_response(self, predicate, timeout):
        assert timeout == apply_credits.RESPONSE_TIMEOUT_MS
        # predicate が今回のレスポンスを受け入れるかを最低限確認
        assert predicate(self.response) is True
        return FakeExpectResponse(self)

    async def click(self, *_args, **_kwargs):
        if self.mode == "timeout_click":
            raise asyncio.TimeoutError()
        if self.mode == "error_click":
            raise RuntimeError("click failed")


class FakeTab:
    def __init__(self, url: str):
        self.url = url


class FakeContext:
    def __init__(self, pages):
        self.pages = pages


def test_load_credit_codes_skips_comments_and_blank_lines(tmp_path):
    csv = tmp_path / "credits.csv"
    csv.write_text("# comment\n\nCODE-1\n  CODE-2  \n", encoding="utf-8")

    codes = apply_credits.load_credit_codes(csv)

    assert codes == ["CODE-1", "CODE-2"]


def test_load_credit_codes_missing_file_exits(tmp_path):
    missing = tmp_path / "no-file.csv"

    with pytest.raises(SystemExit) as exc:
        apply_credits.load_credit_codes(missing)

    assert exc.value.code == 1


def test_save_log_creates_json_file(tmp_path, monkeypatch):
    monkeypatch.setattr(apply_credits, "LOGS_DIR", tmp_path / "logs")
    payload = [{"code": "C1", "status": "success"}]

    log_path = apply_credits.save_log(payload)

    assert log_path.exists()
    data = json.loads(log_path.read_text(encoding="utf-8"))
    assert data == payload


def test_load_runtime_settings_reads_env(monkeypatch):
    monkeypatch.setattr(apply_credits, "load_dotenv", lambda *_args, **_kwargs: None)
    monkeypatch.setenv("LOGIN_URL", "https://example.com/login")
    monkeypatch.setenv("READY_URL", "https://example.com/ready")
    monkeypatch.setenv("BROWSER_CHANNEL", "msedge")
    monkeypatch.setenv("LOGIN_TIMEOUT_MS", "12345")

    settings = apply_credits.load_runtime_settings()

    assert settings["login_url"] == "https://example.com/login"
    assert settings["ready_url"] == "https://example.com/ready"
    assert settings["browser_channel"] == "msedge"
    assert settings["login_timeout_ms"] == 12345


def test_load_runtime_settings_requires_login_url(monkeypatch):
    monkeypatch.setattr(apply_credits, "load_dotenv", lambda *_args, **_kwargs: None)
    monkeypatch.delenv("LOGIN_URL", raising=False)
    monkeypatch.setenv("READY_URL", "https://example.com/ready")

    with pytest.raises(ValueError) as exc:
        apply_credits.load_runtime_settings()

    assert "LOGIN_URL" in str(exc.value)


def test_load_runtime_settings_timeout_must_be_integer(monkeypatch):
    monkeypatch.setattr(apply_credits, "load_dotenv", lambda *_args, **_kwargs: None)
    monkeypatch.setenv("LOGIN_URL", "https://example.com/login")
    monkeypatch.setenv("LOGIN_TIMEOUT_MS", "not-integer")

    with pytest.raises(ValueError) as exc:
        apply_credits.load_runtime_settings()

    assert "LOGIN_TIMEOUT_MS" in str(exc.value)


def test_is_ready_url_exact_and_wildcard():
    assert (
        apply_credits._is_ready_url(
            "https://us-east-1.console.aws.amazon.com/costmanagement/home",
            "https://us-east-1.console.aws.amazon.com/costmanagement/home",
        )
        is True
    )
    assert (
        apply_credits._is_ready_url(
            "https://us-east-1.console.aws.amazon.com/costmanagement/home?x=1",
            "https://us-east-1.console.aws.amazon.com/costmanagement/home",
        )
        is False
    )
    assert (
        apply_credits._is_ready_url(
            "https://us-east-1.console.aws.amazon.com/costmanagement/home?x=1",
            "https://us-east-1.console.aws.amazon.com/costmanagement/home*",
        )
        is True
    )


def test_wait_for_ready_page_finds_matching_tab():
    context = FakeContext(
        pages=[
            FakeTab("https://idp.example.com/login"),
            FakeTab("https://us-east-1.console.aws.amazon.com/costmanagement/home?region=us-east-1"),
        ]
    )

    matched = asyncio.run(
        apply_credits.wait_for_ready_page(
            context,
            "https://us-east-1.console.aws.amazon.com/costmanagement/home*",
            timeout_ms=100,
        )
    )

    assert matched.url.startswith("https://us-east-1.console.aws.amazon.com/costmanagement/home")


def test_wait_for_ready_page_timeout():
    context = FakeContext(pages=[FakeTab("https://idp.example.com/login")])

    with pytest.raises(asyncio.TimeoutError):
        asyncio.run(
            apply_credits.wait_for_ready_page(
                context,
                "https://us-east-1.console.aws.amazon.com/costmanagement/home*",
                timeout_ms=50,
            )
        )


def test_is_billing_api_response_filters_noise_and_method():
    ok = DummyResponse(200, method="POST", url="https://example.com/redeem")
    noise = DummyResponse(200, method="POST", url="https://example.com/analytics")
    get_req = DummyResponse(200, method="GET", url="https://example.com/redeem")

    assert apply_credits._is_billing_api_response(ok) is True
    assert apply_credits._is_billing_api_response(noise) is False
    assert apply_credits._is_billing_api_response(get_req) is False


def test_apply_credit_success():
    page = FakePage(response=DummyResponse(200), mode="ok")

    result = asyncio.run(apply_credits.apply_credit(page, "CODE-OK"))

    assert result["code"] == "CODE-OK"
    assert result["status"] == "success"
    assert result["http_status"] == 200
    assert result["error"] is None


def test_apply_credit_failed_non_200():
    page = FakePage(response=DummyResponse(400), mode="ok")

    result = asyncio.run(apply_credits.apply_credit(page, "CODE-NG"))

    assert result["status"] == "failed"
    assert result["http_status"] == 400


def test_apply_credit_timeout():
    page = FakePage(response=DummyResponse(200), mode="timeout_click")

    result = asyncio.run(apply_credits.apply_credit(page, "CODE-TIMEOUT"))

    assert result["status"] == "timeout"
    assert result["http_status"] is None
    assert "以内に返りませんでした" in (result["error"] or "")


def test_apply_credit_error():
    page = FakePage(response=DummyResponse(200), mode="error_goto")

    result = asyncio.run(apply_credits.apply_credit(page, "CODE-ERR"))

    assert result["status"] == "error"
    assert result["http_status"] is None
    assert "goto failed" in (result["error"] or "")


def test_apply_credit_failed_when_error_flash_appears(monkeypatch):
    async def fake_detect(_page, timeout_ms=2000):
        return True, "クレジットの適用中に問題が発生しました"

    monkeypatch.setattr(apply_credits, "detect_error_flash", fake_detect)
    page = FakePage(response=DummyResponse(200), mode="ok")

    result = asyncio.run(apply_credits.apply_credit(page, "CODE-OK-BUT-FLASH"))

    assert result["http_status"] == 200
    assert result["status"] == "failed"
    assert "問題が発生" in (result["error"] or "")


def test_apply_credit_timeout_but_error_flash_means_failed(monkeypatch):
    async def fake_detect(_page, timeout_ms=2000):
        return True, "クレジットの適用中に問題が発生しました"

    monkeypatch.setattr(apply_credits, "detect_error_flash", fake_detect)
    page = FakePage(response=DummyResponse(200), mode="timeout_click")

    result = asyncio.run(apply_credits.apply_credit(page, "CODE-TIMEOUT-FLASH"))

    assert result["http_status"] is None
    assert result["status"] == "failed"
    assert "問題が発生" in (result["error"] or "")
