import React, { useRef, useState, useCallback } from "react";
import Webcam from "react-webcam";
import axios from "axios";

const videoConstraints = {
  width: 640,
  height: 480,
  facingMode: "user",
};

const WebcamComponent = () => {
  const webcamRef = useRef(null);
  const [feedback, setFeedback] = useState("");
  const [cameraStarted, setCameraStarted] = useState(false);

  const captureAndAnalyze = useCallback(async () => {
    const video = webcamRef.current?.video;

    if (!video) {
      setFeedback("❌ Webcam feed not available");
      return;
    }

    const canvas = document.createElement("canvas");
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;

    const ctx = canvas.getContext("2d");
    ctx.drawImage(video, 0, 0, canvas.width, canvas.height);

    const blob = await new Promise((resolve) =>
      canvas.toBlob(resolve, "image/jpeg", 0.95)
    );

    if (!blob) {
      setFeedback("❌ Failed to capture image");
      return;
    }

    const formData = new FormData();
    formData.append("frame", blob, "frame.jpg");

    try {
      const res = await axios.post("http://localhost:5000/posture", formData);
      setFeedback(res.data.feedback);
    } catch (err) {
      console.error(err);
      setFeedback("❌ Error connecting to server");
    }
  }, []);

  return (
    <div style={{ textAlign: "center", padding: "20px" }}>
      <h2>📷 Posture Detection App</h2>

      <Webcam
        ref={webcamRef}
        audio={false}
        screenshotFormat="image/jpeg"
        videoConstraints={videoConstraints}
        width={640}
        height={480}
        onUserMedia={() => setCameraStarted(true)}
        onUserMediaError={() =>
          setFeedback("❌ Please allow camera access in your browser")
        }
        style={{
          border: "2px solid #ccc",
          borderRadius: "10px",
          marginBottom: "15px",
        }}
      />

      <br />
      <button
        onClick={captureAndAnalyze}
        disabled={!cameraStarted}
        style={{
          padding: "10px 20px",
          fontSize: "16px",
          borderRadius: "8px",
          backgroundColor: "#007bff",
          color: "white",
          border: "none",
          cursor: cameraStarted ? "pointer" : "not-allowed",
        }}
      >
        🧠 Capture & Analyze Posture
      </button>

      <p style={{ marginTop: "20px", fontSize: "18px", whiteSpace: "pre-line" }}>
        <strong>Feedback:</strong> {feedback}
      </p>
    </div>
  );
};

export default WebcamComponent;
