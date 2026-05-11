"""
실시간 인식 상태를 보여주는 GUI.
캡처 화면 + 인식된 번호판 + 서버 응답을 표시한다.
"""


class ClientGUI:
    """실시간 인식 상태 표시 GUI"""

    def __init__(self):
        # TODO: GUI 프레임워크 선택 (Tkinter / PyQt / OpenCV창 등)
        pass

    def start(self):
        """GUI 메인 루프 시작"""
        # TODO: 다음 sub-issue에서 구현
        # 1. 웹캠 캡처 시작
        # 2. 프레임마다 recognizer.recognize() 호출
        # 3. 화면에 캡처 + 검출 bbox + 인식 텍스트 표시
        # 4. sender.send()로 서버 송신
        # 5. 서버 응답 화면에 표시
        raise NotImplementedError("다음 sub-issue에서 구현")