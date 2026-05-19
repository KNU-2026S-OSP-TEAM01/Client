"""
번호판 인식 통합 클래스.
PlateDetector (YOLO) + PlateOCR (EasyOCR)을 묶어서 사용하기 쉽게 만든다.
"""
from datetime import datetime

from src.client.detector import PlateDetector
from src.client.ocr import PlateOCR
from src.client.models import PlateResult


class PlateRecognizer:
    """번호판 검출 + OCR을 합친 통합 클래스."""

    def __init__(self, model_path, use_gpu=True, conf_threshold=0.5):
        """
        Args:
            model_path: YOLO 모델 파일 경로 (.pt)
            use_gpu: GPU 사용 여부
            conf_threshold: YOLO 검출 신뢰도 임계값
        """
        self.detector = PlateDetector(model_path, conf_threshold=conf_threshold)
        self.ocr = PlateOCR(use_gpu=use_gpu)

    def recognize(self, frame):
        """
        한 프레임에서 번호판을 검출하고 OCR로 글자를 읽는다.

        Args:
            frame: OpenCV BGR 이미지 (numpy array)

        Returns:
            List[PlateResult] — 인식된 번호판 정보 리스트
            (검출됐지만 OCR이 한국 번호판 패턴 못 맞춘 건 제외)
        """
        results = []

        # 1. YOLO로 번호판 위치 찾기
        detections = self.detector.detect(frame)

        # 2. 각 검출 영역에서 OCR로 글자 읽기
        for det in detections:
            x1, y1, x2, y2 = det.bbox
            # 번호판 영역 자르기
            plate_image = frame[y1:y2, x1:x2]
            if plate_image.size == 0:
                continue

            # OCR
            plate_text, ocr_confidence = self.ocr.read(plate_image)
            if not plate_text:
                # OCR 실패 또는 한국 번호판 형식 아님
                continue

            results.append(PlateResult(
                plate_number=plate_text,
                confidence=ocr_confidence,
                bbox=det.bbox,
                timestamp=datetime.now(),
            ))

        return results