# 08. Testing & Quality Assurance Audit

## Overview of the Test Suite

The repository contains four test files in the `tests/` directory:
- `tests/test_integration.py`
- `tests/test_llm.py`
- `tests/test_stt.py`
- `tests/test_tts.py`

---

## Detailed File-by-File Analysis & API Drift

A rigorous audit of the `tests/` directory reveals that **all test suites are completely out of sync with the actual implementation**. The test files reference legacy method signatures, functions, and classes that no longer exist in `src/`.

### 1. `tests/test_integration.py`
- **Attempted Imports**:
  ```python
  from src.stt_handler import enqueue_text           # FAILS: enqueue_text does not exist in stt_handler
  from src.llm_handler import query_gemini          # FAILS: query_gemini does not exist in llm_handler
  from src.tts_handler import RealTimeTTSHandler    # FAILS: class is named TTSHandler, not RealTimeTTSHandler
  ```
- **Execution Viability**: **Broken**. Attempting to run this test immediately raises an `ImportError`.

### 2. `tests/test_llm.py`
- **Attempted Imports & Calls**:
  ```python
  from src.llm_handler import enqueue_text          # FAILS: enqueue_text does not exist
  ```
- **Assertion Assumptions**:
  - Tests assume a standalone function `enqueue_text(str)` that queries a Gemini endpoint and returns a dictionary `{"response": "..."}`.
  - The actual implementation in `src/llm_handler.py` provides `LLMHandler.process_text(text: str) -> str` and `LLMHandler.process_text_with_history(text: str, history: list) -> str`.
- **Execution Viability**: **Broken** due to `ImportError`.

### 3. `tests/test_stt.py`
- **Attempted Imports & Calls**:
  ```python
  from src.stt_handler import clean_transcript      # FAILS: clean_transcript does not exist
  ```
- **TTS Method Assumptions**:
  - `await self.tts_handler.process_text(...)` (FAILS: `TTSHandler` has no `process_text` method; its method is `speak(...)`).
  - Expects emotive tag processing output: `self.assertIn("Emotive processing for happy", result)`.
- **Execution Viability**: **Broken** due to `ImportError`.

### 4. `tests/test_tts.py`
- **Method Assumptions on `TTSHandler`**:
  - Calls `self.tts_handler.initialize_orpheus()`: Does not exist on `TTSHandler`.
  - Calls `self.tts_handler.process_text()`: Does not exist on `TTSHandler`.
  - Calls `self.tts_handler.synthesize_speech()`: Does not exist on `TTSHandler`.
- **Instantiation Hazard**:
  - In `setUp()`, `TTSHandler()` is instantiated without mocks:
    ```python
    self.tts_handler = TTSHandler()
    ```
    Because `TTSHandler.__init__` creates an `AudioToTextRecorder(model="tiny")`, running the test attempts to bind to physical microphone audio hardware and downloads Whisper model weights on the local machine during test fixture creation.
- **Execution Viability**: **Broken** with `AttributeError` and hardware binding errors.

---

## Summary of Testing Deficiencies

1. **Zero Passing Unit Tests**: Due to `ImportError` on missing functions and mismatched class names, none of the unit or integration tests can execute against the current codebase.
2. **Missing Mocking for Hardware & Deep Learning Models**: Tests attempt live hardware instantiation of PortAudio streams and Whisper model weights rather than mocking `RealtimeSTT` and `RealtimeTTS`.
3. **No CI Pipeline for Tests**: Unlike `demo-repo`, `voice_mvp_dupe` has no GitHub Actions workflow configured in `.github/workflows/` to run `pytest` or `unittest`.
