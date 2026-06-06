"""실환경 사진으로 best.pt fine-tuning (transfer learning).

기존 AI Hub 분포에서 학습된 best.pt를
실차 휴대폰 사진(40장) 분포에 맞게 추가 학습.
"""
from ultralytics import YOLO


def main():
    model = YOLO("models/best.pt")
    results = model.train(
        data="data/processed_new/dataset.yaml",
        epochs=80,
        imgsz=640,
        batch=8,
        lr0=0.001,
        patience=20,
        project="runs/finetune",
        name="exp",
        device=0,
    )
    print("\n학습 완료")
    print("새 모델 경로: runs/finetune/exp/weights/best.pt")


if __name__ == "__main__":
    main()