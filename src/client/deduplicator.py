"""
같은 번호판이 연속으로 인식되는 걸 방지하는 모듈.
재전송하면 서버에서 입출차가 반전되므로 매우 중요.
"""
from datetime import datetime, timedelta


class Deduplicator:
    """중복 인식 방지기"""

    def __init__(self, cooldown_seconds: int = 30):
        """
        Args:
            cooldown_seconds: 같은 번호판을 다시 받기까지의 대기 시간(초)
        """
        self.cooldown = timedelta(seconds=cooldown_seconds)
        self.last_seen = {}  # {번호판: 마지막 인식 시각}

    def should_send(self, plate_number: str, now: datetime) -> bool:
        """
        지금 이 번호판을 서버로 보낼지 판단한다.

        Args:
            plate_number: 인식된 번호판
            now: 현재 시각

        Returns:
            True면 보냄, False면 무시
        """
        # TODO: 다음 sub-issue에서 구현
        # 1. last_seen에 번호판이 없거나 cooldown 지났으면 → True
        # 2. 아니면 → False
        # 3. True 반환할 때 last_seen 업데이트
        raise NotImplementedError("다음 sub-issue에서 구현")