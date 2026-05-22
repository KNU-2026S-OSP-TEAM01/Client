# OpenPark Client

OpenPark 프로젝트의 클라이언트 컴포넌트.  
웹캠 또는 라즈베리파이 카메라로 차량 번호판을 인식하여 Parking Lot Server로 송신한다.

## 기술 스택

- Python 3.11
- PyTorch (CUDA 12.4)
- OpenCV
- Ultralytics YOLOv8

## 개발 환경 요구사항

- Python 3.11
- (권장) NVIDIA GPU + CUDA 지원 드라이버
- Webcam (PC 환경) 또는 Raspberry Pi Camera Module

## 설치 방법

### 1. 레포 클론 및 가상환경 생성

```bash
git clone https://github.com/KNU-2026S-OSP-TEAM01/Client.git
cd Client
py -3.11 -m venv venv
```

### 2. 가상환경 활성화

**Windows (PowerShell):**

```powershell
.\venv\Scripts\Activate.ps1
```

**macOS / Linux:**

```bash
source venv/bin/activate
```

### 3. PyTorch 설치 (GPU 환경)

```bash
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu124
```

CPU 전용 환경:

```bash
pip install torch torchvision torchaudio
```

### 4. 나머지 패키지 설치

```bash
pip install -r requirements.txt
```

### 5. 동작 확인

```bash
python tests/test_webcam.py
```

웹캠 화면이 뜨면 정상. `Q` 또는 `ESC`로 종료.

## 데이터셋 준비

번호판 검출 모델 학습용 데이터셋을 YOLO 형식으로 변환한다.

### 1. AI Hub 샘플 데이터 다운로드

1. [AI Hub - 자동차 차종/연식/번호판 인식용 영상](https://aihub.or.kr/aihubdata/data/view.do?currMenu=115&topMenu=100&dataSetSn=172) 접속
2. 회원가입 후 **샘플 데이터 다운로드** (신청 불필요)
3. 압축 해제 후 `New_sample/` 폴더를 `data/raw/aihub-vehicle-plate/`로 이동

자세한 내용은 [data/README.md](data/README.md) 참고.

### 2. YOLO 형식으로 변환

```bash
python scripts/convert_aihub_to_yolo.py
```

변환 결과:

- `data/processed/train/` — 학습용 이미지 + YOLO 라벨 (약 4,400개)
- `data/processed/val/` — 검증용 이미지 + YOLO 라벨 (약 1,100개)
- `data/processed/dataset.yaml` — YOLO 학습 설정 파일

## 모델 학습 및 추론

YOLOv8 모델을 fine-tuning하고 추론 테스트를 진행한다.

### 1. 모델 학습 (fine-tuning)

```bash
python scripts/train_yolo.py
```

- 사전학습 모델: `yolov8n.pt` (자동 다운로드)
- 에폭: 50, 이미지 크기: 640, 배치: 16
- 학습 시간: 약 30분~1시간 (NVIDIA RTX 4060 Ti 기준)
- 결과 위치:
  - `runs/detect/train/` — 학습 로그, 그래프, 예측 샘플
  - `models/best.pt` — 학습된 모델 가중치 (재사용용)

### 2. 추론 테스트

```bash
python scripts/predict_yolo.py
```

- 검증셋(val) 이미지 10장을 랜덤하게 추론
- 결과 이미지를 `runs/predict/` 폴더에 저장
- 검출된 번호판에 초록색 박스 + 신뢰도 표시

## 테스트 실행

각 모듈의 단위 테스트를 실행한다.

### 전체 테스트

```bash
pytest
```

### 모듈별 테스트

```bash
# AI Hub → YOLO 변환 함수
pytest tests/test_convert.py -v

# YOLO 번호판 검출기 (models/best.pt 필요, 없으면 자동 skip)
pytest tests/test_detector.py -v

# 웹캠 동작 확인 (수동 종료 필요: Q 또는 ESC)
python tests/test_webcam.py
```

## 프로젝트 구조

```
Client/
├── src/
│   └── client/        # 클라이언트 메인 코드
├── scripts/           # 데이터 전처리 / 학습 스크립트
├── tests/             # 테스트 스크립트
├── data/              # 데이터셋 (gitignore, README만 추적)
├── models/            # 학습된 모델 가중치 (gitignore)
├── requirements.txt   # 의존성 목록
├── .gitignore
├── LICENSE
└── README.md
```

## 라이선스

MIT License (LICENSE 파일 참조)