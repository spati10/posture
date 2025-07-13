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

def analyze_posture(video_path):
    cap = cv2.VideoCapture(video_path)
    results = []

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        output = pose.process(frame_rgb)

        bad_posture = []

        if output.pose_landmarks:
            landmarks = output.pose_landmarks.landmark

            left_knee = landmarks[mp_pose.PoseLandmark.LEFT_KNEE]
            left_ankle = landmarks[mp_pose.PoseLandmark.LEFT_ANKLE]
            left_hip = landmarks[mp_pose.PoseLandmark.LEFT_HIP]
            left_shoulder = landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER]
            left_ear = landmarks[mp_pose.PoseLandmark.LEFT_EAR]

            # Rule 1: Knee over toe
            if left_knee.x < left_ankle.x:
                bad_posture.append("Knee over toe")

            # Rule 2: Back angle
            back_angle = angle_between(left_shoulder, left_hip, left_knee)
            if back_angle < 150:
                bad_posture.append("Back angle < 150 deg")

            # Rule 3: Neck bend
            neck_angle = angle_between(left_ear, left_shoulder, left_hip)
            if neck_angle > 30:
                bad_posture.append("Neck bent > 30 deg")

        results.append({
            "frame": int(cap.get(cv2.CAP_PROP_POS_FRAMES)),
            "bad_posture": bad_posture
        })

    cap.release()
    return results
