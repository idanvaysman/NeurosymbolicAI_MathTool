# Neuro-Symbolic Project Specifications & Guardrails

## 1. Network & LLM Infrastructure
* **Target Server URL:** http://10.16.121.138:11434/v1
* **API Key:** "ollama" (Dummy string placeholder for unauthenticated local network)
* **Default Model Tag:** "llama3.1:8b"

## 2. Strict Library & Architecture Rules
* **Allowed Frameworks:** Use ONLY native Python modules, `sympy` for mathematical symbols, and the official `openai` library (`from openai import OpenAI`) for network calls.
* **FORBIDDEN Frameworks:** DO NOT use LiteLLM, LangChain, CrewAI, AutoGen, or any third-party agent abstraction frameworks. These cause severe array parsing bugs with our network cluster.
* **Determinism:** All agent API calls must enforce `temperature=0.0`.
* **Output Restrictions:** Agents must return raw data via structured JSON schemas using the `response_format={"type": "json_object"}` parameter.

## 3. Core Component Layout
* `src/core/state_manager.py`: Implements `SymbolicStateManager` to register symbols and track math state variables cleanly outside the LLM context.
* `src/agents/llm_client.py`: Implements `call_local_model()` using native OpenAI client to route strings to the network cluster.
* `src/pipeline.py`: Implements `initialize_pipeline()` to run the multi-agent translator and localized JSON self-healing loops.
