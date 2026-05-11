"""
Parking Lot Server로 번호판 데이터를 송신하는 모듈.
POST /api/v1/plates 엔드포인트 사용.
"""
import requests

from src.client.models import PlateResult, ServerResponse, ServerError


class PlateSender:
    """번호판 데이터 송신기"""

    def __init__(self, server_url: str, api_key: str):
        """
        Args:
            server_url: Parking Lot Server 주소 (예: http://localhost:8000)
            api_key: 주차장별 API 키
        """
        self.server_url = server_url
        self.api_key = api_key

    def send(self, result: PlateResult):
        """
        번호판 인식 결과를 서버로 송신한다.

        Args:
            result: 인식 결과

        Returns:
            성공 시 ServerResponse, 실패 시 ServerError
        """
        # TODO: 다음 sub-issue에서 구현
        # 1. URL: f"{self.server_url}/api/v1/plates"
        # 2. 헤더: Authorization: Bearer {api_key}
        # 3. 바디: {"plate": result.plate_number, "timestamp": ISO 8601 문자열}
        # 4. 응답 파싱:
        #    - 200: ServerResponse
        #    - 400/401: ServerError
        raise NotImplementedError("다음 sub-issue에서 구현")