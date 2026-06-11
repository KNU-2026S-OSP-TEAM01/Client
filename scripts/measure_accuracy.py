"""인식률 측정 — 발표용 (선명 케이스 1~4번)."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import numpy as np
import cv2

from src.client.recognizer import PlateRecognizer

# 실제 번호판 정답 (파일명: 번호)
ANSWERS = {
    "1.jpg": "43모3246",
    "2.jpg": "62노9084",
    "3.jpg": "62노9084",
    "4.jpg": "105저7787",
}

test_dir = Path("data/accuracy_test")

recognizer = PlateRecognizer(
    model_path="models/best.pt",
    use_gpu=True,
    conf_threshold=0.25,
)

total = 0
detected = 0
ocr_correct = 0

for name, answer in ANSWERS.items():
    p = test_dir / name
    if not p.exists():
        print(f"{name}: 파일 없음")
        continue
    total += 1
    img = cv2.imdecode(np.fromfile(str(p), np.uint8), cv2.IMREAD_COLOR)
    results = recognizer.recognize(img)

    if results:
        detected += 1
        plate = results[0].plate_number
        mark = "O" if plate == answer else "X"
        if mark == "O":
            ocr_correct += 1
        print(f"{name}: 검출 O | 인식='{plate}' | 정답='{answer}' | {mark}")
    else:
        print(f"{name}: 검출 X | 정답='{answer}'")

print(f"\n검출률: {detected}/{total} = {detected/total*100:.1f}%")
print(f"OCR 정확도(전체 기준): {ocr_correct}/{total} = {ocr_correct/total*100:.1f}%")
if detected:
    print(f"OCR 정확도(검출 성공 중): {ocr_correct}/{detected} = {ocr_correct/detected*100:.1f}%")