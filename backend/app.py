from flask import Flask, request, jsonify
from flask_cors import CORS
import cv2
import mediapipe as mp
import numpy as np
import os
import math

app = Flask(__name__)
CORS(app)

# MediaPipe pose setup
mp_pose = mp.solutions.pose
pose = mp_pose.Pose(static_image_mode=False)
drawing = mp.solutions.drawing_utils

# Helper to calculate angle between 3 points
def calculate_angle(a, b, c):
    try:
        a = np.array([a.x, a.y])
        b = np.array([b.x, b.y])
        c = np.array([c.x, c.y])
        ba = a - b
        bc = c - b
        cosine_angle = np.dot(ba, bc) / (np.linalg.norm(ba) * np.linalg.norm(bc))
        angle = np.degrees(np.arccos(np.clip(cosine_angle, -1.0, 1.0)))
        return angle
    except:
        return None

# Analyze a single image frame
def analyze_frame(frame):
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = pose.process(frame_rgb)

    if not results.pose_landmarks:
        return "No posture detected"

    lm = results.pose_landmarks.landmark
    issues = []

    try:
        # LEFT landmarks
        lk = lm[mp_pose.PoseLandmark.LEFT_KNEE]
        la = lm[mp_pose.PoseLandmark.LEFT_ANKLE]
        lh = lm[mp_pose.PoseLandmark.LEFT_HIP]
        ls = lm[mp_pose.PoseLandmark.LEFT_SHOULDER]

        # RIGHT landmarks
        rk = lm[mp_pose.PoseLandmark.RIGHT_KNEE]
        ra = lm[mp_pose.PoseLandmark.RIGHT_ANKLE]
        rh = lm[mp_pose.PoseLandmark.RIGHT_HIP]
        rs = lm[mp_pose.PoseLandmark.RIGHT_SHOULDER]

        # Midpoints for neck/spine angle
        shoulder_mid = np.array([(ls.x + rs.x) / 2, (ls.y + rs.y) / 2])
        hip_mid = np.array([(lh.x + rh.x) / 2, (lh.y + rh.y) / 2])
        nose = np.array([lm[mp_pose.PoseLandmark.NOSE].x, lm[mp_pose.PoseLandmark.NOSE].y])

        # Rule: Detect if squatting
        is_squat = hip_mid[1] > shoulder_mid[1] + 0.1

        # Rule 1: Knee over toe (only if squatting)
        if is_squat:
            if lk.y < la.y - 0.02 or rk.y < ra.y - 0.02:
                issues.append("Knee over toe")

        # Rule 2: Back angle < 150°
        back_angle_left = calculate_angle(ls, lh, lk)
        back_angle_right = calculate_angle(rs, rh, rk)
        if (back_angle_left is not None and back_angle_left < 150) or \
           (back_angle_right is not None and back_angle_right < 150):
            issues.append("Back angle < 150°")

        # Rule 3: Neck bend > 30°
        neck_vector = nose - shoulder_mid
        spine_vector = hip_mid - shoulder_mid
        cosine_sim = np.dot(neck_vector, spine_vector) / (np.linalg.norm(neck_vector) * np.linalg.norm(spine_vector))
        neck_angle = np.degrees(np.arccos(np.clip(cosine_sim, -1.0, 1.0)))

        if 0 < neck_angle < 150:
            issues.append(f"Neck bent > 30° ({neck_angle:.1f}°)")

        # Final feedback
        if issues:
            return "❌ Bad posture:\n- " + "\n- ".join(issues)
        else:
            return "✅ Good posture"

    except Exception as e:
        return f"Error: {str(e)}"

# Analyze uploaded video
def analyze_video(video_path):
    cap = cv2.VideoCapture(video_path)
    slouch_count = 0
    good_posture_count = 0

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        result = analyze_frame(frame)
        if result.startswith("❌"):
            slouch_count += 1
        elif result.startswith("✅"):
            good_posture_count += 1

    cap.release()

    total = slouch_count + good_posture_count
    if total == 0:
        return ["Error: No detectable posture in video"]

    return [
        f"Slouching detected in {slouch_count / total * 100:.2f}% of frames.",
        f"Good posture in {good_posture_count / total * 100:.2f}% of frames."
    ]

# Route: analyze single webcam frame
@app.route('/posture', methods=['POST'])
def analyze_image():
    file = request.files['frame']
    img_bytes = np.frombuffer(file.read(), np.uint8)
    frame = cv2.imdecode(img_bytes, cv2.IMREAD_COLOR)
    feedback = analyze_frame(frame)
    return jsonify({"feedback": feedback})

# Route: analyze uploaded video
@app.route('/analyze', methods=['POST'])
def analyze_uploaded_video():
    if 'video' not in request.files:
        return jsonify({"error": "No video uploaded"}), 400

    video = request.files['video']
    temp_dir = 'temp'
    os.makedirs(temp_dir, exist_ok=True)
    video_path = os.path.join(temp_dir, video.filename)
    video.save(video_path)

    feedback = analyze_video(video_path)
    os.remove(video_path)

    return jsonify({"feedback": feedback})

# Run app
if __name__ == '__main__':
    app.run(debug=True)
