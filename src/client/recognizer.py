"""
번호판 인식 메인 인터페이스.
detector(YOLO 검출) + ocr(글자 인식)을 합쳐서 사용한다.

사용 예시:
    recognizer = PlateRecognizer("models/plate_yolo.pt")
    result = recognizer.recognize(frame)  # frame은 numpy 배열
    if result:
        print(result.plate_number)
"""
import numpy as np

from src.client.models import PlateResult


class PlateRecognizer:
    """프레임 한 장에서 번호판을 인식하는 클래스"""

    def __init__(self, model_path: str):
        """
        Args:
            model_path: YOLO 모델 파일 경로 (.pt)
        """
        self.model_path = model_path
        # TODO: detector, ocr 객체 초기화 (다음 sub-issue에서)

    def recognize(self, frame: np.ndarray) -> PlateResult:
        """
        한 프레임에서 번호판을 인식한다.

        Args:
            frame: OpenCV로 캡처한 이미지 (BGR)

        Returns:
            PlateResult 객체. 번호판이 안 보이면 None.
        """
        # TODO: 다음 sub-issue에서 구현
        # 1. detector로 번호판 영역 찾기
        # 2. 영역을 잘라서 ocr로 글자 읽기
        # 3. PlateResult 만들어서 반환
        raise NotImplementedError("다음 sub-issue에서 구현")