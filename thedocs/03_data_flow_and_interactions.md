# 03. End-to-End Data Flow & Interaction Model

## Conversational Execution Cycle

The interaction loop in `voice_mvp_dupe` functions as an asynchronous turn-based state machine with full-duplex interrupt capability:

```
[System Init: Handlers Started]
             |
             v
[Welcome Message Synthesized via TTS]
             |
             +---------> [Wait for User Speech: STTHandler.get_transcription()]
             |                                    |
             |                            Transcribed String
             |                                    |
             |                                    v
             |                         [Check 'quit' / 'exit']
             |                                 /     \
             |                             (Yes)     (No)
             |                              /           \
             |                      [Exit Loop]    [Analyze Sentiment]
             |                                           |
             |                                     [Query LLM]
             |                                           |
             |                                    Response Text
             |                                           |
             |                                           v
             |                             [Start TTS Playback Thread]
             |                                           |
             |                     +---------------------+---------------------+
             |                     |                                           |
             |                     v                                           v
             |            [Audio Stream Play]                        [Monitor Barge-In (50ms)]
             |                     |                                           |
             |         [Playback Completes Normal]                      [Speech Detected?]
             |                     |                                       /        \
             |                     |                                   (Yes)        (No)
             |                     |                                     |           |
             |                     |                                [Stop Audio]     |
             |                     |                              [Set Barge Flag]   |
             |                     |                                     |           |
             |                     v                                     v           v
             +---------------------+-------------------------------------+-----------+
```

---

## Detailed Step-by-Step Flow

### 1. Audio Ingestion & Transcription (`STTHandler`)
1. In `main.py`, `stt_handler.start_listening()` activates `RealtimeSTT.AudioToTextRecorder` using PyAudio with a 16kHz sample rate and WebRTC VAD.
2. In `handle_conversation_turn()`, the program calls `await stt_handler.get_transcription()`.
3. `self.recorder.text()` blocks until silence is detected following speech (`post_speech_silence_duration=0.8s`).
4. Common acoustic and spelling errors are sanitized:
   - `"Shambla Tech"` $\rightarrow$ `"Shamla Tech"`
   - `"Shambla"` $\rightarrow$ `"Shamla"`
   - `"blocked"` $\rightarrow$ `"about"`

### 2. Dialogue Processing & History Management (`LLMHandler`)
1. User text is appended to `conversation_history`:
   ```python
   conversation_history.append(f"User: {user_text}")
   ```
2. `llm_handler.process_text_with_history(user_text, conversation_history)` is invoked.
3. The input text is evaluated by `SentimentAnalyzer.analyze(text)`:
   - Counts occurrences of positive, negative, and urgent vocabulary keywords.
4. Input text contractions are normalized:
   - `"wanna"` $\rightarrow$ `"want to"`, `"gonna"` $\rightarrow$ `"going to"`, etc.
5. The dynamic system prompt is constructed combining:
   - Base personality (`Alex, Shamla Tech assistant`).
   - Sentiment tone modifier (`urgent`, `negative`, `positive`, or `neutral`).
   - History continuity modifier.
6. The last 8 conversation exchanges from `conversation_history[-8:]` are formatted into the request payload.
7. An HTTP POST request is dispatched to `https://api.openai.com/v1/chat/completions`.
8. The raw LLM response is post-processed:
   - Prefixes like `"Agent:"`, `"AI:"`, or `"Shamla Tech Agent:"` are stripped.
   - Spoken fillers (`"Um,"`, `"Well,"`) and continuers are conditionally injected based on sentiment and question presence.

### 3. Speech Synthesis & Barge-in Interruption (`TTSHandler`)
1. In `handle_conversation_turn()`, `tts_handler.speak(...)` is invoked with `enable_barge_in=True`.
2. Audio generation uses `RealtimeTTS.SystemEngine` streamed through `TextToAudioStream`.
3. Concurrently, a daemon thread `monitor_speech` runs an active `AudioToTextRecorder(model="tiny")` checking every 50ms:
   - If user speech is detected (`detected_text.strip()` is non-empty):
     - Sets `self.barge_in_detected = True`.
     - Calls `self.stop_event.set()`.
     - Immediately interrupts playback via `self.stream.stop()`.
4. `wait_for_completion(timeout=30.0)` returns whether playback finished cleanly or was interrupted.
5. If barge-in is detected:
   - Logs `"🎤 Barge-in detected! You interrupted the AI."`
   - Appends `"User: [Interrupted AI]"` to `conversation_history`.
   - Recursively invokes `handle_conversation_turn(...)` to immediately capture the interrupting statement.
