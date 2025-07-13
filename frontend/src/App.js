import React, { useRef, useState } from 'react';
import './App.css';

function App() {
  const videoRef = useRef(null);
  const [feedback, setFeedback] = useState('');

  const startCamera = async () => {
    const stream = await navigator.mediaDevices.getUserMedia({ video: true });
    videoRef.current.srcObject = stream;
  };

  const captureAndAnalyze = async () => {
    const canvas = document.createElement('canvas');
    canvas.width = videoRef.current.videoWidth;
    canvas.height = videoRef.current.videoHeight;
    const ctx = canvas.getContext('2d');
    ctx.drawImage(videoRef.current, 0, 0, canvas.width, canvas.height);

    const blob = await new Promise(resolve => canvas.toBlob(resolve, 'image/jpeg'));
    const formData = new FormData();
    formData.append('frame', blob, 'frame.jpg');

    try {
      const res = await fetch('http://localhost:5000/posture', {
        method: 'POST',
        body: formData,
      });
      const data = await res.json();
      setFeedback(data.feedback);
    } catch (err) {
      setFeedback('Error connecting to server');
    }
  };

  return (
    <div className="App">
      <h1>Posture Detection App</h1>
      <video ref={videoRef} autoPlay className="video" />
      <div>
        <button onClick={startCamera}>Start Camera</button>
        <button onClick={captureAndAnalyze}>Capture & Analyze Posture</button>
      </div>
      <div className="feedback"><strong>Feedback:</strong> {feedback}</div>
    </div>
  );
}

export default App;
