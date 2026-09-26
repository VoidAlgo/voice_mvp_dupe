# 02. Architecture & Major Components

## High-Level System Architecture

The application implements a voice assistant pipeline structured around three primary handlers managed by an asynchronous controller:

```
                      +-----------------------------+
                      |         User Audio          |
                      +-----------------------------+
                                     |
                                     v
                      +-----------------------------+
                      |          STTHandler         |
                      |  (RealTimeSTT Whisper Base) |
                      +-----------------------------+
                                     |
                             Transcribed Text
                                     |
                                     v
                      +-----------------------------+
                      |          LLMHandler         |
                      |  - SentimentAnalyzer        |
                      |  - ConversationalPersonality|
                      |  - OpenAI GPT-4o-mini       |
                      +-----------------------------+
                                     |
                               Synthesized Text
                                     |
                                     v
                      +-----------------------------+
                      |          TTSHandler         |
                      |  - RealTimeTTS SystemEngine |
                      |  - Barge-In Monitor Thread  |
                      |    (Whisper Tiny Detector)  |
                      +-----------------------------+
                                     |
                              Speaker Output
```

---

## Component Breakdown & Responsibilities

### 1. Pipeline Controller (`src/main.py`)
- **Role**: Coordinates the entire lifecycle, session setup, and conversational turn loop.
- **Key Functions**:
  - `main()`: Asynchronously initializes handlers, prints the welcome banner, kicks off `stt_handler.start_listening()`, maintains conversation history, and handles graceful teardown in a `finally` block.
  - `handle_conversation_turn(...)`: Executes a single dialog turn:
    1. Awaits transcribed speech from `STTHandler`.
    2. Detects exit phrases (`['quit', 'exit', 'q']`).
    3. Invokes `LLMHandler.process_text_with_history(...)`.
    4. Triggers `TTSHandler.speak(...)` with barge-in enabled.
    5. Awaits completion or handles barge-in detection (recursively initiating the next turn if interrupted).

### 2. Speech-to-Text Handler (`src/stt_handler.py`)
- **Role**: Captures microphone input, detects voice activity, and converts speech to text.
- **Core Class**: `STTHandler`
- **Key Methods**:
  - `start_listening()`: Launches `AudioToTextRecorder` inside a thread pool with a 30-second timeout.
  - `get_transcription()`: Blocking call to `self.recorder.text()`, followed by phonetic error corrections (e.g. replacing `"Shambla"` with `"Shamla"` and `"blocked"` with `"about"`).
  - `stop_listening()`: Terminates recording and releases recorder memory.

### 3. LLM Handler & Personality Engine (`src/llm_handler.py`)
- **Role**: Text understanding, sentiment analysis, dynamic prompt construction, and LLM communication.
- **Core Classes**:
  - `SentimentAnalyzer`: Keyword-based sentiment detector that classifies text into `positive`, `negative`, `urgent`, or `neutral` with an intensity score.
  - `ConversationalPersonality`: Injects natural spoken fillers (e.g., `"Um,"`, `"Well,"`, `"Hmm,"`) and conversation continuers (`"Anything else I can help with?"`), and provides humanized fallback error strings.
  - `LLMHandler`: Preprocesses transcribed text, constructs sentiment-aware prompts, interacts with OpenAI's Chat Completions REST endpoint, and sanitizes output prefixes.

### 4. Text-to-Speech & Barge-In Handler (`src/tts_handler.py`)
- **Role**: Synthesizes spoken audio output while monitoring for real-time human interruption.
- **Core Class**: `TTSHandler`
- **Key Mechanics**:
  - Employs `RealtimeTTS.SystemEngine` coupled with `TextToAudioStream`.
  - Runs playback inside a worker thread `play_audio`.
  - Concurrently spawns a daemon thread `monitor_speech` polling an aggressive, low-latency `AudioToTextRecorder(model="tiny")` every 50 milliseconds.
  - If user speech is detected during playback, sets a `threading.Event()` stop flag, aborts the audio stream (`stream.stop()`), and notifies the controller.

### 5. Audio Utilities (`src/utils/audio_utils.py`)
- **Role**: General-purpose numpy and wave-based audio operations.
- **Functions**:
  - `save_audio_file(file_path, audio_data, sample_rate)`: Writes 16-bit PCM Mono WAV files.
  - `load_audio_file(file_path)`: Reads WAV files into numpy arrays.
  - `normalize_audio(audio_data)`: Scales audio arrays to `[-1.0, 1.0]`.
  - `trim_silence(audio_data, threshold)`: Trims leading and trailing silence.
  - `audio_to_mono(audio_data)`: Downmixes stereo audio arrays to mono.
- **Note**: Currently, `audio_utils.py` is an unreferenced helper module not imported by `main.py`, `stt_handler.py`, or `tts_handler.py`.
