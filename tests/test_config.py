"""
config 모듈 테스트.

YAML 설정 파일을 정상적으로 읽고, 필수 키가 빠지면
명확한 에러를 발생시키는지 확인한다.
"""
import os
import sys
import tempfile

import pytest

# src 폴더를 import 경로에 추가
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.client.config import load_config, ClientConfig


# 정상 설정 파일 내용 (테스트용 템플릿)
VALID_CONFIG_YAML = """
server:
  url: "https://test-server.example.com"
  api_key: "test-api-key-12345"
  timeout_seconds: 10

camera:
  device_id: 1

model:
  path: "models/test.pt"
  conf_threshold: 0.6

ocr:
  use_gpu: false
  min_confidence: 0.7

deduplicator:
  cooldown_seconds: 60
"""


def write_temp_yaml(content):
    """임시 YAML 파일을 만들고 경로를 반환한다."""
    tmp = tempfile.NamedTemporaryFile(
        mode="w", suffix=".yaml", delete=False, encoding="utf-8"
    )
    tmp.write(content)
    tmp.close()
    return tmp.name


# ===== 정상 케이스 =====

def test_정상_설정_로드():
    """모든 필드가 있는 정상 YAML이 잘 로드되어야 한다"""
    path = write_temp_yaml(VALID_CONFIG_YAML)
    try:
        config = load_config(path)
        assert isinstance(config, ClientConfig)

        # server
        assert config.server.url == "https://test-server.example.com"
        assert config.server.api_key == "test-api-key-12345"
        assert config.server.timeout_seconds == 10

        # camera
        assert config.camera.device_id == 1

        # model
        assert config.model.path == "models/test.pt"
        assert config.model.conf_threshold == 0.6

        # ocr
        assert config.ocr.use_gpu is False
        assert config.ocr.min_confidence == 0.7

        # deduplicator
        assert config.deduplicator.cooldown_seconds == 60
    finally:
        os.remove(path)


def test_기본값_적용():
    """선택적 필드 누락 시 기본값이 적용되어야 한다"""
    yaml_content = """
server:
  url: "https://test.com"
  api_key: "key"

camera: {}

model:
  path: "models/best.pt"

ocr: {}

deduplicator: {}
"""
    path = write_temp_yaml(yaml_content)
    try:
        config = load_config(path)
        # 기본값 확인
        assert config.server.timeout_seconds == 5
        assert config.camera.device_id == 0
        assert config.model.conf_threshold == 0.5
        assert config.ocr.use_gpu is True
        assert config.ocr.min_confidence == 0.5
        assert config.deduplicator.cooldown_seconds == 30
    finally:
        os.remove(path)


# ===== 에러 케이스 =====

def test_파일_없으면_에러():
    """존재하지 않는 파일은 FileNotFoundError 발생"""
    with pytest.raises(FileNotFoundError):
        load_config("nonexistent_config_file.yaml")


def test_빈_파일은_에러():
    """비어있는 YAML 파일은 ValueError 발생"""
    path = write_temp_yaml("")
    try:
        with pytest.raises(ValueError):
            load_config(path)
    finally:
        os.remove(path)


def test_server_섹션_없으면_에러():
    """server 섹션이 없으면 ValueError 발생"""
    yaml_content = """
camera:
  device_id: 0
model:
  path: "models/best.pt"
ocr: {}
deduplicator: {}
"""
    path = write_temp_yaml(yaml_content)
    try:
        with pytest.raises(ValueError, match="server"):
            load_config(path)
    finally:
        os.remove(path)


def test_api_key_없으면_에러():
    """server.api_key가 없으면 ValueError 발생"""
    yaml_content = """
server:
  url: "https://test.com"

camera: {}
model:
  path: "models/best.pt"
ocr: {}
deduplicator: {}
"""
    path = write_temp_yaml(yaml_content)
    try:
        with pytest.raises(ValueError, match="api_key"):
            load_config(path)
    finally:
        os.remove(path)


def test_model_path_없으면_에러():
    """model.path가 없으면 ValueError 발생"""
    yaml_content = """
server:
  url: "https://test.com"
  api_key: "key"

camera: {}
model:
  conf_threshold: 0.5
ocr: {}
deduplicator: {}
"""
    path = write_temp_yaml(yaml_content)
    try:
        with pytest.raises(ValueError, match="model.path"):
            load_config(path)
    finally:
        os.remove(path)