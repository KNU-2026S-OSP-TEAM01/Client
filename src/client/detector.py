"""
YOLO 모델로 영상에서 번호판을 검출하는 모듈.
"""
import cv2
import numpy as np
from ultralytics import YOLO

from src.client.models import PlateDetection


class PlateDetector:
    """YOLO 모델을 사용해 번호판 영역을 검출하는 클래스."""

    def __init__(self, model_path, conf_threshold=0.5):
        """
        Args:
            model_path: 학습된 YOLO 모델 파일 경로 (.pt)
            conf_threshold: 검출 신뢰도 임계값 (0~1)
        """
        self.model = YOLO(model_path)
        self.conf_threshold = conf_threshold

    def detect(self, frame):
        """
        한 프레임에서 번호판을 검출한다.

        Args:
            frame: OpenCV BGR 이미지 (numpy array, shape: HxWx3)

        Returns:
            List[PlateDetection] — 검출된 번호판 정보 리스트
        """
        # YOLO 추론
        results = self.model.predict(
            frame,
            conf=self.conf_threshold,
            verbose=False,   # 추론 로그 끄기
        )

        detections = []

        # results는 리스트(한 프레임당 1개)이므로 첫 번째만 사용
        for result in results:
            boxes = result.boxes
            if boxes is None:
                continue

            for box in boxes:
                # 좌표 (xyxy 형식: 픽셀 좌표)
                xyxy = box.xyxy[0].cpu().numpy()
                x1, y1, x2, y2 = int(xyxy[0]), int(xyxy[1]), int(xyxy[2]), int(xyxy[3])

                # 신뢰도
                confidence = float(box.conf[0].cpu().numpy())

                detections.append(PlateDetection(
                    bbox=(x1, y1, x2, y2),
                    confidence=confidence,
                ))

        return detections


def load_image(image_path):
    """
    이미지를 OpenCV BGR 형식으로 읽는다.
    Windows 한글 경로 대응.

    Args:
        image_path: 이미지 파일 경로

    Returns:
        numpy array 또는 None (실패 시)
    """
    image_array = np.fromfile(image_path, np.uint8)
    return cv2.imdecode(image_array, cv2.IMREAD_COLOR)