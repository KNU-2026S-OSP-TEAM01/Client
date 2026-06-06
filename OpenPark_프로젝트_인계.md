# OpenPark Client 프로젝트 인계 문서

> **목적**: Claude Desktop (Code 탭)으로 작업을 이어가기 위한 프로젝트 컨텍스트 인계
> **작성일**: 2026-06-06
> **사용자**: 김준석 (경북대 전자공학·컴공 4학년, 학번 2021111675)
> **GitHub**: Oll01

---

## 1. 프로젝트 개요 및 현재 스택

### 1.1 프로젝트 정보

OpenPark는 경북대 4학년 캡스톤 프로젝트로, **번호판 인식 기반 자동 주차 관리 시스템**이다. 김준석은 **Client 파트(번호판 인식 및 백엔드 송신)를 단독 담당**한다.

### 1.2 팀 구성 (Client 레포 기준)

| 역할 | 담당자 | GitHub |
|------|--------|--------|
| Client (번호판 인식) | 김준석 | Oll01 |
| Raspberry Pi 환경 | 김태이 | kimtaei1223 |
| Backend (PLS) | 박수겸 | suder0213 |
| CI/CD | MOJAN3543 | MOJAN3543 |

### 1.3 시스템 아키텍처

```
[차량 진입]
    ↓
[카메라 (웹캠 또는 라파+외장)]
    ↓ OpenCV 프레임
[Client (Python)]
    ├── PlateRecognizer (Detector + OCR)
    ├── Deduplicator (중복 차단)
    └── PlateSender (HTTP 송신)
    ↓ POST /api/v1/plates
[Parking Lot Server (PLS)]
    ├── FastAPI (port 8000)
    ├── PostgreSQL 16
    └── 입출차 자동 판단 + 요금 계산
```

### 1.4 기술 스택

**Client (우리 작업)**
- Python 3.11 + venv
- PyTorch 2.6.0 + CUDA 12.4 (PC) / CPU (라파)
- Ultralytics YOLOv8 (검출)
- EasyOCR (한국어 OCR)
- OpenCV 4.13.0.92 (카메라)
- requests, PyYAML
- pytest, pytest-mock (테스트)

**Backend (박수겸 담당)**
- FastAPI (Python)
- PostgreSQL 16
- SQLAlchemy + Alembic
- Docker Compose
- 카카오 로컬 API (주소 → 좌표)

### 1.5 개발 환경

- **메인 PC** (집): `C:\Users\USER\Desktop\OpenPark-Client`, RTX 4060 Ti, CUDA 12.4
- **노트북** (외부 작업용): 가벼운 의존성만 (PyTorch 등 안 깔림)
- **백엔드 (로컬 도커)**: `C:\Users\USER\Desktop\Parking-Lot-Backend` (PC에 clone되어 있음)

---

## 2. 이미 구현 완료된 핵심 기능 및 파일 구조

### 2.1 Client 파일 구조

