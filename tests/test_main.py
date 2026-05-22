"""
main.py의 handle_result 함수 단위 테스트.

handle_result는 인식 결과를 받아서:
1. Deduplicator로 중복 차단 확인
2. Sender로 송신
3. ServerResponse / ServerError 분기 로그 출력
하는 핵심 통합 로직이다.

mock을 사용해서 외부 의존성 없이 분기 로직을 검증한다.
"""
import os
import sys

import pytest

# 프로젝트 루트를 import 경로에 추가
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from main import handle_result
from src.client.models import PlateResult, ServerResponse, ServerError


# ===== 테스트용 가짜 객체 =====

class FakeDeduplicator:
    """Deduplicator 흉내내는 가짜 객체.
    should_send 값을 미리 정해놓을 수 있다."""
    def __init__(self, should_send_value):
        self.should_send_value = should_send_value
        self.called_with = None  # 어떤 번호판이 전달됐는지 기록

    def should_send(self, plate, now=None):
        self.called_with = plate
        return self.should_send_value


class FakeSender:
    """Sender 흉내내는 가짜 객체.
    send 호출 시 미리 정해놓은 응답을 반환한다."""
    def __init__(self, response):
        self.response = response
        self.called = False
        self.called_with = None

    def send(self, plate):
        self.called = True
        self.called_with = plate
        return self.response


def make_plate_result(text="12가3456", confidence=0.87):
    """테스트용 PlateResult 생성."""
    return PlateResult(
        text=text,
        confidence=confidence,
        bbox=(100, 100, 200, 200),
    )


# ===== 테스트 =====

def test_deduplicator_차단되면_sender_호출_안함(capsys):
    """Deduplicator가 False 반환하면 Sender가 호출되지 않아야 한다"""
    dedup = FakeDeduplicator(should_send_value=False)
    sender = FakeSender(response=None)

    result = make_plate_result("12가3456", 0.87)
    handle_result(result, dedup, sender)

    # Sender가 호출되지 않았어야 함
    assert sender.called is False
    # 로그에 "중복 차단" 메시지 포함
    captured = capsys.readouterr()
    assert "중복 차단" in captured.out


def test_entry_응답_정상_로그(capsys):
    """ServerResponse(entry) 받으면 'entry' 로그 출력"""
    dedup = FakeDeduplicator(should_send_value=True)
    sender = FakeSender(response=ServerResponse(
        event="entry",
        entered_at="2026-05-22T12:00:00+09:00",
    ))

    result = make_plate_result("12가3456", 0.87)
    handle_result(result, dedup, sender)

    # Sender 호출됐어야 함
    assert sender.called is True
    assert sender.called_with == "12가3456"

    # 로그에 entry 정보 포함
    captured = capsys.readouterr()
    assert "entry" in captured.out
    assert "2026-05-22T12:00:00+09:00" in captured.out


def test_exit_응답_요금_표시(capsys):
    """ServerResponse(exit) 받으면 요금과 주차 시간 로그"""
    dedup = FakeDeduplicator(should_send_value=True)
    sender = FakeSender(response=ServerResponse(
        event="exit",
        fee=3000,
        parked_duration_minutes=90,
    ))

    result = make_plate_result("12가3456", 0.87)
    handle_result(result, dedup, sender)

    # 로그에 요금/시간 포함
    captured = capsys.readouterr()
    assert "exit" in captured.out
    assert "3000" in captured.out
    assert "90" in captured.out


def test_401_에러_로그(capsys):
    """ServerError(401) 받으면 에러 코드와 메시지 로그"""
    dedup = FakeDeduplicator(should_send_value=True)
    sender = FakeSender(response=ServerError(
        status_code=401,
        error="invalid_api_key",
    ))

    result = make_plate_result("12가3456", 0.87)
    handle_result(result, dedup, sender)

    # 로그에 401, invalid_api_key 포함
    captured = capsys.readouterr()
    assert "401" in captured.out
    assert "invalid_api_key" in captured.out


def test_409_만석_에러_로그(capsys):
    """ServerError(409 parking_lot_full) 받으면 만석 로그"""
    dedup = FakeDeduplicator(should_send_value=True)
    sender = FakeSender(response=ServerError(
        status_code=409,
        error="parking_lot_full",
    ))

    result = make_plate_result("12가3456", 0.87)
    handle_result(result, dedup, sender)

    captured = capsys.readouterr()
    assert "409" in captured.out
    assert "parking_lot_full" in captured.out


def test_타임아웃_에러_로그(capsys):
    """ServerError(timeout) 받으면 타임아웃 로그"""
    dedup = FakeDeduplicator(should_send_value=True)
    sender = FakeSender(response=ServerError(
        status_code=0,
        error="timeout",
        message="요청 시간 초과",
    ))

    result = make_plate_result("12가3456", 0.87)
    handle_result(result, dedup, sender)

    captured = capsys.readouterr()
    assert "timeout" in captured.out
    # message가 있으면 로그에 포함되어야 함
    assert "요청 시간 초과" in captured.out


def test_message_없으면_메시지_라인_없음(capsys):
    """ServerError에 message가 없으면 메시지 라인이 출력되지 않아야 한다"""
    dedup = FakeDeduplicator(should_send_value=True)
    sender = FakeSender(response=ServerError(
        status_code=401,
        error="invalid_api_key",
        message=None,
    ))

    result = make_plate_result("12가3456", 0.87)
    handle_result(result, dedup, sender)

    captured = capsys.readouterr()
    # "메시지:" 라인이 안 나와야 함
    assert "메시지:" not in captured.out


def test_낮은_신뢰도도_정상_처리(capsys):
    """신뢰도가 낮아도 인식 결과로 들어오면 정상 처리한다"""
    dedup = FakeDeduplicator(should_send_value=True)
    sender = FakeSender(response=ServerResponse(event="entry"))

    result = make_plate_result("12가3456", confidence=0.51)
    handle_result(result, dedup, sender)

    # Sender 호출됐어야 함
    assert sender.called is True
    # 신뢰도 0.51 로그에 포함
    captured = capsys.readouterr()
    assert "0.51" in captured.out