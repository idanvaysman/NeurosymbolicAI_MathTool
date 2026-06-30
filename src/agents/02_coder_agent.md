# Coder Agent Specification

## 1. Architectural Overview
[cite_start]The `CoderAgent` acts as the low-level syntactic execution layer of the neuro-symbolic framework[cite: 41]. [cite_start]Its sole responsibility is to ingest the structured data from the planning phase and translate it into valid JSON instructions or executable Python syntax optimized for the SymPy engine[cite: 58]. [cite_start]By isolating syntax generation here, the high-level semantic planner remains unburdened by code compilation details[cite: 41].

### Stateless Design Matrix
* [cite_start]**Context Bloat Mitigation:** To maximize token efficiency, the Coder Agent does not ingest the user's conversational history[cite: 46]. 
* [cite_start]**Brief Isolation:** It operates completely statelessly, interacting strictly with a dense, auto-generated Mathematical Brief provided by the central state manager[cite: 46]. [cite_start]This approach minimizes token consumption and prevents "lost in the middle" memory degradation[cite: 46].

---

## 2. Execution Interface
The Coder Agent acts as a deterministic translator converting schema attributes to concrete functional code:

1. [cite_start]**Brief Retrieval:** The agent receives a structural snapshot (JSON/Dict) from the `SymbolicStateManager` outlining current active variables, equations, and rules[cite: 46, 56].
2. [cite_start]**Syntactic Generation:** It maps the declarative steps down to explicit SymPy commands (e.g., `sympy.Symbol`, `sympy.solve`, `sympy.integrate`)[cite: 2, 58].
3. [cite_start]**Payload Outbound:** Emits a raw code block string that is routed directly to the system Sanitizer before engine evaluation[cite: 64].

---

## 3. Class Structure & Core Methods

### `CoderAgent` (Class)
* **Attributes:**
    * [cite_start]`llm_client`: The target LLM API interface handler (e.g., Qwen-Coder or alternative specialized coding models)[cite: 52].
    * `generation_prompt`: A strict system prompt defining permitted SymPy code structures and limiting output to raw code blocks.
* **Methods:**
    * `generate_sympy_syntax(mathematical_brief: Dict[str, Any]) -> str`
        * [cite_start]**Purpose:** Evaluates the standardized state manager summary and outputs a target snippet of Python/SymPy code[cite: 46, 58].
        * **Logic:** Formats the brief into the agent prompt context, triggers the LLM execution, and filters the string response to clean out any markdown formatting anomalies.

---

## 4. Creative Implementation Areas
* **Code Modularization:** Determine whether the Coder Agent should emit a single, complete execution script containing all calculation steps or execute smaller, individual functional blocks sequentially while updating the state anchor after each step.
* **Assumption Engineering:** Design how the Coder maps metadata constraints (e.g., "x is a positive integer") into explicit SymPy keyword arguments (`symbols('x', integer=True, positive=True)`) to keep calculations accurate.