```
C:\Users\USER\Desktop\OpenPark-Client\
├── main.py                          # 통합 실행 스크립트 (카메라 → 인식 → 송신)
├── config/
│   ├── client.example.yaml          # 설정 예제
│   └── client.yaml                  # 실제 설정 (gitignore, api_key 포함)
├── src/client/
│   ├── __init__.py
│   ├── config.py                    # YAML 로더 + ClientConfig 데이터클래스
│   ├── detector.py                  # YOLO 번호판 검출 (PlateDetector)
│   ├── ocr.py                       # EasyOCR 한국어 + 정규식 (PlateOCR)
│   ├── recognizer.py                # Detector + OCR 통합 (PlateRecognizer)
│   ├── deduplicator.py              # 중복 차단 (cooldown 30초)
│   ├── sender.py                    # HTTP 송신 (PlateSender)
│   └── models.py                    # 데이터 클래스
│       ├── PlateDetection (bbox, confidence)
│       ├── PlateResult (plate_number, confidence, bbox, timestamp)
│       ├── ServerResponse (event=entry/exit, entered_at, fee, parked_duration_minutes)
│       └── ServerError (status_code, error, message)
├── tests/                           # 57개 단위 테스트
│   ├── test_config.py               # 7개 (설정 로더)
│   ├── test_convert.py              # 6개 (AIHub → YOLO 변환)
│   ├── test_detector.py             # 3개 (검출기)
│   ├── test_ocr.py                  # 13개 (OCR 정규식, 텍스트 정리)
│   ├── test_deduplicator.py         # 8개 (cooldown 로직)
│   ├── test_sender.py               # 12개 (HTTP mock 통신)
│   ├── test_main.py                 # 8개 (handle_result 분기)
│   └── manual_check_webcam.py       # 수동 웹캠 검증 스크립트 (pytest 자동 수집 제외)
├── scripts/
│   ├── convert_aihub_to_yolo.py     # AI Hub JSON → YOLO 라벨 변환
│   ├── train_yolo.py                # YOLOv8 fine-tuning
│   ├── predict_yolo.py              # 검출 단독 추론
│   ├── predict_ocr.py               # 검출 + OCR 통합 추론
│   └── test_ocr_real.py             # 실제 번호판 OCR 검증
├── data/
│   ├── README.md
│   ├── raw/                         # gitignore (AI Hub 원본)
│   ├── processed/                   # gitignore (YOLO 형식)
│   └── test_real/                   # 실제 번호판 사진 3장 (작은 크롭, 194x259)
│       ├── 번호판1.jpeg
│       ├── 번호판2.jpeg
│       └── 번호판3.jpeg
├── models/
│   ├── best.pt                      # gitignore (학습된 YOLOv8n, 6MB)
│   └── README.md
├── docs/
│   ├── architecture.md              # 모듈 아키텍처 + 통신 흐름
│   └── raspberry-pi-setup.md        # 라파 환경 가이드 (10개 섹션)
├── runs/                            # gitignore (학습/추론 결과)
├── venv/                            # gitignore
├── requirements.txt                 # opencv-python-headless 제외함
├── README.md
├── .gitignore
└── LICENSE
```

### 2.2 백엔드 파일 구조 (참고용)

```
C:\Users\USER\Desktop\Parking-Lot-Backend\
├── docker-compose.yml               # PostgreSQL + FastAPI
├── Dockerfile
├── .env                             # KAKAO_REST_API_KEY 포함
├── alembic/                         # DB 마이그레이션
├── app/                             # FastAPI 코드
├── scripts/
│   ├── seed_integration.py          # 계정 + 주차장 생성 → api_key 발급
│   ├── get_lots.py                  # 주차장 현황 조회
│   └── seed_plates.py               # 더미 입출차 데이터 주입
└── docs/ref/
    └── client-guide.md              # 클라이언트 연동 가이드
```

### 2.3 모듈별 핵심 정보

#### PlateResult 데이터 클래스 (자주 헷갈리는 부분)
```python
@dataclass
class PlateResult:
    plate_number: str    # ⚠️ "text"가 아님!
    confidence: float
    bbox: tuple
    timestamp: datetime  # ⚠️ 필수 필드
```

#### Sender 인증 형식
```python
headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json",
}
body = {
    "plate": "12가3456",
    "timestamp": "2026-05-27T02:54:29.132700+09:00",  # KST +09:00
}
```

#### Recognizer 흐름
```
frame (1080x1920) → detector.detect() → [PlateDetection bbox 리스트]
   ↓ 각 bbox 영역 잘라냄
crop image → ocr.read() → (text, confidence)
   ↓ 정규식 검증 (^\d{2,3}[가-힣]\d{4}$)
PlateResult
```

### 2.4 백엔드 API 명세 핵심

**엔드포인트**: `POST /api/v1/plates`

