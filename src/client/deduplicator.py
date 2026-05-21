"""
같은 번호판이 짧은 시간 안에 여러 번 인식되어도
서버에는 한 번만 송신되도록 중복을 거른다.

박수겸 백엔드 요구사항: "같은 번호판 재전송 금지"
"""
from datetime import datetime, timedelta


class Deduplicator:
    """번호판 재전송을 차단하는 클래스."""

    def __init__(self, cooldown_seconds=30):
        """
        Args:
            cooldown_seconds: 같은 번호판을 다시 보낼 수 있는 최소 간격(초)
        """
        self.cooldown_seconds = cooldown_seconds
        # {번호판 문자열: 마지막으로 송신한 datetime}
        self.last_sent = {}

    def should_send(self, plate_number, now=None):
        """
        이 번호판을 지금 보내야 하는지 판단한다.

        Args:
            plate_number: 번호판 문자열 (예: "12가3456")
            now: 현재 시각 (None이면 datetime.now() 사용)
                 — 테스트에서 시각을 주입할 수 있도록 인자로 받음

        Returns:
            True: 보내야 함 (처음이거나 cooldown 지남)
            False: 보내지 말 것 (최근에 보냄)
        """
        if now is None:
            now = datetime.now()

        # 처음 본 번호판이면 무조건 송신
        if plate_number not in self.last_sent:
            self.last_sent[plate_number] = now
            return True

        # 마지막 송신 시각과 비교
        elapsed = now - self.last_sent[plate_number]
        if elapsed >= timedelta(seconds=self.cooldown_seconds):
            # cooldown 지났음 → 송신 + 시각 갱신
            self.last_sent[plate_number] = now
            return True

        # cooldown 안 지났음 → 송신 안 함
        return False

    def reset(self):
        """내부 캐시를 비운다 (주로 테스트용)."""
        self.last_sent = {}