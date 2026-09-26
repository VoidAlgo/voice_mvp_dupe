# 04. AI/ML Components, Models & Prompt Engineering

## AI & ML Model Stack

`voice_mvp_dupe` integrates three distinct AI/ML model subsystems:

| Function | Framework / Library | Model Identifier | Precision / Device |
|---|---|---|---|
| **Speech-to-Text (STT)** | `RealtimeSTT` / `faster-whisper` | `base` (CTranslate2 Whisper) | `int8`, CPU/CUDA auto |
| **Barge-in VAD/STT** | `RealtimeSTT` / `faster-whisper` | `tiny` (CTranslate2 Whisper) | `int8`, low-latency |
| **Voice Activity Detection** | WebRTC VAD + Silero VAD | Built-in Silero neural VAD | Optimized real-time |
| **Language Intelligence** | OpenAI API (`requests`) | `gpt-4o-mini` | Remote cloud inference |
| **Text-to-Speech (TTS)** | `RealtimeTTS` | `SystemEngine` (OS Native TTS) | Local system synthesizer |

---

## Prompt Engineering Architecture

The prompt engineering system in `src/llm_handler.py` is dynamic and sentiment-adaptive.

### 1. Base System Prompt
```text
You are Alex, a warm and genuinely helpful voice assistant for Shamla Tech.

CRITICAL VOICE GUIDELINES:
🎙️ You're being heard, not read - so speak naturally:
- Use contractions constantly (I'm, you're, that's, we'll, don't)
- Vary your sentence structure - mix short and long sentences
- Occasional incomplete thoughts are fine ("So that means... yeah, we can definitely help with that")
- Ask follow-up questions when genuinely curious or when it helps clarify
- Reference earlier conversation points naturally ("Like you mentioned before...")

About Shamla Tech:
- Cutting-edge AI solutions & blockchain/crypto services
- We help businesses transform with innovative tools
- Passionate tech team that genuinely cares about clients

TRANSCRIPTION HANDLING:
- Shamla Tech variations (Shambla/Shamla/etc.) → always "Shamla Tech"
- Forgive pronunciation errors, focus on intent
- If unclear, ask friendly
```

### 2. Sentiment-Conditioned Modifiers

The `SentimentAnalyzer` scores text using keyword matches and appends specific behavioral directives:

- **Urgent (`urgent_count > 0`)**:
  - Direct, rapid tone: skips pleasantries, acknowledges urgency (`"I've got you, let me help right away"`).
  - Dynamically lowers temperature to `0.6` for focused precision.
  - Filler insertion probability is reduced to `0.05`.
- **Negative (`negative_count > positive_count`)**:
  - Empathetic and patient tone (`"I hear you, that's frustrating"`).
  - Sets temperature to `0.8`.
- **Positive (`positive_count > negative_count`)**:
  - Enthusiastic tone matching user energy.
  - Dynamically elevates temperature to `0.9` for playful, varied responses.
- **Neutral**:
  - Balanced, conversational tone at temperature `0.8`.

### 3. Conversation Continuity Prompting

When previous turns exist (`has_history=True`), the following instruction is appended:
```text
📝 CONVERSATION CONTINUITY:
- Reference what they said earlier when relevant: "Going back to what you asked about..."
- Show you're building on previous exchanges
- Don't repeat yourself - build on previous answers
- If they're asking follow-ups, acknowledge you remember: "Right, so building on that..."
```

---

## Spoken Natural Language Simulation

To prevent synthesized speech from sounding robotic, `ConversationalPersonality` applies heuristic conversational post-processing:

1. **Filler Words Insertion**:
   - Injects categories: `thinking` (`"Um,"`, `"Well,"`, `"Let me think,"`, `"Hmm,"`), `transition` (`"So,"`, `"Actually,"`), `clarifying` (`"I mean,"`), or `agreement` (`"Definitely,"`).
   - Probability: ~18% for normal/positive queries, 5% for urgent queries.
2. **Follow-Up Continuers**:
   - Injects phrases such as `"Anything else I can help with?"` or `"Does that help, or should I explain differently?"` (probability ~35%, suppressed if user query already contained a question mark).
3. **Prefix Cleaning**:
   - Strips unintended prefixes produced by the LLM (`"Agent:"`, `"Assistant:"`, `"AI:"`, `"Alex:"`, `"Shamla Tech Agent:"`).
