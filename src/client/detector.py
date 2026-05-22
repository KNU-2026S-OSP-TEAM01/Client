"""
YOLO 모델로 번호판 영역을 검출하는 모듈.
"""
import numpy as np

from src.client.models import PlateDetection


class PlateDetector:
    """YOLO 기반 번호판 검출기"""

    def __init__(self, model_path: str):
        """
        Args:
            model_path: YOLO 모델 파일 경로 (.pt)
        """
        self.model_path = model_path
        # TODO: YOLO 모델 로드
        # from ultralytics import YOLO
        # self.model = YOLO(model_path)

    def detect(self, frame: np.ndarray) -> list[PlateDetection]:
        """
        프레임에서 번호판 영역을 찾는다.

        Args:
            frame: OpenCV 이미지 (BGR)

        Returns:
            검출된 번호판 영역 리스트. 없으면 빈 리스트.
        """
        # TODO: 다음 sub-issue에서 구현
        # 1. self.model(frame)으로 추론
        # 2. 결과에서 bbox와 confidence 뽑기
        # 3. PlateDetection 리스트로 반환
        raise NotImplementedError("다음 sub-issue에서 구현")