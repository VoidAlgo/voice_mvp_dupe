# 06. Configuration & Environment Variables

## Environment Variables

The application expects variables to be defined in `.env` (loaded automatically by `python-dotenv` in `src/llm_handler.py`).

| Variable Name | Required | Default Value | Description |
|---|---|---|---|
| `OPENAI_API_KEY` | **Yes** | *None* | Authentication token for OpenAI Chat Completions API. If missing, `LLMHandler.__init__` raises `ValueError`. |
| `STT_MODEL_SIZE` | No | `"base"` | Model size for the primary speech recognition engine (`tiny`, `base`, `small`, `medium`, `large`). |
| `STT_REALTIME_MODEL_SIZE` | No | `"small"` | Model size declared for real-time speech processing in `config.py`. |
| `STT_DEVICE` | No | `"auto"` | Compute target (`auto`, `cpu`, `cuda`). |
| `STT_REALTIME_PROCESSING_PAUSE` | No | `0.2` | Processing pause duration in seconds. |
| `STT_BEAM_SIZE` | No | `3` | Whisper decoding beam size. |
| `LLM_RATE_LIMIT_DELAY` | No | `0.2` | Delay between consecutive LLM queries. |
| `LLM_MAX_RETRIES` | No | `3` | Maximum retry attempts for LLM network requests. |
| `LLM_RETRY_DELAY` | No | `1.0` | Backoff sleep duration between retries. |
| `BUFFER_THRESHOLD` | No | `5` | Character buffer batching threshold. |
| `BUFFER_TIMEOUT` | No | `0.5` | Buffer flush timeout in seconds. |
| `LOG_LEVEL` | No | `"INFO"` | Logging verbosity (`DEBUG`, `INFO`, `WARNING`, `ERROR`). |
| `MAX_AUDIO_DURATION` | No | `3600` | Maximum recording length in seconds. |

---

## Static Configuration (`src/config.py`)

The repository contains a centralized `Config` class designed with schema validation and environment overrides:

```python
class Config:
    # Model settings
    STT_MODEL_SIZE: str = "base"
    STT_REALTIME_MODEL_SIZE: str = "small"
    STT_DEVICE: str = "auto"
    STT_REALTIME_PROCESSING_PAUSE: float = 0.2
    STT_BEAM_SIZE: int = 3
    
    # LLM settings
    LLM_MODEL: str = "gemini-2.0-flash-lite"
    LLM_TEMPERATURE: float = 0.7
    LLM_MAX_TOKENS: int = 2048
    LLM_RATE_LIMIT_DELAY: float = 0.2
    LLM_MAX_RETRIES: int = 3
    LLM_RETRY_DELAY: float = 1.0
    
    # TTS settings
    TTS_MODEL: str = "orpheus"
    TTS_VOICE: str = "default"
    TTS_EMOTIVE_TAGS: bool = True
    ...
```

---

## Configuration Drift & Architectural Decoupling

A critical architectural finding in this repository is that **the handlers do not currently consume `Config`**:

1. **LLM Provider Divergence**:
   - `Config.LLM_MODEL` specifies `"gemini-2.0-flash-lite"`.
   - However, `src/llm_handler.py` does not import `Config` and directly targets OpenAI's `"gpt-4o-mini"`.
2. **TTS Model Divergence**:
   - `Config.TTS_MODEL` specifies `"orpheus"`.
   - However, `src/tts_handler.py` directly instantiates `RealtimeTTS.SystemEngine()` (system default voice), bypassing the Orpheus neural model.
3. **STT Parameters Hardcoded**:
   - `src/stt_handler.py` hardcodes `model="base"`, `compute_type="int8"`, and `realtime_processing_pause=0.3`, rather than reading from `Config.STT_MODEL_SIZE` or `Config.STT_REALTIME_PROCESSING_PAUSE`.
4. **Validation Failure Bug**:
   - In `Config.validate_settings()`, lines 110-113 invoke `logger = logging.getLogger(__name__)`, but `import logging` is missing from `src/config.py`. As a result, if validation fails, it triggers a `NameError: name 'logging' is not defined`.
