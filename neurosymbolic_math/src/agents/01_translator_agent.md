# Translator Agent & Self-Refiner Loop Specification

## 1. Architectural Overview
The `TranslatorAgent` represents the primary semantic entry point of the neuro-symbolic workflow. [cite_start]Acting as the high-level planner (System 1), it decouples the cognitive load of mathematical reasoning by separating strategic intent from low-level execution syntax. [cite_start]Its core responsibility is to read unstructured English math problems and emit a deterministic, structured mathematical plan wrapped in JSON instructions[cite: 1, 8, 50, 51].

[cite_start]To ensure the integrity of the generated plan before it mutates the global state, the Translator is tightly coupled with a **Self-Refiner Agent** in a closed-loop verification sequence[cite: 20, 53].

---

## 2. The Ingestion & Verification Loop
[cite_start]The integration of the Self-Refiner acts as an internal quality control gatekeeper[cite: 54]. The loop executes across the following stages:

1. [cite_start]**Ingestion:** The system accepts a raw natural language math problem from the user.
2. [cite_start]**Drafting:** The Translator Agent (utilizing an LLM API wrapper like GPT-4o, Claude 3.5 Sonnet, or Llama 3) generates an initial logical breakdown and draft code structure[cite: 52, 53].
3. [cite_start]**Interpretation:** The Self-Refiner Agent executes this draft code within an isolated, local Python code interpreter environment[cite: 21, 53].
4. [cite_start]**Feedback/Refinement:** * If the interpreter encounters an error, the Self-Refiner intercepts the trace and routes it back to the Translator to patch its logic[cite: 53].
    * [cite_start]If the code executes successfully and satisfies structural validation, the plan is approved to output its finalized JSON instructions[cite: 8, 53].

---

## 3. Class Structure & Core Methods
*The underlying prompt templates, system instructions, and orchestration libraries (e.g., LangChain, Instructor, or a pure HTTP client) remain completely customizable.*

### `TranslatorAgent` (Class)
* **Attributes:**
    * [cite_start]`llm_client`: The wrapped LLM backend client interface[cite: 52].
    * `system_prompt`: Guidelines enforcing strict JSON formatting rules and mathematical decomposition strategies.
* **Methods:**
    * `generate_plan(user_input: str) -> Dict`
        * **Purpose:** Coordinates the primary execution block. [cite_start]Calls the LLM, triggers the Self-Refiner loop, and returns the verified JSON payload[cite: 8, 53].
    * `refine_plan(previous_output: str, error_trace: str) -> str`
        * [cite_start]**Purpose:** A specialized prompt context handler that forces the LLM to review its previous failure alongside the code interpreter's feedback to yield a corrected mathematical plan[cite: 53].

### `SelfRefinerAgent` (Class)
* **Methods:**
    * `verify_execution(draft_code: str) -> Tuple]`
        * [cite_start]**Purpose:** Acts as the programmatic wrapper around the local code interpreter[cite: 21, 53]. [cite_start]Returns a status boolean along with any caught execution error trace messages[cite: 53].

---

## 4. Creative Implementation & Prompt Areas
When implementing the actual code for this module, you have creative freedom over several optimization factors:
* **JSON Constraints:** You can choose whether to use standard string manipulation with rigorous error parsing, or enforce strict schemas using Pydantic frameworks to eliminate formatting failures before they hit the interpreter.
* **Plan Granularity:** Determine how complex the Translator's output schema should be. Should it map problems out step-by-step into micro-operations (e.g., `isolate_variable`, `substitute`, `integrate`), or output broad declarative blocks for the Coder Agent to interpret?
* **Interpreter Sandboxing:** Define the depth of the local interpreter environment—whether it is a simple native `exec()` scope or an isolated Jupyter/Docker kernel wrapper to prevent local evaluation drift.
