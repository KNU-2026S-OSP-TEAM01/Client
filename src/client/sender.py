"""
번호판 데이터를 Parking Lot Server로 송신하는 모듈.

백엔드 명세 (Parking-Lot-Backend/docs/ref/client-guide.md, 2026-05-15)
- POST /api/v1/plates
- Authorization: Bearer {api_key}
- Body: {"plate": "...", "timestamp": "ISO8601+09:00"}

응답 케이스:
- 200 OK: entry / exit
- 400: invalid_request
- 401: invalid_api_key
- 409: parking_lot_full (만석)
- 5xx: server_error
- Timeout / ConnectionError 별도 처리
"""
from datetime import datetime, timezone, timedelta

import requests

from src.client.models import ServerResponse, ServerError


# 한국 표준시 (KST)
KST = timezone(timedelta(hours=9))

# API 경로
PLATES_ENDPOINT = "/api/v1/plates"


class PlateSender:
    """Parking Lot Server에 번호판을 송신하는 클래스."""

    def __init__(self, server_url, api_key, timeout_seconds=5):
        """
        Args:
            server_url: 서버 주소 (예: "http://192.168.0.10:8000")
            api_key: 주차장별로 발급된 API 키
            timeout_seconds: 요청 타임아웃 (초)
        """
        # 끝에 슬래시 붙어 있으면 제거 (URL 안전하게)
        self.server_url = server_url.rstrip("/")
        self.api_key = api_key
        self.timeout = timeout_seconds

    def send(self, plate_number):
        """
        번호판을 서버에 송신한다.

        Args:
            plate_number: 번호판 문자열 (예: "12가3456")

        Returns:
            ServerResponse: 성공 (200 OK)
            ServerError: 실패 (4xx, 5xx, 네트워크 오류 등)
        """
        url = self.server_url + PLATES_ENDPOINT
        headers = {
            "Authorization": "Bearer " + self.api_key,
            "Content-Type": "application/json",
        }
        body = {
            "plate": plate_number,
            "timestamp": datetime.now(KST).isoformat(),
        }

        # HTTP 요청 (타임아웃/연결 오류는 예외로 처리)
        try:
            response = requests.post(
                url,
                headers=headers,
                json=body,
                timeout=self.timeout,
            )
        except requests.Timeout:
            return ServerError(status_code=0, error="timeout",
                               message="요청 시간 초과")
        except requests.ConnectionError:
            return ServerError(status_code=0, error="connection_failed",
                               message="서버에 연결할 수 없음")
        except requests.RequestException as e:
            return ServerError(status_code=0, error="request_failed",
                               message=str(e))

        # 응답 처리
        return parse_response(response)


def parse_response(response):
    """
    HTTP 응답을 ServerResponse 또는 ServerError로 변환한다.
    """
    status = response.status_code

    # JSON 파싱 (실패 시 빈 dict)
    try:
        data = response.json()
    except ValueError:
        data = {}

    # 200 OK: 성공
    if status == 200:
        return _parse_success(data)

    # 4xx, 5xx: 에러
    return _parse_error(status, data)


def _parse_success(data):
    """200 OK 응답을 ServerResponse로 변환."""
    event = data.get("event", "unknown")

    if event == "entry":
        return ServerResponse(
            event="entry",
            entered_at=data.get("entered_at"),
        )

    if event == "exit":
        return ServerResponse(
            event="exit",
            fee=data.get("fee"),
            parked_duration_minutes=data.get("parked_duration_minutes"),
        )

    # 알 수 없는 event
    return ServerResponse(event=event)


def _parse_error(status_code, data):
    """에러 응답을 ServerError로 변환.
    백엔드 명세가 두 버전 있어서 호환 처리:
    - 5/15 신: {"detail": "..."}
    - 5/3 구: {"error": "...", "message": "..."}
    """
    # detail 우선, error fallback
    error_code = data.get("detail") or data.get("error")
    message = data.get("message")

    # 명확한 에러 코드 없으면 status 기반으로 기본값
    if not error_code:
        if 400 <= status_code < 500:
            error_code = "client_error"
        elif 500 <= status_code < 600:
            error_code = "server_error"
        else:
            error_code = "unknown_error"

    return ServerError(
        status_code=status_code,
        error=error_code,
        message=message,
    )