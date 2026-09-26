# 05. APIs and External Integrations

## External APIs Overview

The only external network service integrated into `voice_mvp_dupe` is the **OpenAI REST API**.

---

## OpenAI Chat Completions API

### Endpoint Specification
- **URL**: `https://api.openai.com/v1/chat/completions`
- **Method**: `POST`
- **Protocol**: HTTPS (synchronous via Python `requests` library inside async wrapper)
- **Authentication**: Bearer Token via HTTP header `Authorization: Bearer <OPENAI_API_KEY>`

### Request Headers
```python
{
    "Authorization": f"Bearer {self.api_key}",
    "Content-Type": "application/json"
}
```

### Request Payload Structure
```json
{
  "model": "gpt-4o-mini",
  "messages": [
    {
      "role": "system",
      "content": "<DYNAMIC_SYSTEM_PROMPT>"
    },
    {
      "role": "user",
      "content": "User: Hello"
    },
    {
      "role": "assistant",
      "content": "Agent: Welcome to Shamla Tech..."
    },
    {
      "role": "user",
      "content": "<PREPROCESSED_USER_QUERY>"
    }
  ],
  "temperature": 0.8,
  "max_tokens": 800,
  "top_p": 0.9,
  "frequency_penalty": 0.3,
  "presence_penalty": 0.2
}
```

### Parameter Tuning
- `model`: Hardcoded to `"gpt-4o-mini"`.
- `max_tokens`: `1000` for single-turn calls (`process_text`), `800` for historical conversations (`process_text_with_history`).
- `top_p`: `0.9` (nucleus sampling).
- `frequency_penalty`: `0.3` (reduces verbatim repetition across turns).
- `presence_penalty`: `0.2` (encourages introducing new topics).

---

## Error Handling & Resiliency

When the API request fails due to network partitions, timeouts, invalid authentication, or rate limits:
1. `requests.exceptions.RequestException` is caught in `llm_handler.py`.
2. The error is logged to `logger.error(...)`.
3. Rather than crashing the voice loop, `ConversationalPersonality.get_random_error()` returns a conversational fallback response selected at random from:
   - *"Oops, I'm having a bit of a brain freeze right now. Give me a sec?"*
   - *"Ah man, something's not clicking on my end. Can you try that again?"*
   - *"You know what? I'm having trouble with that. Let me try to help differently."*
   - *"Hmm, I'm hitting a snag here. Could you rephrase that for me?"*
   - *"Ugh, technical difficulties on my end. Mind repeating that?"*
4. The synthesized voice assistant speaks the error naturally, giving the user a chance to restate their question.
