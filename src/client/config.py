"""
설정 파일을 읽어서 ClientConfig 객체로 반환하는 모듈.
환경별로 달라지는 값(api_key, server_url, 카메라 ID 등)을
YAML 파일로 분리하여 관리한다.
"""
from dataclasses import dataclass, field

import yaml


@dataclass
class ServerConfig:
    """Parking Lot Server 설정"""
    url: str
    api_key: str
    timeout_seconds: int = 5


@dataclass
class CameraConfig:
    """카메라 설정"""
    device_id: int = 0


@dataclass
class ModelConfig:
    """YOLO 모델 설정"""
    path: str
    conf_threshold: float = 0.5


@dataclass
class OCRConfig:
    """OCR 설정"""
    use_gpu: bool = True
    min_confidence: float = 0.5


@dataclass
class DeduplicatorConfig:
    """중복 인식 방지 설정"""
    cooldown_seconds: int = 30


@dataclass
class BufferConfig:
    """OCR 결과 안정화 버퍼 설정"""
    window_size: int = 10
    min_count: int = 5
    min_avg_conf: float = 0.7
    similarity_threshold: int = 1


@dataclass
class ClientConfig:
    """전체 Client 설정"""
    server: ServerConfig
    camera: CameraConfig
    model: ModelConfig
    ocr: OCRConfig
    deduplicator: DeduplicatorConfig
    buffer: BufferConfig = field(default_factory=BufferConfig)


def load_config(config_path):
    """
    YAML 설정 파일을 읽어서 ClientConfig 객체로 반환한다.
    """
    with open(config_path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)

    if data is None:
        raise ValueError(f"설정 파일이 비어있습니다: {config_path}")

    required_sections = ["server", "camera", "model", "ocr", "deduplicator"]
    for section in required_sections:
        if section not in data:
            raise ValueError(f"필수 설정 섹션이 없습니다: '{section}'")

    server_data = data["server"]
    if "url" not in server_data:
        raise ValueError("server.url 설정이 없습니다")
    if "api_key" not in server_data:
        raise ValueError("server.api_key 설정이 없습니다")

    model_data = data["model"]
    if "path" not in model_data:
        raise ValueError("model.path 설정이 없습니다")

    buffer_data = data.get("buffer", {}) or {}

    return ClientConfig(
        server=ServerConfig(
            url=server_data["url"],
            api_key=server_data["api_key"],
            timeout_seconds=server_data.get("timeout_seconds", 5),
        ),
        camera=CameraConfig(
            device_id=data["camera"].get("device_id", 0),
        ),
        model=ModelConfig(
            path=model_data["path"],
            conf_threshold=model_data.get("conf_threshold", 0.5),
        ),
        ocr=OCRConfig(
            use_gpu=data["ocr"].get("use_gpu", True),
            min_confidence=data["ocr"].get("min_confidence", 0.5),
        ),
        deduplicator=DeduplicatorConfig(
            cooldown_seconds=data["deduplicator"].get("cooldown_seconds", 30),
        ),
        buffer=BufferConfig(
            window_size=buffer_data.get("window_size", 10),
            min_count=buffer_data.get("min_count", 5),
            min_avg_conf=buffer_data.get("min_avg_conf", 0.7),
            similarity_threshold=buffer_data.get("similarity_threshold", 1),
        ),
    )