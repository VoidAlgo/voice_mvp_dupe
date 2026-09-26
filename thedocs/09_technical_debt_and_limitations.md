# 09. Technical Debt, Limitations & Investigation Roadmap

## Current System Limitations

1. **Synchronous HTTP in Async Loop**:
   - In `src/llm_handler.py`, the network call to OpenAI is performed using synchronous `requests.post(...)` inside `async def process_text` and `async def process_text_with_history`.
   - This blocks the Python `asyncio` event loop during the entire round-trip LLM network call, stalling other concurrent async tasks.
2. **Audio Hardware Dependence**:
   - The application relies directly on local host audio hardware (microphone, speakers) through PortAudio / PyAudio and Windows SAPI.
   - It cannot currently operate headlessly in standard Docker containers or cloud VMs without virtual audio devices (`veth`, ALSA dummy driver, or PulseAudio loopback).
3. **Fragile Barge-In Speech Detector**:
   - The barge-in detector runs a second instance of `AudioToTextRecorder(model="tiny")` checking every 50ms while system speakers are actively playing audio.
   - Without Acoustic Echo Cancellation (AEC), the microphone can capture the assistant's own voice output from the speakers and falsely trigger a barge-in interruption.

---

## Technical Debt & Codebase Flaws

### 1. Naive History Role Assignment
In `src/llm_handler.py` (lines 209-211):
```python
for i, exchange in enumerate(conversation_history[-8:]):
    role = "user" if i % 2 == 0 else "assistant"
    messages.append({"role": role, "content": exchange})
```
- It arbitrarily alternates `role` solely based on whether the slice index `i` is even or odd, completely ignoring whether the line starts with `"User:"`, `"Agent:"`, or `"System:"`.
- If an interruption occurred (`"User: [Interrupted AI]"`) or an odd number of turns was sliced, the roles for the entire conversation history can become completely inverted, causing the LLM to mistake previous assistant responses for user input.

### 2. Prompt Identity Divergence
- In `src/main.py` (line 87), the system prompt instructs:
  *"You are an AI voice calling agent for Shamla Tech. Shamla Tech provides AI, blockchain, and cryptocurrency services..."*
- In `src/llm_handler.py` (lines 287-289), the dynamic system prompt defines:
  *"You are Alex, a warm and genuinely helpful voice assistant for Shamla Tech..."*
- Two conflicting personas with differing guidelines are passed at different layers of the pipeline.

### 3. Missing `import logging` in `src/config.py`
In `Config.validate_settings()` (line 110):
```python
if errors:
    logger = logging.getLogger(__name__)  # NameError: name 'logging' is not defined!
```
- `logging` is not imported at the top of `src/config.py`. Any validation failure causes an immediate uncaught `NameError`.

### 4. Configuration Disconnect
- `src/config.py` defines extensive settings (`LLM_MODEL = "gemini-2.0-flash-lite"`, `TTS_MODEL = "orpheus"`, buffer thresholds, timeouts), but `main.py`, `llm_handler.py`, and `tts_handler.py` do not import or use `Config`.

### 5. Orphaned & Artifact Files
- `src/utils/audio_utils.py`: Standalone utilities for audio processing that are never imported or utilized.
- `responses`: A text file containing only `"# This directory is intentionally left blank."`, while `Config.RESPONSES_DIR` references a directory.
- `src/audio/output/263639.wav`, `264257.wav`, `265298.wav`: Zero-byte empty files committed into version control.
- `src/realtimesst.log`: A 360KB log file committed directly to version control.
- `.gitignore`: Does not ignore `*.log`, `__pycache__/`, or `*.pyc` files.

---

## Areas for Further Investigation

1. **Acoustic Echo Cancellation (AEC)**:
   - Investigate integrating WebRTC AEC or PyAudio loopback filtering so that audio emitted by `TTSHandler` is subtracted before passing audio to `speech_detector`.
2. **Migration to Async OpenAI Client**:
   - Replace synchronous `requests.post` with `openai.AsyncOpenAI` or `aiohttp` to ensure non-blocking execution in the `asyncio` event loop.
3. **Structured Role Parsing**:
   - Refactor `process_text_with_history` to parse message prefixes (`User:`, `Agent:`, `System:`) into proper OpenAI message roles (`user`, `assistant`, `system`).
4. **Test Suite Modernization**:
   - Rewrite `tests/` using `pytest` and `unittest.mock` to mock `AudioToTextRecorder`, `SystemEngine`, and the OpenAI client without requiring real audio hardware or API credits.
