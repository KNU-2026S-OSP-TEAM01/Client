"""
Client 패키지.
번호판 인식 → 서버 송신을 담당하는 모듈 모음.
"""
from src.client.models import (
    PlateDetection,
    PlateResult,
    ServerResponse,
    ServerError,
)