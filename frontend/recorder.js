// Simple browser audio recorder and playback logic
let mediaRecorder;
let audioChunks = [];
let audioBlob;
let audioUrl;

const recordBtn = document.getElementById('micBtn');
const playBtn = document.getElementById('playBtn');
const audioPlayer = document.getElementById('audio');

recordBtn.onclick = async function() {
  if (recordBtn.dataset.recording === 'true') {
    mediaRecorder.stop();
    recordBtn.innerText = '🎤 Mic';
    recordBtn.dataset.recording = 'false';
  } else {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    mediaRecorder = new MediaRecorder(stream);
    audioChunks = [];
    mediaRecorder.ondataavailable = e => audioChunks.push(e.data);
    mediaRecorder.onstop = () => {
      audioBlob = new Blob(audioChunks, { type: 'audio/wav' });
      audioUrl = URL.createObjectURL(audioBlob);
      audioPlayer.src = audioUrl;
      playBtn.disabled = false;
    };
    mediaRecorder.start();
    recordBtn.innerText = '⏹️ Stop';
    recordBtn.dataset.recording = 'true';
    playBtn.disabled = true;
  }
};

playBtn.onclick = function() {
  if (audioUrl) {
    audioPlayer.play();
  }
};

// To upload audioBlob to backend:
// let formData = new FormData();
// formData.append('audio', audioBlob, 'user_audio.wav');
// fetch('/your-upload-endpoint', { method: 'POST', body: formData });
