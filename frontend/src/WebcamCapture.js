import React, { useRef, useState, useCallback, useEffect } from "react";
import Webcam from "react-webcam";
import axios from "axios";
import "./styles.css"; // optional styling file

const WebcamCapture = () => {
  const webcamRef = useRef(null);
  const [feedback, setFeedback] = useState("");
  const [loading, setLoading] = useState(false);

  // Function to capture image and send to Flask backend
  const capture = useCallback(async () => {
    if (!webcamRef.current) return;

    const imageSrc = webcamRef.current.getScreenshot();
    if (!imageSrc) return;

    const blob = await (await fetch(imageSrc)).blob();
    const file = new File([blob], "frame.jpg", { type: "image/jpeg" });

    const formData = new FormData();
    formData.append("frame", file);

    try {
      setLoading(true);
      const response = await axios.post("http://localhost:5000/posture", formData);
      setFeedback(response.data.feedback);
    } catch (error) {
      console.error("Error sending frame to backend:", error);
      setFeedback("Error analyzing posture.");
    } finally {
      setLoading(false);
    }
  }, []);

  // Automatically analyze every 3 seconds
  useEffect(() => {
    const interval = setInterval(() => {
      capture();
    }, 3000);
    return () => clearInterval(interval);
  }, [capture]);

  return (
    <div className="container">
      <Webcam
        audio={false}
        height={360}
        width={480}
        ref={webcamRef}
        screenshotFormat="image/jpeg"
        mirrored
      />
      <div className="controls">
        <button onClick={capture}>Analyze Posture</button>
        <p className="feedback">
          {loading ? "Analyzing posture..." : feedback}
        </p>
      </div>
    </div>
  );
};

export default WebcamCapture;
