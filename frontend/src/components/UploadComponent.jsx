import React, { useState } from 'react';
import axios from 'axios';

function UploadComponent() {
  const [feedback, setFeedback] = useState([]);

  const handleFile = async (e) => {
    const file = e.target.files[0];
    const formData = new FormData();
    formData.append('video', file);

    const res = await axios.post('http://localhost:5000/analyze', formData);
    setFeedback(res.data);
  };

  return (
    <div>
      <h2>Upload Video</h2>
      <input type="file" onChange={handleFile} />
      <div>
        {feedback.map((f, i) => (
          <div key={i}>
            Frame {f.frame}: {f.bad_posture.join(', ') || 'Good posture'}
          </div>
        ))}
      </div>
    </div>
  );
}

export default UploadComponent;
