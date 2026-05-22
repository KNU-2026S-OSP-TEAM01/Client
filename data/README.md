# Datasets

번호판 인식 모델 학습/검증용 데이터셋을 저장하는 디렉터리.

데이터셋 파일 자체는 git에 추적되지 않음 (`.gitignore` 처리).

## 사용 중인 데이터셋

| 이름 | 출처 | 라이선스 | 종류 | 용도 |
|------|------|----------|------|------|
| 자동차 차종/연식/번호판 인식용 영상 (샘플) | [AI Hub #27727](https://aihub.or.kr/aihubdata/data/view.do?currMenu=115&topMenu=100&dataSetSn=172) | AI Hub 이용약관 | 한국 차량 영상 + 번호판 bbox 어노테이션 | YOLO 검출 학습 |

## 폴더 구조

```
data/
├── README.md                          # 이 파일
└── raw/
    └── aihub-vehicle-plate/           # AI Hub 샘플 데이터셋
        ├── 원천데이터/                # 차량 이미지 (.jpg)
        │   └── 차종분류데이터/
        │       └── SUV/SUV/
        │           ├── 현대자동차/
        │           ├── 기아자동차/
        │           └── BMW/
        └── 라벨링데이터/              # 어노테이션 (.json)
            └── [라벨]차종분류_train/
                └── SUV/
                    ├── 현대자동차/
                    ├── 기아자동차/
                    └── BMW/
```

## 어노테이션 구조

각 이미지에 대응하는 JSON 파일에 차량 정보와 번호판 위치가 함께 들어있다.

### JSON 예시
```json
{
  "imagePath": "소명지하차도_옆_...-1035.jpg",
  "car": {
    "bbox": [[1179.05, 582.44], [1431.98, 918.37]],
    "imagePath": "SUV/현대자동차/SUV_팰리세이드-876.jpg",
    "attributes": {
      "brand": "현대자동차",
      "color": "흰색",
      "model": "SUV_팰리세이드",
      "year": "2019-2020"
    }
  },
  "plate": {
    "bbox": [[1317.59, 887.01], [1374.62, 903.41]]
  },
  "id": "8479e972-...",
  "videoName": "소명지하차도_옆_...-002.mp4",
  "frameNo": 1035,
  "weather": "박무,연무"
}
```

### 핵심 필드
- **`plate.bbox`**: 번호판 영역 좌표 — `[[x1, y1], [x2, y2]]` 형식 → **YOLO 학습에 사용**
- **`car.bbox`**: 차량 영역 좌표 (참고용, 현재 사용 X)
- **`weather`**: 날씨 정보 (다양한 환경 학습에 도움)

> **주의**: 이 데이터셋에는 번호판 텍스트(번호값) 정보는 없음. 번호판 위치만 학습 가능.

## 데이터셋 선정 배경

### 최종 선택: AI Hub 자동차 차종/연식/번호판 인식용 영상 (샘플)
- **선택 이유**:
  - 한국 도로 환경 이미지 (CCTV 영상 프레임)
  - 다양한 날씨/시간대/차종 포함
  - 번호판 bbox 어노테이션 제공 → YOLO 검출 학습 가능
  - 샘플 데이터는 회원가입만으로 즉시 다운로드 가능 (정식 신청 절차 없음)
- **데이터 규모**: 약 5,500장 (학부 프로젝트 수준에 충분)

### 검토했으나 제외한 옵션

#### Roboflow License Plate Recognition (~10,125장)
- **제외 이유**: 외국 번호판 위주 (미국/유럽/베트남 등), 한국 환경 미반영

#### 사전학습 모델 직접 사용 (morsetechlab/yolov11-license-plate-detection 등)
- **제외 이유**: 모델 라이선스가 AGPLv3로 우리 프로젝트 MIT 라이선스와 충돌

#### 가상 번호판 합성
- **제외 이유**: 실제 환경(조명/각도/노이즈) 일반화 약함

## OCR 처리 방식

번호판 텍스트 인식은 별도 데이터셋 없이 **EasyOCR**의 사전학습 한국어 모델을 사용한다.

- 라이브러리: [EasyOCR](https://github.com/JaidedAI/EasyOCR) (Apache 2.0)
- 추가 학습 없이 한국어 인식 가능
- 후처리로 한국 번호판 패턴(숫자2-한글1-숫자4) 검증

## 사용 방법

### 1. 데이터셋 다운로드 (수동)
1. AI Hub 접속: https://aihub.or.kr/aihubdata/data/view.do?currMenu=115&topMenu=100&dataSetSn=172
2. 회원가입 + 본인 인증
3. 페이지에서 **샘플 데이터 다운로드** 버튼 클릭 (신청 불필요)
4. 다운로드 받은 zip을 압축 해제하면 `New_sample/` 폴더 생성
5. `New_sample/` 폴더를 `data/raw/` 안으로 이동하고 이름을 **`aihub-vehicle-plate`** 로 변경

### 2. 데이터 확인
```powershell
# 이미지 개수 확인
ls data\raw\aihub-vehicle-plate\원천데이터 -Recurse -Filter *.jpg | Measure-Object

# JSON 개수 확인
ls data\raw\aihub-vehicle-plate\라벨링데이터 -Recurse -Filter *.json | Measure-Object
```

### 3. 다음 단계 (YOLO 학습용 변환)
- AI Hub JSON 형식을 YOLO txt 형식으로 변환 필요
- 변환 스크립트는 다음 sub-issue (`feat: YOLO 모델 fine-tuning`)에서 작성

## 라이선스 주의사항

AI Hub 데이터를 사용하므로, 결과물 배포 시 다음 사항 표기 필요:

> 본 결과물은 과학기술정보통신부의 재원으로 한국지능정보사회진흥원의 지원을 받아  
> 구축된 "자동차 차종/연식/번호판 인식용 영상" 데이터셋을 활용하였음.  
> Source: https://aihub.or.kr/aihubdata/data/view.do?currMenu=115&topMenu=100&dataSetSn=172