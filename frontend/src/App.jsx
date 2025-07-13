import React, { useRef, useState } from 'react';
import axios from 'axios';
// import WebcamComponent from './components/WebcamComponent'; // Optional use

function App() {
  const videoRef = useRef(null);
  const [feedback, setFeedback] = useState("");
  const [videoFile, setVideoFile] = useState(null);

  // Start webcam stream
  const startWebcam = () => {
    navigator.mediaDevices.getUserMedia({ video: true }).then(stream => {
      if (videoRef.current) {
        videoRef.current.srcObject = stream;
      }
    });
  };

  // Capture and send frame to backend
  const captureFrameAndSend = async () => {
    if (!videoRef.current) return;

    const video = videoRef.current;
    const canvas = document.createElement("canvas");
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    const ctx = canvas.getContext("2d");
    ctx.drawImage(video, 0, 0, canvas.width, canvas.height);

    const blob = await new Promise(resolve => canvas.toBlob(resolve, "image/jpeg", 0.95));
    const formData = new FormData();
    formData.append("frame", blob, "frame.jpg");

    try {
      const res = await axios.post("http://localhost:5000/posture", formData);
      setFeedback(res.data.feedback);
    } catch (error) {
      console.error("Webcam frame upload failed:", error);
      setFeedback("❌ Error connecting to server");
    }
  };

  // Handle file input change
  const handleVideoChange = (e) => {
    setVideoFile(e.target.files[0]);
  };

  // Upload selected video file for analysis
  const uploadVideoAndAnalyze = async () => {
    if (!videoFile) {
      alert("Please select a video file.");
      return;
    }

    const formData = new FormData();
    formData.append("video", videoFile);

    try {
      const res = await axios.post("http://localhost:5000/analyze", formData);
      setFeedback(res.data.feedback.join('\n'));
    } catch (error) {
      console.error("Video upload failed:", error);
      setFeedback("❌ Error analyzing video.");
    }
  };

  return (
    <div style={{ padding: '20px', textAlign: 'center' }}>
      <h1>🧍‍♂️ Posture Detection App</h1>

      {/* Webcam Stream */}
      <video ref={videoRef} autoPlay playsInline width="640" height="480" style={{ border: "2px solid #ccc", borderRadius: "10px" }} />
      <br />
      <button onClick={startWebcam} style={{ margin: '10px' }}>🎥 Start Webcam</button>
      <button onClick={captureFrameAndSend} style={{ margin: '10px' }}>📸 Capture Frame</button>

      <hr style={{ margin: '30px 0' }} />

      {/* Upload Video File */}
      <h3>🎬 Upload Video</h3>
      <input type="file" accept="video/*" onChange={handleVideoChange} />
      <br />
      <button onClick={uploadVideoAndAnalyze} style={{ marginTop: '10px' }}>📤 Analyze Video</button>

      <hr style={{ margin: '30px 0' }} />

      {/* Feedback Section */}
      <h3>📋 Feedback</h3>
      <pre style={{ background: "#f4f4f4", padding: "10px", borderRadius: "5px", whiteSpace: "pre-wrap" }}>
        {feedback}
      </pre>

      {/* Optionally replace this section with <WebcamComponent /> */}
      {/* <WebcamComponent /> */}
    </div>
  );
}

export default App;
