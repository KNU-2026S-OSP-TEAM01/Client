"""
YOLOv8 모델 fine-tuning 스크립트.

AI Hub 데이터(data/processed)로 한국 환경 번호판 검출 모델을 학습한다.

사용법:
    python scripts/train_yolo.py
"""
import os
from ultralytics import YOLO


# 학습 설정
DATASET_YAML = "data/processed/dataset.yaml"
PRETRAINED_MODEL = "yolov8n.pt"   # 가장 가벼운 모델 (라즈베리파이 호환)
EPOCHS = 50
IMAGE_SIZE = 640
BATCH_SIZE = 16
DEVICE = 0   # GPU 0번 사용. CPU만 있으면 "cpu"로 변경
PROJECT_NAME = "runs/detect"
RUN_NAME = "train"

# 최종 모델 저장 위치
MODELS_DIR = "models"
BEST_MODEL_DST = os.path.join(MODELS_DIR, "best.pt")


def train():
    """YOLOv8 모델을 fine-tuning한다."""
    print("=" * 50)
    print("YOLOv8 fine-tuning 시작")
    print(f"  데이터셋: {DATASET_YAML}")
    print(f"  사전학습 모델: {PRETRAINED_MODEL}")
    print(f"  epochs: {EPOCHS}")
    print(f"  이미지 크기: {IMAGE_SIZE}")
    print(f"  배치 크기: {BATCH_SIZE}")
    print(f"  device: {DEVICE}")
    print("=" * 50)

    # 사전학습 모델 로드
    model = YOLO(PRETRAINED_MODEL)

    # 학습 시작
    results = model.train(
        data=DATASET_YAML,
        epochs=EPOCHS,
        imgsz=IMAGE_SIZE,
        batch=BATCH_SIZE,
        device=DEVICE,
        project=PROJECT_NAME,
        name=RUN_NAME,
        exist_ok=True,   # 같은 폴더에 덮어쓰기 허용
    )

    print("\n학습 완료!")
    print(f"  결과 저장 위치: {PROJECT_NAME}/{RUN_NAME}/")

    # 학습된 best.pt 모델을 models/ 폴더로 복사
    # ultralytics가 project 경로 안에 또 하위 폴더를 만드는 경우가 있어 두 위치 모두 시도
    candidates = [
        os.path.join(PROJECT_NAME, RUN_NAME, "weights", "best.pt"),
        os.path.join(PROJECT_NAME, PROJECT_NAME, RUN_NAME, "weights", "best.pt"),
    ]
    src = None
    for c in candidates:
        if os.path.exists(c):
            src = c
            break

    if src:
        os.makedirs(MODELS_DIR, exist_ok=True)
        import shutil
        shutil.copy(src, BEST_MODEL_DST)
        print(f"  모델 복사: {src} -> {BEST_MODEL_DST}")

    return results


if __name__ == "__main__":
    train()