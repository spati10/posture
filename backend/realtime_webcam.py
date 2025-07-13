import cv2
import mediapipe as mp
import math

mp_pose = mp.solutions.pose
pose = mp_pose.Pose()
drawing = mp.solutions.drawing_utils

def angle_between(p1, p2, p3):
    a = [p1.x - p2.x, p1.y - p2.y]
    b = [p3.x - p2.x, p3.y - p2.y]
    angle = math.atan2(b[1], b[0]) - math.atan2(a[1], a[0])
    return abs(angle * 180 / math.pi)

cap = cv2.VideoCapture(0)

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    frame = cv2.flip(frame, 1)  # Optional: flip for mirror effect
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = pose.process(frame_rgb)

    feedback = ""

    if results.pose_landmarks:
        lm = results.pose_landmarks.landmark

        knee = lm[mp_pose.PoseLandmark.LEFT_KNEE]
        ankle = lm[mp_pose.PoseLandmark.LEFT_ANKLE]
        hip = lm[mp_pose.PoseLandmark.LEFT_HIP]
        shoulder = lm[mp_pose.PoseLandmark.LEFT_SHOULDER]
        ear = lm[mp_pose.PoseLandmark.LEFT_EAR]

        issues = []

        # Rule 1: Knee over toe (vertical comparison - better for squats)
        if knee.y < ankle.y - 0.02:  # small buffer
            issues.append("❌ Knee over toe")

        # Rule 2: Back angle
        back_angle = angle_between(shoulder, hip, knee)
        if back_angle < 150:
            issues.append("❌ Back < 150°")

        # Rule 3: Neck bent > 30°
        neck_angle = angle_between(ear, shoulder, hip)
        if neck_angle > 30:
            issues.append("❌ Neck > 30°")

        if not issues:
            feedback = "✅ Good posture"
        else:
            feedback = " | ".join(issues)

        drawing.draw_landmarks(frame, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)

    cv2.putText(frame, feedback.encode('ascii', 'ignore').decode(), (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2, cv2.LINE_AA)

    cv2.imshow('Posture Detection - Webcam', frame)

    if cv2.waitKey(5) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
