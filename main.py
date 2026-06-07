"""
OpenPark Client 통합 실행 스크립트.

카메라 → 번호판 인식 → 안정화 버퍼 → 중복 차단 → 서버 송신 흐름을 실행한다.

종료: 'q' 또는 ESC: 정상 종료 / Ctrl+C: 강제 종료
"""
import os
import sys
from datetime import datetime

import cv2

from src.client.config import load_config
from src.client.recognizer import PlateRecognizer
from src.client.deduplicator import Deduplicator
from src.client.sender import PlateSender
from src.client.buffer import RecognitionBuffer
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


def send_plate(plate, deduplicator, sender):
    """안정된 번호판 문자열을 받아 중복 차단 후 송신 + 응답 로그."""
    if not deduplicator.should_send(plate):
        log("  → 중복 차단 (cooldown 안)")
        return

    response = sender.send(plate)

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


def handle_result(plate_result, deduplicator, sender):
    """단일 PlateResult를 직접 처리 (기존 호환성 유지)."""
    plate = plate_result.plate_number
    confidence = plate_result.confidence
    log("인식: " + plate + " (신뢰도 " + "{:.2f}".format(confidence) + ")")
    send_plate(plate, deduplicator, sender)


def main():
    if not os.path.exists(CONFIG_PATH):
        print("ERROR: 설정 파일이 없습니다: " + CONFIG_PATH)
        print("       'config/client.example.yaml'을 복사해서 사용하세요.")
        sys.exit(1)

    config = load_config(CONFIG_PATH)
    log("설정 로드 완료: " + CONFIG_PATH)

    check_files(config)

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

    buffer = RecognitionBuffer(
        window_size=config.buffer.window_size,
        min_count=config.buffer.min_count,
        min_avg_conf=config.buffer.min_avg_conf,
        similarity_threshold=config.buffer.similarity_threshold,
        suppress_seconds=config.deduplicator.cooldown_seconds,
    )

    log("초기화 완료. 서버 주소: " + config.server.url)
    log("버퍼 설정: window=" + str(config.buffer.window_size) +
        ", min_count=" + str(config.buffer.min_count) +
        ", min_avg_conf=" + str(config.buffer.min_avg_conf) +
        ", similarity=" + str(config.buffer.similarity_threshold) +
        ", suppress=" + str(config.deduplicator.cooldown_seconds) + "s")

    cap = open_camera(config.camera.device_id)
    log("카메라 시작 (device_id=" + str(config.camera.device_id) + ")")
    log("종료하려면 'q' 또는 ESC 키를 누르세요.")

    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                log("프레임을 읽을 수 없습니다.")
                break

            results = recognizer.recognize(frame)

            # 각 검출 결과를 버퍼에 누적
            for result in results:
                buffer.add(result.plate_number, result.confidence)

            # 안정된 다수결 결과만 송신
            consensus = buffer.get_consensus()
            if consensus is not None:
                log("안정된 인식: " + consensus)
                send_plate(consensus, deduplicator, sender)
                buffer.mark_sent(consensus)

            cv2.imshow("OpenPark Client", frame)

            key = cv2.waitKey(1) & 0xFF
            if key == ord("q") or key == 27:
                log("종료 키 입력. 정리 중...")
                break

    except KeyboardInterrupt:
        log("Ctrl+C 입력. 정리 중...")

    finally:
        cap.release()
        cv2.destroyAllWindows()
        log("종료 완료.")


if __name__ == "__main__":
    main()