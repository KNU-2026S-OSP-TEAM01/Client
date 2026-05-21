"""
PlateSender 모듈 테스트.

실제 서버에 요청하지 않고 pytest-mock으로 requests를 mock한다.
순수 함수(parse_response 등)는 mock 없이 직접 호출해서 테스트한다.
"""
import os
import sys

import pytest
import requests

# src 폴더를 import 경로에 추가
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.client.sender import PlateSender, parse_response
from src.client.models import ServerResponse, ServerError


# ===== 가짜 응답 객체 만들기 =====

class FakeResponse:
    """requests.Response를 흉내내는 가짜 객체."""
    def __init__(self, status_code, json_data):
        self.status_code = status_code
        self._json_data = json_data

    def json(self):
        return self._json_data


# ===== parse_response 단위 테스트 (mock 없이) =====

def test_200_entry_응답_파싱():
    """200 OK + event=entry → ServerResponse(event='entry')"""
    fake = FakeResponse(200, {
        "event": "entry",
        "entered_at": "2026-05-15T10:00:00+09:00"
    })

    result = parse_response(fake)
    assert isinstance(result, ServerResponse)
    assert result.event == "entry"
    assert result.entered_at == "2026-05-15T10:00:00+09:00"


def test_200_exit_응답_파싱():
    """200 OK + event=exit → ServerResponse(event='exit', fee, duration)"""
    fake = FakeResponse(200, {
        "event": "exit",
        "fee": 3000,
        "parked_duration_minutes": 90
    })

    result = parse_response(fake)
    assert isinstance(result, ServerResponse)
    assert result.event == "exit"
    assert result.fee == 3000
    assert result.parked_duration_minutes == 90


def test_401_invalid_api_key_5_15_명세():
    """5/15 명세: {detail: 'invalid_api_key'} → ServerError"""
    fake = FakeResponse(401, {"detail": "invalid_api_key"})

    result = parse_response(fake)
    assert isinstance(result, ServerError)
    assert result.status_code == 401
    assert result.error == "invalid_api_key"


def test_401_invalid_api_key_5_3_명세_fallback():
    """5/3 명세: {error: 'invalid_api_key'} → ServerError (fallback)"""
    fake = FakeResponse(401, {"error": "invalid_api_key"})

    result = parse_response(fake)
    assert isinstance(result, ServerError)
    assert result.status_code == 401
    assert result.error == "invalid_api_key"


def test_409_parking_lot_full():
    """409 만석: {detail: 'parking_lot_full'} → ServerError"""
    fake = FakeResponse(409, {"detail": "parking_lot_full"})

    result = parse_response(fake)
    assert isinstance(result, ServerError)
    assert result.status_code == 409
    assert result.error == "parking_lot_full"


def test_400_invalid_request_with_message():
    """400 + message 필드: {error: '...', message: '...'} → ServerError"""
    fake = FakeResponse(400, {
        "error": "invalid_request",
        "message": "plate is required"
    })

    result = parse_response(fake)
    assert isinstance(result, ServerError)
    assert result.status_code == 400
    assert result.error == "invalid_request"
    assert result.message == "plate is required"


def test_5xx_server_error_기본값():
    """5xx 응답 + 본문 없음 → 'server_error' 기본값"""
    fake = FakeResponse(500, {})

    result = parse_response(fake)
    assert isinstance(result, ServerError)
    assert result.status_code == 500
    assert result.error == "server_error"


def test_4xx_기본값():
    """4xx 응답 + 본문 없음 → 'client_error' 기본값"""
    fake = FakeResponse(404, {})

    result = parse_response(fake)
    assert isinstance(result, ServerError)
    assert result.status_code == 404
    assert result.error == "client_error"


# ===== PlateSender.send() 통합 테스트 (requests mock) =====

def test_send_정상_요청_헤더_바디(mocker):
    """send() 호출 시 올바른 URL/헤더/바디로 요청해야 한다"""
    # requests.post 모킹
    mock_post = mocker.patch("src.client.sender.requests.post")
    mock_post.return_value = FakeResponse(200, {
        "event": "entry",
        "entered_at": "2026-05-15T10:00:00+09:00"
    })

    sender = PlateSender("http://test-server:8000", "test-api-key", timeout_seconds=5)
    sender.send("12가3456")

    # post가 정확한 인자로 호출됐는지
    assert mock_post.called
    call_kwargs = mock_post.call_args.kwargs

    # URL 확인
    call_args = mock_post.call_args.args
    assert call_args[0] == "http://test-server:8000/api/v1/plates"

    # 헤더 확인
    assert call_kwargs["headers"]["Authorization"] == "Bearer test-api-key"
    assert call_kwargs["headers"]["Content-Type"] == "application/json"

    # 바디 확인
    body = call_kwargs["json"]
    assert body["plate"] == "12가3456"
    assert "timestamp" in body
    # 타임존(+09:00) 포함 확인
    assert "+09:00" in body["timestamp"]


def test_send_타임아웃(mocker):
    """타임아웃 발생 시 ServerError(timeout) 반환"""
    mocker.patch(
        "src.client.sender.requests.post",
        side_effect=requests.Timeout("timed out")
    )

    sender = PlateSender("http://test:8000", "key")
    result = sender.send("12가3456")

    assert isinstance(result, ServerError)
    assert result.status_code == 0
    assert result.error == "timeout"


def test_send_연결_실패(mocker):
    """연결 실패 시 ServerError(connection_failed) 반환"""
    mocker.patch(
        "src.client.sender.requests.post",
        side_effect=requests.ConnectionError("cannot connect")
    )

    sender = PlateSender("http://test:8000", "key")
    result = sender.send("12가3456")

    assert isinstance(result, ServerError)
    assert result.status_code == 0
    assert result.error == "connection_failed"


def test_send_url_끝_슬래시_정리(mocker):
    """server_url 끝에 슬래시가 붙어도 정상 처리"""
    mock_post = mocker.patch("src.client.sender.requests.post")
    mock_post.return_value = FakeResponse(200, {"event": "entry"})

    sender = PlateSender("http://test:8000/", "key")  # 슬래시 붙음
    sender.send("12가3456")

    # 이중 슬래시 없이 호출됐는지
    call_args = mock_post.call_args.args
    assert call_args[0] == "http://test:8000/api/v1/plates"