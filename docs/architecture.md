# OpenPark Client 아키텍처

OpenPark Client의 모듈 구성과 데이터 흐름을 정리한 문서.

---

## 시스템 전체 구조

```
┌─────────────────────────────────────────────────────────────┐
│                       main.py (진입점)                       │
│                                                             │
│  1. ClientConfig 로드  →  2. 모듈 초기화  →  3. 메인 루프    │
└─────────────────────────────────────────────────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        ▼                     ▼                     ▼
   ┌─────────┐         ┌──────────────┐      ┌──────────┐
   │ Camera  │ ──→     │  Recognizer  │ ──→  │ Sender   │ ──→ 백엔드
   │ (cv2)   │ frame   │              │      │          │
   └─────────┘         │ ┌──────────┐ │      └──────────┘
                       │ │ Detector │ │            │
                       │ │ (YOLO)   │ │            ▼
                       │ └──────────┘ │      ┌──────────────┐
                       │      ↓       │      │ Deduplicator │
                       │ ┌──────────┐ │      │ (cooldown)   │
                       │ │ OCR      │ │      └──────────────┘
                       │ │ (EasyOCR)│ │
                       │ └──────────┘ │
                       └──────────────┘
```

---

## 모듈별 역할

### 1. `src/client/config.py` — 설정 로더
- `ClientConfig` 데이터 클래스 (server, camera, model, ocr, deduplicator 그룹)
- `load_config(path)`: YAML 파일을 읽어 ClientConfig 객체 반환
- 필수 키 검증, 선택적 필드는 기본값 자동 적용

### 2. `src/client/detector.py` — 번호판 검출
- `PlateDetector`: YOLOv8 모델 래퍼
- 입력: OpenCV 프레임 (numpy array)
- 출력: `List[PlateDetection]` (bbox + 신뢰도)
- 학습된 모델: `models/best.pt` (mAP@50: 0.995)

### 3. `src/client/ocr.py` — 번호판 문자 인식
- `PlateOCR`: EasyOCR(한국어+영어) 래퍼
- `clean_text(text)`: 공백/특수문자 제거
- `is_valid_korean_plate(text)`: 한국 번호판 정규식 검증
  - 패턴: `^\d{2,3}[가-힣]\d{4}$`

### 4. `src/client/recognizer.py` — 통합 인식기
- `PlateRecognizer`: Detector + OCR 결합
- 메서드: `recognize(frame)` → `List[PlateResult]`
- 흐름: YOLO 검출 → 검출 영역 잘라내기 → OCR → 유효한 번호판만 반환

### 5. `src/client/deduplicator.py` — 중복 차단
- `Deduplicator`: 같은 번호판 재송신 방지
- `should_send(plate, now=None)`: 송신 여부 판단
- 내부 자료구조: `{번호판: 마지막 송신 시각}` 딕셔너리
- 기본 cooldown: 30초

### 6. `src/client/sender.py` — 백엔드 송신
- `PlateSender`: HTTP POST로 Parking Lot Server에 송신
- `send(plate)` → `ServerResponse` 또는 `ServerError`
- 처리 케이스: 200/400/401/409/5xx/타임아웃/연결실패
- 백엔드 명세 두 버전 호환 (`detail` 우선, `error` fallback)

### 7. `src/client/models.py` — 데이터 클래스
- `PlateDetection`: bbox + confidence
- `PlateResult`: plate_number + confidence + bbox + timestamp
- `ServerResponse`: event(entry/exit) + entered_at/fee/duration
- `ServerError`: status_code + error + message

### 8. `main.py` — 통합 실행 스크립트
- 설정 로드 → 모듈 초기화 → 카메라 루프
- `handle_result()`: 인식 결과를 Deduplicator + Sender로 처리
- 종료 처리: Q/ESC/Ctrl+C, 카메라 자원 안전 해제

---

## 데이터 흐름

### 한 프레임 처리 흐름

```
[카메라]
   ↓ ret, frame = cap.read()
[OpenCV 프레임 (BGR numpy array)]
   ↓ recognizer.recognize(frame)
[List[PlateResult]]
   ↓ 각 결과마다 handle_result()
[Deduplicator.should_send(plate)]
   ↓ True인 경우만
[Sender.send(plate)]
   ↓ HTTP POST
[Parking Lot Server]
   ↓
[ServerResponse 또는 ServerError]
   ↓
[콘솔 로그 출력]
```

### 백엔드 통신 상세

```
요청:
  POST {server_url}/api/v1/plates
  Authorization: Bearer {api_key}
  Content-Type: application/json
  
  {
    "plate": "12가3456",
    "timestamp": "2026-05-23T12:00:00+09:00"
  }

응답 (입차):
  200 OK
  {
    "event": "entry",
    "entered_at": "2026-05-23T12:00:00+09:00"
  }

응답 (출차):
  200 OK
  {
    "event": "exit",
    "fee": 3000,
    "parked_duration_minutes": 90
  }
```

자세한 응답 케이스는 [백엔드 클라이언트 가이드](https://github.com/KNU-2026S-OSP-TEAM01/Parking-Lot-Backend/blob/develop/docs/ref/client-guide.md) 참고.

---

## 책임 분리 원칙

각 모듈은 단일 책임을 갖도록 설계:

| 모듈 | 단일 책임 |
|------|---------|
| Config | YAML 파싱 + 검증 |
| Detector | 번호판 위치 찾기 |
| OCR | 문자 인식 + 정규식 검증 |
| Recognizer | 검출 + OCR 통합 (영역 자르기 등) |
| Deduplicator | 중복 차단 판단 |
| Sender | HTTP 송신 + 응답 변환 |
| main.py | 위 모듈을 조립한 실행 흐름 |

이 분리 덕분에:
- 각 모듈을 독립적으로 단위 테스트 가능 (총 57개 테스트)
- 백엔드 명세 변경 시 Sender만 수정하면 됨
- 다른 OCR 라이브러리로 교체 시 OCR 모듈만 수정

---

## 외부 의존성

| 라이브러리 | 용도 | 버전 |
|----------|-----|------|
| `ultralytics` | YOLOv8 모델 추론 | 8.4.48 |
| `opencv-python` | 카메라 입출력 + 이미지 처리 | 4.13.0.92 |
| `easyocr` | 한국어 OCR | 1.7.2 |
| `requests` | HTTP 클라이언트 | 2.33.1 |
| `PyYAML` | 설정 파일 파싱 | 6.0.3 |
| `pytorch` | EasyOCR/YOLO의 백엔드 (GPU 가속) | 2.6.0+cu124 |

자세한 버전은 `requirements.txt` 참고.

---

## 환경별 설정

| 환경 | server.url | camera.device_id | ocr.use_gpu |
|------|-----------|-----------------|------------|
| PC 개발 | localhost:8000 또는 박수겸 서버 | 0 (웹캠) | true (NVIDIA GPU) |
| 라파 운영 | Parking Lot Server IP | 0 또는 1 (외장 USB) | false (CPU) |

자세한 설정은 `config/client.example.yaml` 참고.

---

## 관련 문서

- [README.md](../README.md) — 설치 및 실행 방법
- [백엔드 API 명세](https://github.com/KNU-2026S-OSP-TEAM01/Parking-Lot-Backend/blob/develop/docs/ref/client-guide.md)