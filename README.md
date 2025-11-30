posture-detection-app
🧍‍♂️ Posture Detection App A full-stack real-time and video-based posture detection system using React, Flask, MediaPipe, and OpenCV. It detects posture issues like:

🚫 Knee over toe

⚠️ Back angle < 150°

⚠️ Neck bend > 30°

📸 Features ✅ Real-time webcam posture capture.

🎥 Upload video for full session analysis.

📊 Instant feedback (Good/Bad posture).

🔁 Rule-based logic using MediaPipe landmarks.

📂 Project Structure

posture-detection-app/ ├── frontend/ # React frontend ├── backend/ # Flask API │ ├── app.py │ └── posture_analysis.py └── README.md

🛠️ Setup Instructions ⚙️ Backend (Flask) Navigate to backend:

cd backend python -m venv venv venv\Scripts\activate # On Windows pip install -r requirements.txt python app.py

🌐 Frontend (React) Navigate to frontend:

cd frontend npm install npm start

📡API Endpoints: POST /posture – Analyze a single webcam frame.



🔍 Tech Stack: Frontend: React, react-webcam, Axios.

Backend: Flask,  OpenCV, MediaPipe.

Video Analysis: MediaPipe .



Backend: Render
🧠 Future Improvements: Real-time video streaming support.

Pose history & analytics.

User accounts for tracking progress.
