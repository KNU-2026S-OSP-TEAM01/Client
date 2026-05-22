"""웹캠 동작 확인용 임시 테스트 스크립트"""
import cv2

# 0번 카메라 (노트북 내장 또는 첫번째 웹캠)
cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("❌ 웹캠을 열 수 없습니다.")
    exit()

print("✅ 웹캠 연결 성공!")
print("ESC 또는 Q 키를 누르면 종료됩니다.")

while True:
    ret, frame = cap.read()
    if not ret:
        print("❌ 프레임을 읽을 수 없습니다.")
        break

    cv2.imshow("Webcam Test - Press Q to quit", frame)

    key = cv2.waitKey(1) & 0xFF
    if key == ord('q') or key == 27:  # Q 또는 ESC
        break

cap.release()
cv2.destroyAllWindows()
print("종료됨")