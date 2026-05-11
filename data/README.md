# Datasets

번호판 인식 모델 학습/검증용 데이터셋을 저장하는 디렉터리.

데이터셋 파일 자체는 git에 추적되지 않음 (`.gitignore` 처리).

## 사용 중인 데이터셋

| 이름 | 출처 | 라이선스 | 이미지 수 | 어노테이션 형식 |
|------|------|----------|-----------|----------------|
| License Plate Recognition | [Roboflow Universe](https://universe.roboflow.com/roboflow-universe-projects/license-plate-recognition-rxg4e) | CC BY 4.0 | 10,125장 | YOLO format |

## 폴더 구조

```
data/
├── README.md                  # 이 파일
└── raw/
    └── license-plate-roboflow/   # Roboflow 데이터셋
        ├── train/
        │   ├── images/
        │   └── labels/
        ├── valid/
        │   ├── images/
        │   └── labels/
        ├── test/
        │   ├── images/
        │   └── labels/
        └── data.yaml          # YOLO 설정 파일
```

## 데이터셋 선정 배경

### Phase 1: Roboflow License Plate Recognition (현재 선택)
- **선택 이유**: 즉시 다운로드 가능, MIT 라이선스 호환(CC BY 4.0), YOLO 포맷 그대로 사용 가능
- **한계**: 한국 번호판 비율이 높지 않음 → 한국 환경에서 인식률 부족할 수 있음
- **다음 단계**: 학습 후 인식률 부족하면 AI Hub 한국 데이터 추가 학습

### Phase 2 후보: AI Hub 자동차 차종/연식/번호판 인식용 영상 (보류)
- **출처**: https://aihub.or.kr/aidata/27727
- **데이터**: 한국(부천) CCTV 영상 약 2,189시간 + 번호판 크롭 10만 장
- **보류 이유**: 가입/신청 필요, 다운로드 크기 매우 큼 (수십~수백 GB)
- **활용 시점**: Roboflow로 학습 후 한국 번호판 인식률 90% 미달 시 추가 도입

### 검토했으나 제외한 옵션
- **사전학습 모델 직접 사용** (morsetechlab/yolov11-license-plate-detection 등)
  - 제외 이유: 모델 라이선스가 AGPLv3로 우리 프로젝트 MIT 라이선스와 충돌
- **가상 번호판 생성**
  - 제외 이유: 실제 환경(조명/각도/노이즈) 일반화 약함

## 사용 방법

### 1. 데이터셋 다운로드 (수동)
1. Roboflow Universe 접속: https://universe.roboflow.com/roboflow-universe-projects/license-plate-recognition-rxg4e
2. `Download Dataset` 버튼 클릭
3. Format: **YOLOv8** 선택
4. `Download zip to computer` 선택
5. 다운로드 받은 zip을 `data/raw/license-plate-roboflow/`에 압축 해제

### 2. 데이터 확인
```bash
# train 이미지 개수 확인
ls data/raw/license-plate-roboflow/train/images | wc -l
```

## 라이선스 주의사항

Roboflow 데이터셋(CC BY 4.0)을 사용하므로 모델 학습 결과물 배포 시 다음 사항 표기 필요:

> This work uses the "License Plate Recognition" dataset from Roboflow Universe (CC BY 4.0).
> Source: https://universe.roboflow.com/roboflow-universe-projects/license-plate-recognition-rxg4e