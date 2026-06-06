"""
OpenPark Client 통합 실행 스크립트.

카메라 → 번호판 인식 → 중복 차단 → 서버 송신 흐름을 실행한다.

실행 방법:
    python main.py

사전 준비:
    1. config/client.yaml 작성 (client.example.yaml 참고)
    2. models/best.pt 존재 (학습된 YOLOv8 모델)
    3. 카메라 연결 (PC 웹캠 또는 외장 카메라)

종료:
    'q' 또는 ESC: 정상 종료
    Ctrl+C: 강제 종료
"""
import os
import sys
from datetime import datetime

import cv2

from src.client.config import load_config
from src.client.recognizer import PlateRecognizer
from src.client.deduplicator import Deduplicator
from src.client.sender import PlateSender
from src.client.models import ServerResponse, ServerError


CONFIG_PATH = "config/client.yaml"


def log(message):
    """현재 시각을 붙여 콘솔에 출력한다."""
    now = datetime.now().strftime("%H:%M:%S")
    print("[" + now + "] " + message)


def check_files(config):
    """실행에 필요한 파일이 있는지 확인한다."""
    if not os.path.exists(config.model.path):
        print("ERROR: 모델 파일이 없습니다: " + config.model.path)
        print("       먼저 'python scripts/train_yolo.py'로 모델을 학습하세요.")
        sys.exit(1)


def open_camera(device_id):
    """카메라를 연다. 실패 시 종료."""
    cap = cv2.VideoCapture(device_id)
    if not cap.isOpened():
        print("ERROR: 카메라를 열 수 없습니다 (device_id=" + str(device_id) + ")")
        print("       카메라 연결을 확인하거나 config의 camera.device_id를 변경하세요.")
        sys.exit(1)
    return cap


def handle_result(plate_result, deduplicator, sender):
    """
    한 개의 인식 결과를 처리한다.
    - 중복 차단 확인
    - 서버 송신
    - 응답 로그
    """
    plate = plate_result.plate_number
    confidence = plate_result.confidence

    log("인식: " + plate + " (신뢰도 " + "{:.2f}".format(confidence) + ")")

    # 중복 차단 확인
    if not deduplicator.should_send(plate):
        log("  → 중복 차단 (cooldown 안)")
        return

    # 서버 송신
    response = sender.send(plate)

    # 응답 로그
    if isinstance(response, ServerResponse):
        if response.event == "entry":
            log("  → 서버 응답: entry @ " + str(response.entered_at))
        elif response.event == "exit":
            log("  → 서버 응답: exit, 요금 " + str(response.fee) +
                "원, " + str(response.parked_duration_minutes) + "분 주차")
        else:
            log("  → 서버 응답: " + str(response.event))
    elif isinstance(response, ServerError):
        log("  → 서버 에러 [" + str(response.status_code) + "]: " + response.error)
        if response.message:
            log("    메시지: " + response.message)


def main():
    # 1. 설정 로드
    if not os.path.exists(CONFIG_PATH):
        print("ERROR: 설정 파일이 없습니다: " + CONFIG_PATH)
        print("       'config/client.example.yaml'을 복사해서 사용하세요.")
        sys.exit(1)

    config = load_config(CONFIG_PATH)
    log("설정 로드 완료: " + CONFIG_PATH)

    # 2. 파일 확인
    check_files(config)

    # 3. 모듈 초기화
    log("번호판 인식기 초기화 중...")
    recognizer = PlateRecognizer(
        model_path=config.model.path,
        use_gpu=config.ocr.use_gpu,
        conf_threshold=config.model.conf_threshold,
    )

    deduplicator = Deduplicator(
        cooldown_seconds=config.deduplicator.cooldown_seconds,
    )

    sender = PlateSender(
        server_url=config.server.url,
        api_key=config.server.api_key,
        timeout_seconds=config.server.timeout_seconds,
    )

    log("초기화 완료. 서버 주소: " + config.server.url)

    # 4. 카메라 열기
    cap = open_camera(config.camera.device_id)
    log("카메라 시작 (device_id=" + str(config.camera.device_id) + ")")
    log("종료하려면 'q' 또는 ESC 키를 누르세요.")

    # 5. 메인 루프
    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                log("프레임을 읽을 수 없습니다.")
                break

            # 번호판 인식
            results = recognizer.recognize(frame)

            # 각 결과 처리
            for result in results:
                handle_result(result, deduplicator, sender)

            # 화면 표시 (확인용)
            cv2.imshow("OpenPark Client", frame)

            # 종료 키 확인 (q 또는 ESC)
            key = cv2.waitKey(1) & 0xFF
            if key == ord("q") or key == 27:  # 27 = ESC
                log("종료 키 입력. 정리 중...")
                break

    except KeyboardInterrupt:
        log("Ctrl+C 입력. 정리 중...")

    finally:
        # 자원 정리
        cap.release()
        cv2.destroyAllWindows()
        log("종료 완료.")


if __name__ == "__main__":
    main()