**응답 케이스 (10가지 처리)**:
| 상황 | HTTP | 반환 |
|------|------|------|
| 입차 | 200 | `ServerResponse(event='entry', entered_at=...)` |
| 출차 | 200 | `ServerResponse(event='exit', fee=..., parked_duration_minutes=...)` |
| 401 | 401 | `ServerError(status_code=401, error='invalid_api_key')` |
| 만석 | 409 | `ServerError(status_code=409, error='parking_lot_full')` |
| 400 | 400 | `ServerError(status_code=400, error='invalid_request')` |
| 5xx | 5xx | `ServerError(status_code=5xx, error='server_error')` |
| 타임아웃 | 0 | `ServerError(error='timeout')` |
| 연결실패 | 0 | `ServerError(error='connection_failed')` |

**에러 키 호환**: `detail` 우선, `error` fallback (백엔드 두 버전 명세 통합)

### 2.5 완료된 PR/이슈

**머지된 PR (10개)** - 모두 main에 직접 머지됨 (Week 2 후반에 develop 도입)
- #7 환경 세팅 / #8 프로젝트 구조 / #9 데이터셋 확보
- #11 YOLO 변환 / #13 YOLOv8 학습 / #15 EasyOCR
- #17 설정 로더 / #20 Deduplicator / #22 Sender
- #24 main.py 통합 (develop으로 머지) ⭐ Week 2 완성

**열려있는 PR**:
- **PR #26**: 라파 가이드 (`docs/raspberry-pi-setup.md`) - 김태이 리뷰 진행 중, **6/5 미팅 후 반영 예정**

**Closed 이슈 (10개)** - 각 PR과 매칭

**Open 이슈 (8개)**:
- #1, #3, #6, #18 (백그라운드 작업)
- #23 main.py (PR #24와 매칭)
- #25 라파 가이드 (PR #26과 매칭)
- ⚠️ **#28** docs : 라즈베리파이 환경설정 실제화 (김태이, 2시간 전)
- ⚠️ **#29** docs : 라즈베리파이 사용에 대한 회의감 (김태이, Bug 라벨, 2시간 전) ⭐ **6/5 미팅 핵심 안건**

### 2.6 GitHub Release

- **v0.1.0-week2-model** (Pre-release): `best.pt` 자산
  - URL: `https://github.com/KNU-2026S-OSP-TEAM01/Client/releases/download/v0.1.0-week2-model/best.pt`
  - 김태이가 라파에서 wget으로 다운로드

### 2.7 검증 완료 상태

