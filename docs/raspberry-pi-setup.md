# 라즈베리파이 환경 세팅 가이드

OpenPark Client를 라즈베리파이에서 실행하기 위한 단계별 가이드.

> **대상**: Week 3 라파 이식 작업
> **사전 준비**: 라파 OS 세팅 완료, VNC 또는 SSH 접속 가능, 외장 USB 카메라 연결

---

## 1. Client 레포 가져오기

라파 터미널에서:

```bash
cd ~
git clone https://github.com/KNU-2026S-OSP-TEAM01/Client.git OpenPark-Client
cd OpenPark-Client
```

> 폴더 이름은 자유롭게. 가이드에서는 `~/OpenPark-Client` 로 가정한다.

---

## 2. Python 환경 세팅

### 2-1. Python 3.11 확인

```bash
python3 --version
```

> Raspberry Pi OS (64bit) 최신 버전엔 Python 3.11이 기본 설치되어 있다.
> 만약 3.11 미만이면 [공식 가이드](https://www.python.org/downloads/) 참고.

### 2-2. venv 생성 + 활성화

```bash
python3 -m venv venv
source venv/bin/activate
```

> 활성화되면 프롬프트 앞에 `(venv)` 가 붙는다.
> 이후 모든 명령어는 venv 활성화 상태에서 실행한다.

---

## 3. 의존성 설치

### 3-1. PyTorch (CPU 전용)

라파는 GPU가 없으므로 CPU 전용 PyTorch를 설치한다.

```bash
pip install torch torchvision torchaudio
```

> ⏱️ 시간: 10~20분 (네트워크 속도에 따라)

### 3-2. 나머지 패키지

```bash
pip install -r requirements.txt
```

> ⏱️ 시간: 10~20분

### 3-3. ⚠️ opencv-python-headless 충돌 대응

`requirements.txt`에서는 `opencv-python-headless`를 제외했지만, `easyocr` 같은 의존성 패키지가 자동으로 `opencv-python-headless`를 다시 설치할 수 있다. headless는 GUI 없는 서버용이라 `cv2.imshow`가 작동하지 않으므로 라파에서 화면을 띄우려면 제거해야 한다.

설치 후 확인:

```bash
pip list | grep opencv
```

만약 `opencv-python-headless`가 보이면:

```bash
pip uninstall opencv-python-headless -y
pip install opencv-python --force-reinstall
```

> 이 작업은 한 번만 하면 되지만, 다른 패키지를 추가 설치하면 headless가 다시 설치될 수 있으니 그때마다 확인.

---

## 4. 모델 파일 가져오기

`models/best.pt`는 학습된 YOLOv8 가중치 파일로, gitignore 되어 있어 레포에 포함되지 않는다.

### 옵션 A: PC에서 scp로 전송 (권장)

PC에서:

```bash
scp models/best.pt pi@<라파_IP>:/home/pi/OpenPark-Client/models/
```

### 옵션 B: USB로 복사

PC의 `models/best.pt`를 USB에 복사해서 라파에 옮긴 뒤 `~/OpenPark-Client/models/` 폴더로 이동.

### 확인

```bash
ls -la models/
```

`best.pt` 파일이 보여야 정상 (크기 약 6MB).

---

## 5. 설정 파일 작성

### 5-1. 예제 파일 복사

```bash
cp config/client.example.yaml config/client.yaml
```

### 5-2. 라파용 값 수정

`config/client.yaml`을 열어 다음 값들을 수정한다.

```bash
nano config/client.yaml
```

라파 환경 권장값:

```yaml
server:
  url: "http://<백엔드_서버_IP>:8000"   # 백엔드 팀에서 받은 주소
  api_key: "<발급받은_API_키>"          # 백엔드 팀에서 받은 키
  timeout_seconds: 5

camera:
  device_id: 0   # 외장 USB 카메라. 만약 0번이 안 잡히면 1, 2 시도

model:
  path: "models/best.pt"
  conf_threshold: 0.5

ocr:
  use_gpu: false   # ⚠️ 라파는 GPU 없으므로 반드시 false
  min_confidence: 0.5

deduplicator:
  cooldown_seconds: 30
```

> 서버 주소 / api_key는 박수겸 팀원에게 문의.

---

## 6. 카메라 동작 확인

### 6-1. 외장 카메라 인식 확인

```bash
lsusb
```

→ 카메라 모델명이 보여야 정상.

```bash
ls /dev/video*
```

→ `/dev/video0` 등이 보여야 정상. 이 숫자가 `device_id`와 매칭된다.

### 6-2. 수동 웹캠 테스트

```bash
python tests/manual_check_webcam.py
```

→ 카메라 화면이 뜨면 정상. **Q 또는 ESC**로 종료.

> 화면이 안 뜨면:
> - VNC 접속 상태에서 실행 중인지 확인 (SSH로는 GUI 못 띄움)
> - `cv2.error: ... not implemented` 에러 → 3-3 단계 (opencv-python-headless 제거) 다시 확인

---

## 7. main.py 실행

```bash
python main.py
```

### 예상 콘솔 로그

```
[12:00:00] 설정 로드 완료: config/client.yaml
[12:00:01] 번호판 인식기 초기화 중...
[12:00:30] 초기화 완료. 서버 주소: http://...
[12:00:30] 카메라 시작 (device_id=0)
[12:00:30] 종료하려면 'q' 또는 ESC 키를 누르세요.
```

> 초기화 시간: 라파는 PC보다 모델 로드가 느리므로 20~40초 걸릴 수 있다. 인내심을 가지고 기다린다.

### 종료

- **Q** 또는 **ESC**: 정상 종료
- **Ctrl+C**: 강제 종료

---

## 8. 트러블슈팅

### 8-1. 카메라가 잡히지 않을 때

```
ERROR: 카메라를 열 수 없습니다 (device_id=0)
```

대응:
1. `ls /dev/video*`로 device 번호 확인
2. `config/client.yaml`의 `camera.device_id`를 0 → 1 또는 2로 변경
3. USB 케이블 / 카메라 자체 확인

### 8-2. cv2.imshow가 작동하지 않을 때

```
cv2.error: ... The function is not implemented.
```

대응:
1. SSH가 아닌 **VNC**로 접속했는지 확인 (SSH로는 GUI 못 띄움)
2. `opencv-python-headless`가 또 설치된 건 아닌지 확인
```bash
   pip list | grep opencv
```
3. 둘 다 보이면 3-3 단계 명령어 재실행

### 8-3. PyTorch / EasyOCR 설치 실패

라파 ARM 환경에서 일부 패키지는 빌드에 시간이 오래 걸리거나 wheel이 없을 수 있다.

대응:
- 네트워크 안정한 환경에서 재시도
- 한 패키지씩 따로 설치
- 그래도 안 되면 김준석에게 문의

### 8-4. 백엔드 통신 실패

```
서버 에러 [0]: connection_failed
서버 에러 [0]: timeout
```

대응:
1. `config/client.yaml`의 `server.url`이 맞는지 확인
2. 백엔드 서버가 켜져 있는지 박수겸에게 확인
3. 네트워크 연결 (같은 LAN인지) 확인
4. `api_key`가 맞는지 확인 (401 invalid_api_key 떴을 경우)

### 8-5. 모델 파일 없음

```
ERROR: 모델 파일이 없습니다: models/best.pt
```

대응:
- 4단계 (모델 파일 가져오기)를 다시 확인
- PC의 `models/best.pt` 파일을 라파로 복사

---

## 9. 자동 실행 (선택, Week 3 후반 고려)

실 운영 환경에서 라파 부팅 시 자동으로 main.py를 실행하려면 systemd 서비스로 등록한다.
[client-guide.md](https://github.com/KNU-2026S-OSP-TEAM01/Parking-Lot-Backend/blob/develop/docs/ref/client-guide.md)의 "부팅 시 자동 실행" 섹션 참고.

---

## 10. 다음 단계 (Week 3 통합 테스트)

위 가이드대로 라파에서 `python main.py`가 정상 동작하면:

1. 실내에서 외장 카메라로 번호판 인식 테스트 (사진 또는 모형)
2. 백엔드 통신 정상 동작 확인
3. **경북대 정문에서 실제 차량 통합 테스트**

자세한 내용은 김준석에게 문의.

---

## 관련 문서

- [README.md](../README.md) — 프로젝트 개요 + PC 환경 설치
- [architecture.md](./architecture.md) — 모듈 아키텍처 + 데이터 흐름
- [백엔드 client-guide.md](https://github.com/KNU-2026S-OSP-TEAM01/Parking-Lot-Backend/blob/develop/docs/ref/client-guide.md) — 백엔드 API 명세