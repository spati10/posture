import cv2

print("Testing camera access...")
cap = cv2.VideoCapture(0)
print("Camera opened:", cap.isOpened())
cap.release()
