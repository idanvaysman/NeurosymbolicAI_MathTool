# Symbolic State Manager Specification

## 1. Architectural Overview
The `SymbolicStateManager` serves as the non-neural, deterministic single source of truth for the entire multi-agent lifecycle. By acting as a centralized state anchor, it replaces highly volatile, token-heavy LLM chat histories with a clean, structured Python object layer. This completely mitigates context bloat and guards against multi-agent logic drift during complex mathematical execution.

### Neuro-Symbolic Synchronization
* **System 1 (Probabilistic):** External LLM agents analyze semantic intent and emit structured instructions.
* **System 2 (Deterministic):** The State Manager receives these instructions, binds them to exact mathematical entities, and enforces algebraic constraints in a strict object space via SymPy.

---

## 2. Core Data Structures
*To maintain maximum flexibility, the exact underlying implementation details are left open to optimization (e.g., standard dictionaries, directed acyclic graphs, or custom dataclasses).*

The State Manager must track three core categories of computational state:
1. **Variable Registry:** A map tracking active symbols, their designated data types (e.g., Integer, Real, Complex), and bound assumptions.
2. **Equation Stack:** An ordered collection of active expressions and mathematical equality relations managed within SymPy's Abstract Syntax Tree (AST) space.
3. **Constraint Vector:** A list of boundary conditions, ranges, or implicit logical rules (e.g., `x > 0`, `y must be an integer`) that condition valid states.

---

## 3. Core API Methods

### `update_variable(symbol_name: str, value_expr: str, constraints: Optional[List[str]] = None) -> bool`
* **Purpose:** Registers or updates a mathematical token inside the state space.
* **Logic:** Parses the incoming string expression into a SymPy object wrapper. It evaluates the assignment against current constraints. If an operational paradox or structural invalidity occurs, it returns `False` or raises an exception to trigger the local debugger loop.
* **Creative Freedom:** Implement advanced tracking here—such as keeping an internal version history of a variable's state mutations for auditing agent logic over time.

### `get_constraints(target_symbols: Optional[List[str]] = None) -> Dict[str, Any]`
* **Purpose:** Queries active boundaries restricting specified symbols.
* **Logic:** If no list is provided, returns the global mathematical constraint boundary matrix. Otherwise, dynamically slices constraints tied to the queried dependency graph.

### `generate_brief() -> Dict[str, Any] (or JSON)`
* **Purpose:** Synthesizes the entire mathematical state down into an incredibly dense, clean, token-efficient text format.
* **Logic:** This "Mathematical Brief" is fed directly to downstream agents (like the Coder Agent), eliminating the need to pass massive, disorganized conversational multi-agent histories.
* **Creative Freedom:** Design how this brief is structured! You can craft a minimal Markdown table string, an optimized compressed JSON chunk, or an explicit declarative mathematical summary designed specifically to keep your local LLM highly attentive.

---

## 4. Error Boundary & State Rollbacks
If a downstream component (such as the SymPy engine or the Sanitizer) catches a runtime exception or illegal syntax during computation, the State Manager must remain uncorrupted. 

* **State Snapshot Isolation:** The State Manager should support a transactional rollback mechanism (`commit()`, `rollback()`), or track mutation steps so it can cleanly revert to the last universally validated mathematical state if a Coder Agent generates broken code.
