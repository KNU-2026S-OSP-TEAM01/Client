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

### 5. 설정 파일 작성

`config/client.example.yaml`을 `config/client.yaml`로 복사하고 환경에 맞게 값 수정한다.

**Windows (PowerShell):**

```powershell
Copy-Item config\client.example.yaml config\client.yaml
```

**macOS / Linux:**

```bash
cp config/client.example.yaml config/client.yaml
```

`config/client.yaml`에서 `server.url`, `server.api_key` 등을 실제 값으로 수정한다.
(이 파일은 `.gitignore`에 등록되어 있어 api_key 등 비밀 정보가 외부에 노출되지 않는다.)

### 6. 동작 확인

```bash
python tests/manual_check_webcam.py
```

웹캠 화면이 뜨면 정상. `Q` 또는 `ESC`로 종료.

## 실행 방법

전체 클라이언트를 실행한다. 카메라 → 번호판 인식 → 중복 차단 → 서버 송신 흐름이 자동으로 동작한다.

### 사전 준비

1. `config/client.yaml` 작성 (위의 "5. 설정 파일 작성" 참고)
2. `models/best.pt` 존재 (모델 학습 섹션 참고)
3. 카메라 연결 (PC 웹캠 또는 외장 카메라)
4. Parking Lot Server 동작 중 (백엔드 팀에게 확인)

### 실행

```bash
python main.py
```

실행 시 콘솔 출력 예시:

```
[12:00:00] 설정 로드 완료: config/client.yaml
[12:00:01] 번호판 인식기 초기화 중...
[12:00:05] 초기화 완료. 서버 주소: http://192.168.0.10:8000
[12:00:05] 카메라 시작 (device_id=0)
[12:00:05] 종료하려면 'q' 또는 ESC 키를 누르세요.
[12:00:08] 인식: 12가3456 (신뢰도 0.87)
[12:00:08]   → 서버 응답: entry @ 2026-05-22T12:00:08+09:00
[12:00:12] 인식: 12가3456 (신뢰도 0.85)
[12:00:12]   → 중복 차단 (cooldown 안)
```

### 종료 방법

- `q` 또는 `ESC` 키: 정상 종료 (카메라 자원 정리)
- `Ctrl+C`: 강제 종료

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

## 번호판 인식 통합 (검출 + OCR)

학습된 YOLO 모델과 EasyOCR을 결합하여 실제 번호판 문자열을 추출한다.

### 1. AI Hub 검증 이미지 추론

```bash
python scripts/predict_ocr.py
```

- 검증셋(val) 이미지 10장에서 검출 + OCR 동시 진행
- 결과 이미지를 `runs/predict_ocr/`에 저장
- ⚠️ AI Hub 데이터는 번호판이 블러 처리되어 있어 OCR 인식률 0%가 정상
  - 검출(YOLO)은 정상 작동 (mAP@50: 0.995)
  - OCR 검증은 실제 선명한 번호판 사진으로 진행 필요

### 2. EasyOCR 단독 검증 (실제 번호판)

```bash
python scripts/test_ocr_real.py
```

- `data/test_real/` 폴더의 실제 번호판 사진으로 OCR 단독 동작 확인
- 한국 번호판 패턴 (`숫자2~3자리 + 한글1자 + 숫자4자리`) 검증
- 자체 테스트 결과: 3/3 인식 성공 (구형 자가용 형식)

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

# OCR 정규식 + 텍스트 정리 함수
pytest tests/test_ocr.py -v

# 설정 파일 로더
pytest tests/test_config.py -v

# 중복 인식 방지 (Deduplicator)
pytest tests/test_deduplicator.py -v

# 서버 송신 (Sender — requests mock 사용)
pytest tests/test_sender.py -v

# 웹캠 동작 확인 (수동 종료 필요: Q 또는 ESC)
python tests/manual_check_webcam.py
```

## 프로젝트 구조

```
Client/
├── main.py            # 통합 실행 스크립트 (카메라 → 인식 → 송신)
├── src/
│   └── client/        # 클라이언트 메인 모듈
│       ├── config.py        # 설정 파일 로더
│       ├── detector.py      # YOLO 번호판 검출
│       ├── ocr.py           # EasyOCR 한국어 OCR
│       ├── recognizer.py    # Detector + OCR 통합
│       ├── deduplicator.py  # 중복 인식 방지
│       ├── sender.py        # 서버 송신
│       └── models.py        # 데이터 클래스
├── config/            # 설정 파일 (client.yaml은 gitignore)
├── scripts/           # 데이터 전처리 / 학습 스크립트
├── tests/             # 단위 테스트
├── data/              # 데이터셋 (gitignore, README만 추적)
├── models/            # 학습된 모델 가중치 (gitignore)
├── requirements.txt   # 의존성 목록
├── .gitignore
├── LICENSE
└── README.md
```

## 라이선스

MIT License (LICENSE 파일 참조)