#### ✅ 완료된 검증
1. **자동 단위 테스트 57개** (14초 내 통과)
2. **PC에서 main.py 풀 실행** (카메라 + 모듈 초기화 + Q/ESC 종료)
3. **PC 캠 → 모니터에 띄운 정적 사진** (PC 카메라는 앞이 안 보이지만 화면은 띄움)
4. **백엔드 End-to-End 통신 검증** (이슈 #27에 기록)
   - 정상 입차: `12가3456` → `event='entry'`
   - 정상 출차: 같은 차 재송신 → `event='exit', fee=1000원`
   - 다중 입차: `99허9999`, `11라1111`
   - 401 검증: 잘못된 api_key
5. **OCR 단독 인식** (test_real/ 3장, 3/3 성공)
6. **YOLO 학습 성능**: mAP@50 = 0.995 (AI Hub 검증셋)

#### ⚠️ 미완료 (Week 3+에서 해결)
1. **실제 카메라 환경 (1080x1920)에서 YOLO 검출** ← **도메인 갭 문제** (김태이가 발견)
2. **실시간 차량 인식 (움직이는 차)**
3. **라파에서 풀 파이프라인 동작** (김태이 환경, 동작 안 됨)
4. **다양한 환경 (낮/밤, 햇빛/그늘)**

### 2.8 발견한 이슈와 해결

#### 해결 완료
- **PlateResult 필드명 오류**: `text` → `plate_number` (노트북에서 코드 짤 때 잘못 추측, PC 검증에서 발견)
- **opencv-python-headless 충돌**: `cv2.imshow` 작동 안 함 → requirements.txt에서 제거
- **test_webcam.py → manual_check_webcam.py**: pytest 자동 수집 분리 (수동 검증 스크립트)
- **카카오 API 503 → 502 → 200**: 키 발급 + 도메인 등록 + 카카오맵 서비스 활성화 단계별 해결

#### 미해결 (현재 진행 중)
- ⚠️ **도메인 갭**: 학습 데이터(194x259 크롭) vs 실시간 이미지(1080x1920) 크기 차이
  - 김태이 진단: 라파에서 번호판 인식 안 됨
  - 김태이 제안: (a) 모델 재학습 (고화질 포함) (b) 영상 다운사이징
  - **6/5 미팅에서 논의 예정**

---

## 3. 바로 이어서 작업해야 할 구체적인 다음 단계

### 3.1 🔥 최우선 (지금~6/5 미팅 전)

#### Task A: 김태이 새 이슈 #28, #29 본문 확인
**상태**: 미확인. 본문 모르면 6/5 미팅 준비 불가.

**필요한 작업**:
```
브라우저: https://github.com/KNU-2026S-OSP-TEAM01/Client/issues/28
브라우저: https://github.com/KNU-2026S-OSP-TEAM01/Client/issues/29
```

특히 **#29 (라즈베리파이 사용에 대한 회의감, Bug 라벨)**는 라파 플랫폼 자체 재검토 가능성. 미팅 핵심 안건.

#### Task B: PR #26 코멘트 답글
김태이가 단 코멘트 두 개:
1. PyTorch 설치 명령어 수정 (`--index-url https://download.pytorch.org/whl/cpu` 필요) → 김태이가 이미 반영하겠다고 함
2. 파일명: `test_webcam.py`로 적었는데 우리는 `manual_check_webcam.py`로 변경했음 → **우리 의도 설명 필요**

**답글 안**:
```
@kimtaei1223 파일명 관련 추가 설명드리면, 
test_webcam.py → manual_check_webcam.py로 이름 변경한 이유는 
이 스크립트가 사람이 직접 Q/ESC 눌러야 종료되는 수동 검증용이라 
pytest 자동 수집 대상에서 분리하기 위함이었습니다.
test_ 접두사 있으면 pytest -v 실행 시 자동 수집되어 무한 대기 문제가 발생합니다.
```

#### Task C: PC에서 정적 사진 검증 (도메인 갭 자체 확인)
김태이의 도메인 갭 진단을 우리도 PC에서 확인:
1. 휴대폰으로 1080p 차량 사진 5~10장 촬영
2. 모니터에 띄움
3. 노트북 웹캠으로 그 화면 인식 (PC 캠은 앞 안 보임)
4. YOLO 검출 성공률 측정

→ **김태이 진단 검증 + 6/5 미팅에 데이터 들고 가기**

### 3.2 6/5 미팅 준비 안건

**핵심 논점**:
1. **도메인 갭 해결 방향**
   - Option A: 모델 재학습 (고화질 차량 사진 데이터 추가)
   - Option B: 영상 다운사이징 (1080p → 640) — 김태이는 한계 지적
   - Option C: 카메라 위치 최적화 (번호판이 화면 30%+ 차지하도록)

2. **라즈베리파이 회의감 (#29)**
   - 라파 한계 분석 (성능, 카메라, 환경)
   - 대안 검토: PC + USB 카메라? Jetson Nano? 다른 임베디드?
   - 또는 라파 유지 + 모델 경량화 (TFLite/ONNX, Week 4 원래 계획)

3. **데이터 보강 계획**
   - 정문 데이터 수집 (Week 3 후반)
   - 또는 휴대폰 사진 기반 보강 데이터셋

4. **PR #26 머지 일정**
   - 가이드 일부 수정 (PyTorch 명령어, 파일명 협의) 후 머지

### 3.3 Week 3 작업 (5/25 ~ )

- [ ] 김태이와 라파 환경 디버깅
- [ ] 도메인 갭 해결책 실험
- [ ] 정문 또는 학교 주차장에서 실제 차 인식 테스트 데이터 수집

### 3.4 Week 4 (5/29 ~ ) - 원래 계획

- [ ] 모델 경량화 (TFLite/ONNX 변환)
- [ ] 추론 속도 3~5배 향상 목표
- [ ] **도메인 갭 해소 후 진행** (먼저 모델 자체 성능 확보)

### 3.5 Week 5 (6/5 ~ )

- [ ] 인식률 90% 달성
- [ ] 실패 케이스 분석 (낮/밤, 거리, 각도)
- [ ] 모델 추가 학습 또는 후처리 개선

### 3.6 Week 6 (6/12 ~ )

- [ ] 데모 영상 제작
- [ ] 발표 자료 (이미 `Week2_Client_검증_결과_정리.md` 초안 있음)
- [ ] 소프트웨어 저작권 등록

---

## 4. 통합 환경 실행 방법 (전체 가이드)

### 4.1 백엔드 띄우기

```powershell
cd C:\Users\USER\Desktop\Parking-Lot-Backend
docker compose up db app -d
docker compose exec app alembic upgrade head
```

**환경 변수 확인** (`.env`):
- `KAKAO_REST_API_KEY=2b7254b6524882e811b96110876ea52b` ⚠️ **재발급 필요** (채팅 노출됨)

### 4.2 주차장 생성 + api_key 발급

```powershell
cd C:\Users\USER\Desktop\Parking-Lot-Backend
python scripts/seed_integration.py
```

출력에서 `api_key` 메모.

현재 발급된 키: `adda20df2eab13f510e70d0940a3d900ce919ae9abe20ead1e4164b6222b261d`

### 4.3 Client 환경 활성화

```powershell
cd C:\Users\USER\Desktop\OpenPark-Client
.\venv\Scripts\Activate.ps1
```

### 4.4 config 작성

`config/client.yaml`:
```yaml
server:
  url: "http://localhost:8000"
  api_key: "<seed_integration.py로_발급받은_키>"
  timeout_seconds: 5

camera:
  device_id: 0

model:
  path: "models/best.pt"
  conf_threshold: 0.5

ocr:
  use_gpu: true                # 라파는 false
  min_confidence: 0.5

deduplicator:
  cooldown_seconds: 30
```

### 4.5 검증 실행 옵션

#### Option A: 자동 단위 테스트
```powershell
pytest -v
```
→ 57개 통과 확인.

#### Option B: 카메라 동작 확인
```powershell
python tests/manual_check_webcam.py
```
→ Q 또는 ESC로 종료.

#### Option C: 통합 실행
```powershell
python main.py
```
→ 카메라 → 인식 → 송신 풀 흐름.

#### Option D: Sender 단독 호출 (백엔드 통신만 검증)
```powershell
python -c "from src.client.sender import PlateSender; s = PlateSender(server_url='http://localhost:8000', api_key='<key>'); print(s.send('12가3456'))"
```

#### Option E: 백엔드 DB 상태 확인
```powershell
cd C:\Users\USER\Desktop\Parking-Lot-Backend
python scripts/get_lots.py
```

### 4.6 라파 (Week 3, 김태이 환경)

가이드 문서: `docs/raspberry-pi-setup.md` 참조.

핵심 차이:
- PyTorch 설치: `pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu`
- `config/client.yaml`의 `ocr.use_gpu: false`
- `models/best.pt`는 GitHub Release에서 wget으로 다운로드

---

## 5. 사용자(김준석) 작업 선호도

Claude Desktop에서 이어 작업할 때 참고할 사용자 선호:

### 5.1 코드 스타일
- ✅ **완전한 copy-paste 가능 코드 선호** (부분 스니펫 X)
- ✅ `@dataclass` OK, **메타클래스/`from __future__` 금지**
- ✅ 단계별 가이드 + 명령어 명확하게
- ✅ 학부 4학년 수준 (과한 추상화 X)
- ✅ 한국어 주석/문서

### 5.2 작업 방식
- 단계별로 짧게 확인하면서 진행
- 결정 옵션 줄 때 추천(⭐) 명시
- 위험한 작업 전 한 번 더 확인
- git 브랜치 의식적으로 관리

### 5.3 협업 메세지
- 정중하고 명확한 톤
- 박수겸/김태이/MOJAN3543에게 카톡 보낼 때 드래프트 미리 제시

---

## 6. 보안 주의사항 (재발급 필요)

다음 키들이 이전 대화에서 노출됨. **재발급 권장**:

1. **카카오 REST API 키**: `2b7254b6524882e811b96110876ea52b`
   - 발급처: https://developers.kakao.com/console/app/1468664/config/appKey
   - 재발급 후 백엔드 `.env`의 `KAKAO_REST_API_KEY` 갱신 + `docker compose down && up`

2. **백엔드 주차장 api_key**: `adda20df2eab13f510e70d0940a3d900ce919ae9abe20ead1e4164b6222b261d`
   - 발급처: `seed_integration.py` 재실행 (또는 백엔드에서 신규 주차장 생성)
   - dev 환경이라 큰 위험은 없지만 인지

---

## 7. 즉시 실행할 작업 (Claude Desktop에서 시작 시)

1. **이슈 #28, #29 본문 확인** (브라우저 또는 GitHub API)
2. **PR #26 코멘트 답글 작성**
3. **PC에서 정적 사진 검증 (도메인 갭 자체 확인)**
   - 휴대폰 차량 사진 준비
   - 노트북 웹캠 + 모니터에 사진 띄우기
   - YOLO 검출 성공률 측정
4. **6/5 미팅 안건 정리 (Markdown 문서)**

---

## 8. 참고 문서

### 작성된 문서 (레포 내부)
- `README.md` — 설치/실행 가이드
- `docs/architecture.md` — 모듈 아키텍처
- `docs/raspberry-pi-setup.md` — 라파 가이드 (PR #26)

### 백엔드 문서
- `Parking-Lot-Backend/docs/ref/client-guide.md` — API 명세

### 외부 자료
- 발표용 정리 문서 (이전 대화에서 생성): `Week2_Client_검증_결과_정리.md`

---
## 알려진 이슈 (해결)

- ~~`tests/test_convert.py` Line 13: `convert_aihub_to_yolo` import 미해결 (Pylance reportMissingImports)~~
  - 원인: `sys.path.insert` 런타임 주입을 Pylance 정적 분석기가 추적 못함 (모듈 자체는 정상 존재)
  - 해결: `pyrightconfig.json`에 `extraPaths: ["scripts"]` 추가

## 9. GitHub 링크 모음

- Client 레포: https://github.com/KNU-2026S-OSP-TEAM01/Client
- Backend 레포: https://github.com/KNU-2026S-OSP-TEAM01/Parking-Lot-Backend
- 이슈 #28: https://github.com/KNU-2026S-OSP-TEAM01/Client/issues/28
- 이슈 #29: https://github.com/KNU-2026S-OSP-TEAM01/Client/issues/29
- PR #26: https://github.com/KNU-2026S-OSP-TEAM01/Client/pull/26
- 이슈 #27 (검증 완료): https://github.com/KNU-2026S-OSP-TEAM01/Client/issues/27
- v0.1.0-week2-model Release: https://github.com/KNU-2026S-OSP-TEAM01/Client/releases/tag/v0.1.0-week2-model

---
## 브랜치 정책
- 작업 브랜치는 항상 develop 기준에서 분기
- PR target은 develop (main 직접 금지)
- develop → main 머지는 사람이 수동으로 진행

## 10. Claude Desktop에서 시작할 때 첫 명령어

```
이 문서 (OpenPark_프로젝트_인계.md) 보고 컨텍스트 잡았으면, 
먼저 이슈 #28, #29 본문 확인부터 도와줘. 
그 다음 6/5 미팅 안건 정리하자.
알려진 이슈해결하기
```

또는:

```
도메인 갭 검증부터 시작하자. 
PC에서 정적 사진으로 YOLO 검출 테스트하는 방법 안내해줘.
```