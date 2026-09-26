# 01. Project Overview & Repository Structure

## Project Purpose & Domain

`voice_mvp_dupe` is a real-time, bidirectional voice conversational agent. According to the codebase implementation (primarily in `src/main.py` and `src/llm_handler.py`), the project serves as an AI Voice Calling Agent tailored for **Shamla Tech**, an organization providing artificial intelligence, blockchain, and cryptocurrency services.

The system is designed to provide full-duplex conversational voice interaction:
1. **Continuous Speech-to-Text (STT)**: Listens for user voice input using real-time Voice Activity Detection (VAD) and Whisper models.
2. **Contextual AI Intelligence (LLM)**: Analyzes conversational sentiment, injects natural vocal pauses and fillers, and queries OpenAI's `gpt-4o-mini` with conversation history.
3. **Voice Synthesis with Interruption Handling (TTS & Barge-in)**: Speaks responses back to the user via system audio while actively listening for user interruptions (barge-in) to immediately halt audio playback and pivot to the next turn.

---

## Repository Structure

```
voice_mvp_dupe/
├── .gitignore                     # Git ignore rules (ignores .env, .venv, /audio, /README.md)
├── README.md                      # Minimal root repository description
├── requirements.txt               # Python package dependencies
├── responses                      # Placeholder file ("# This directory is intentionally left blank.")
├── src/
│   ├── .env                       # Local environment configuration file (empty in repository)
│   ├── config.py                  # Static configuration dataclass and environment variable loader
│   ├── llm_handler.py             # LLM orchestration, sentiment detection, personality tuning
│   ├── main.py                    # Main conversational pipeline loop and entrypoint
│   ├── realtimesst.log            # Execution log file from previous RealTimeSTT runs
│   ├── stt_handler.py             # RealTimeSTT wrapper with audio recording & transcription
│   ├── tts_handler.py             # RealTimeTTS wrapper with barge-in interrupt detection
│   ├── audio/
│   │   └── output/
│   │       ├── 263639.wav         # Zero-byte audio placeholder artifact
│   │       ├── 264257.wav         # Zero-byte audio placeholder artifact
│   │       └── 265298.wav         # Zero-byte audio placeholder artifact
│   └── utils/
│       └── audio_utils.py         # Audio utility functions (normalization, trim silence, WAV I/O)
├── tests/
│   ├── test_integration.py        # Integration test cases for STT -> LLM -> TTS pipeline
│   ├── test_llm.py                # Unit tests for LLM handler
│   ├── test_stt.py                # Unit tests for speech transcription
│   └── test_tts.py                # Unit tests for speech synthesis
└── thedocs/                       # Comprehensive technical documentation suite
```

---

## Important Files & Directories

- `src/main.py`: Orchestrates the main asynchronous conversation loop (`handle_conversation_turn` and `main`).
- `src/stt_handler.py`: Houses `STTHandler`, wrapping `RealtimeSTT.AudioToTextRecorder`.
- `src/llm_handler.py`: Houses `LLMHandler`, `ConversationalPersonality`, and `SentimentAnalyzer`.
- `src/tts_handler.py`: Houses `TTSHandler`, managing `RealtimeTTS.SystemEngine` audio playback and a secondary `AudioToTextRecorder` instance running at 50ms intervals to detect user barge-in.
- `src/config.py`: Defines the `Config` class with default parameters for models, timeouts, and thresholds.
- `src/utils/audio_utils.py`: Standalone numpy-based audio manipulation helpers (`save_audio_file`, `load_audio_file`, `normalize_audio`, `trim_silence`, `audio_to_mono`).
- `requirements.txt`: Package manifests specifying `RealtimeSTT`, `RealtimeTTS[orpheus]`, `faster-whisper`, `openai`, `soundfile`, `colorlog`, etc.
- `src/realtimesst.log`: Operational trace containing log entries demonstrating RealtimeSTT initialization, WebRTC VAD, Silero VAD, and transcription timing.
