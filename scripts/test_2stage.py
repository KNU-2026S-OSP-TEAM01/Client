"""2단계 파이프라인 (차량 → 번호판) + 시각 결과 저장.

진단용. 결과: 차량 8/8 OK, 번호판 0/8 + false positive → 재학습 결정 근거.
"""
from pathlib import Path
import numpy as np
import cv2
from ultralytics import YOLO

img_dir = Path("data/test_cars")
out_dir = Path("runs/2stage_results")
out_dir.mkdir(parents=True, exist_ok=True)

car_model = YOLO("yolov8n.pt")
plate_model = YOLO("models/best.pt")

for p in sorted(img_dir.glob("*.jpg")):
    img = cv2.imdecode(np.fromfile(str(p), np.uint8), cv2.IMREAD_COLOR)
    if img is None:
        print(f"읽기 실패: {p.name}")
        continue
    output = img.copy()

    # 1단계: 차량
    car_r = car_model.predict(img, classes=[2, 5, 7], conf=0.3, verbose=False)
    car_boxes = car_r[0].boxes
    if car_boxes is None:
        print(f"\n{p.name}: 차량 0대")
        continue
    cars = car_boxes.xyxy.cpu().numpy().astype(int)  # type: ignore[attr-defined]
    print(f"\n{p.name}: 차량 {len(cars)}대")

    for i, (x1, y1, x2, y2) in enumerate(cars):
        cv2.rectangle(output, (x1, y1), (x2, y2), (0, 255, 0), 2)
        cv2.putText(output, f"car{i+1}", (x1, y1 - 5),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

        car_crop = img[y1:y2, x1:x2]
        if car_crop.size == 0:
            continue
        cw, ch = x2 - x1, y2 - y1
        car_crop_640 = cv2.resize(car_crop, (640, 640))

        # 2단계: 번호판
        plate_r = plate_model.predict(car_crop_640, conf=0.1, imgsz=640, verbose=False)
        plate_boxes = plate_r[0].boxes
        if plate_boxes is None or len(plate_boxes) == 0:
            continue
        
        for j, box in enumerate(plate_boxes.xyxy.cpu().numpy()):  # type: ignore[attr-defined]
            px1, py1, px2, py2 = box
            px1 = int(px1 / 640 * cw) + x1
            py1 = int(py1 / 640 * ch) + y1
            px2 = int(px2 / 640 * cw) + x1
            py2 = int(py2 / 640 * ch) + y1
            conf = float(plate_boxes.conf[j])
            cv2.rectangle(output, (px1, py1), (px2, py2), (0, 0, 255), 3)
            cv2.putText(output, f"plate {conf:.2f}", (px1, py1 - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
            print(f"  차량{i+1}: 번호판 {conf:.2f}")

    ok, buf = cv2.imencode(".jpg", output)
    if ok:
        buf.tofile(str(out_dir / p.name))

print(f"\n결과 폴더: {out_dir}")