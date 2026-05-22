"""
설정 파일을 읽어들이는 모듈.
config/client.yaml에서 api_key, 서버 주소 등을 불러온다.
"""
import yaml


def load_config(path: str = "config/client.yaml") -> dict:
    """
    YAML 설정 파일을 읽어서 딕셔너리로 반환한다.

    Args:
        path: 설정 파일 경로

    Returns:
        설정 내용 딕셔너리
    """
    # TODO: 다음 sub-issue에서 구현
    # 1. yaml 파일 열기
    # 2. yaml.safe_load로 파싱
    # 3. 필수 키 검증 (api_key, server_url 등)
    raise NotImplementedError("다음 sub-issue에서 구현")