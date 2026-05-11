"""
데이터 클래스 모음.
Client 모듈들이 주고받는 데이터 구조를 정의한다.
"""
from dataclasses import dataclass
from datetime import datetime


@dataclass
class PlateDetection:
    """YOLO가 찾은 번호판 영역"""
    bbox: tuple        # (x1, y1, x2, y2)
    confidence: float  # 검출 신뢰도 0.0 ~ 1.0


@dataclass
class PlateResult:
    """번호판 인식 최종 결과 (검출 + OCR)"""
    plate_number: str  # 번호판 문자열 (공백 제거됨)
    confidence: float  # OCR 신뢰도
    bbox: tuple        # (x1, y1, x2, y2)
    timestamp: datetime  # 인식 시각


@dataclass
class ServerResponse:
    """Parking Lot Server 응답"""
    event: str  # "entry" 또는 "exit"
    entered_at: datetime = None      # 입차일 때
    fee: int = None                  # 출차일 때 요금(원)
    parked_duration_minutes: int = None  # 출차일 때 주차시간(분)


@dataclass
class ServerError:
    """Server 에러 응답"""
    status_code: int  # 400, 401 등
    error: str        # 에러 코드
    message: str = None