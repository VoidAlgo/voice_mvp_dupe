# Voice MVP Dupe - Technical Documentation Suite

Welcome to the comprehensive technical documentation for **voice_mvp_dupe**, housed inside `thedocs/`.

This documentation suite provides a complete, code-verified analysis of the voice assistant pipeline, covering architecture, speech recognition, LLM intelligence, text-to-speech synthesis, barge-in interrupt handling, configuration, dependencies, testing audits, and technical debt.

---

## Documentation Index

| Module | Title | Primary Focus |
|---|---|---|
| [01. Project Overview](file:///d:/VoidAlgo/fatbatman/voice_mvp_dupe/thedocs/01_project_overview.md) | Overview & Repository Structure | Mission, domain (Shamla Tech voice agent), directory tree, and key files |
| [02. Architecture & Components](file:///d:/VoidAlgo/fatbatman/voice_mvp_dupe/thedocs/02_architecture_and_components.md) | Component Architecture | Handlers (`STTHandler`, `LLMHandler`, `TTSHandler`), utilities, and roles |
| [03. Data Flow & Barge-In](file:///d:/VoidAlgo/fatbatman/voice_mvp_dupe/thedocs/03_data_flow_and_interactions.md) | Execution & Interaction Flow | End-to-end conversation cycle, threading model, and real-time barge-in interruption |
| [04. AI/ML, Models & Prompts](file:///d:/VoidAlgo/fatbatman/voice_mvp_dupe/thedocs/04_ai_ml_and_prompts.md) | AI/ML Models & Prompt Engineering | Whisper STT, GPT-4o-mini, SystemEngine TTS, persona prompts, sentiment adaptation |
| [05. APIs & External Integrations](file:///d:/VoidAlgo/fatbatman/voice_mvp_dupe/thedocs/05_apis_and_integrations.md) | External Integrations | OpenAI Chat Completions API, payload schemas, error recovery |
| [06. Configuration & Environment](file:///d:/VoidAlgo/fatbatman/voice_mvp_dupe/thedocs/06_configuration_and_environment.md) | Config & Environment Variables | `Config` class, `.env` variables, configuration drift analysis |
| [07. Dependencies & Runtime](file:///d:/VoidAlgo/fatbatman/voice_mvp_dupe/thedocs/07_dependencies_and_runtime.md) | Dependencies & Deployment | `requirements.txt`, PyAudio, audio drivers, execution commands |
| [08. Testing & Validation Audit](file:///d:/VoidAlgo/fatbatman/voice_mvp_dupe/thedocs/08_testing_and_quality.md) | Test Suite Audit | Detailed line-by-line review of `tests/`, API contract mismatches, execution failures |
| [09. Technical Debt & Roadmap](file:///d:/VoidAlgo/fatbatman/voice_mvp_dupe/thedocs/09_technical_debt_and_limitations.md) | Technical Debt & Limitations | Bugs, unreferenced code, history alternation flaws, and research areas |
