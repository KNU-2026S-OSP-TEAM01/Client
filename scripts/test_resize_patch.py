"""이슈 #28의 cv2.resize(640,640) 패치 확인 (파일별로 결과 저장).

진단용. 결과: 0/8 + false positive → 재학습 결정 근거.
"""
from pathlib import Path
import numpy as np
import cv2
from ultralytics import YOLO

img_dir = Path("data/test_cars")
resized_dir = Path("data/test_cars_resized")
resized_dir.mkdir(exist_ok=True)

# 1. 640x640 리사이즈해서 별도 폴더에 저장
for p in sorted(img_dir.glob("*.jpg")):
    raw = np.fromfile(str(p), np.uint8)
    img = cv2.imdecode(raw, cv2.IMREAD_COLOR)
    if img is None:
        print(f"읽기 실패: {p.name}")
        continue
    img_640 = cv2.resize(img, (640, 640))
    ok, buf = cv2.imencode(".jpg", img_640)
    if ok:
        buf.tofile(str(resized_dir / p.name))

# 2. 추론
m = YOLO("models/best.pt")
for p in sorted(resized_dir.glob("*.jpg")):
    r = m.predict(str(p), conf=0.1, imgsz=640, save=True, verbose=False)
    boxes = r[0].boxes
    if boxes is None:
        print(f"{p.name}: 검출 없음")
        continue
    confs = [round(c, 2) for c in boxes.conf.tolist()]
    print(f"{p.name}: 검출 {len(boxes)}개, 신뢰도 {confs}")