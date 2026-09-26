# 07. Dependencies, Runtime & Deployment Setup

## Dependencies Analysis (`requirements.txt`)

```text
# Voice Processing Dependencies
realtimetts[orpheus]
RealtimeSTT
faster-whisper
requests
python-dotenv
openai

# Audio Processing
soundfile
numpy

# Async Support
asyncio

# Logging
colorlog

# Optional: For better performance
torch
transformers
```

### Dependency Roles:
1. `RealtimeSTT`: Real-time audio recording, WebRTC VAD, Silero VAD, and transcription thread management.
2. `faster-whisper`: CTranslate2-accelerated inference engine for OpenAI Whisper models (used by RealtimeSTT).
3. `realtimetts[orpheus]`: Real-time text-to-speech streaming engine supporting multiple backends (SystemEngine, Orpheus, ElevenLabs, Azure, Coqui).
4. `openai`: OpenAI client library (declared in requirements; however, `llm_handler.py` currently invokes OpenAI directly via `requests.post`).
5. `requests`: Synchronous HTTP client library used for calling the OpenAI Chat Completions API endpoint.
6. `python-dotenv`: Parses `.env` key-value pairs into `os.environ`.
7. `soundfile` & `numpy`: Low-level raw audio waveform loading, normalization, and WAV file encoding in `audio_utils.py`.
8. `torch` & `transformers`: PyTorch deep-learning runtime for accelerated Silero VAD, CUDA acceleration, and neural audio synthesis.
9. `colorlog`: Terminal formatting for formatted colored logs.

---

## Hardware & System Requirements

- **Operating System**: Windows (tested with PyAudio / WASAPI and Windows SAPI `SystemEngine`), Linux (requires ALSA / PulseAudio development headers), or macOS.
- **Audio Hardware**:
  - Functional microphone input device.
  - Functional speaker/headphone audio output device.
- **Audio Drivers / Native Libraries**:
  - `pyaudio` (requires PortAudio binaries/headers).
- **GPU Acceleration (Optional)**:
  - NVIDIA GPU with CUDA 11.8+ or 12.x and cuDNN for real-time faster-whisper STT acceleration. If absent, CTranslate2 falls back to CPU execution (`int8` quantization).

---

## Running the Application Locally

### 1. Environment Setup
```bash
# Create a virtual environment
python -m venv .venv

# Activate virtual environment (Windows PowerShell)
.venv\Scripts\Activate.ps1
# (Linux / macOS)
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Credentials
Create a `.env` file in the project root:
```ini
OPENAI_API_KEY=your_actual_openai_api_key_here
```

### 3. Execution Commands
```bash
# Run the voice assistant pipeline
python src/main.py

# Test individual modules independently
python src/llm_handler.py
python src/stt_handler.py
python src/tts_handler.py
```
