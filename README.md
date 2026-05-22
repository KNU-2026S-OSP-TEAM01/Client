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

## 프로젝트 구조

```
Client/
├── src/
│   └── client/        # 클라이언트 메인 코드
├── tests/             # 테스트 스크립트
├── requirements.txt   # 의존성 목록
├── .gitignore
├── LICENSE
└── README.md
```

## 라이선스

MIT License (LICENSE 파일 참조)