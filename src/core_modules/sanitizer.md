# Sanitizer Specification

## 1. Architectural Overview
The `Sanitizer` is a deterministic security guardrail and validation script that inspects code payloads before execution[cite: 1]. Operating entirely without neural patterns, it serves as the gatekeeper between the probabilistic Coder/Debugger agents and the local Python execution environment[cite: 1]. Its primary goal is to catch syntax issues or malicious code injections early, preventing the execution of dangerous operations on the host system[cite: 1].

### Security Boundaries
* **Static Analysis First:** Payloads are never executed to check their validity. The Sanitizer evaluates code strictly through static text or structural analysis[cite: 1].
* **Fail-Closed Principle:** If a script or code block triggers even a minor validation warning, the Sanitizer immediately rejects the payload and returns a deterministic error trace to trigger a localized debugger loop[cite: 1].

---

## 2. Core Validation Mechanisms
*You have complete creative freedom over how strictly you enforce security policies—whether using standard library AST visitors, regular expression patterns, or explicit token blocklists.*

The Sanitizer relies on two layered defensive mechanisms to validate incoming code strings:

### A. Abstract Syntax Tree (AST) Inspection
Using Python’s native `ast` module, the sanitizer parses raw code strings into an isolated node tree before any code evaluates[cite: 1].
* **Node Whitelisting:** Restricts allowed operations exclusively to safe mathematical constructs (e.g., `ast.BinOp`, `ast.Name`, `ast.Call` involving approved SymPy functions).
* **Attribute Verification:** Blocks dangerous property lookups or hidden dunder attribute access (e.g., trying to access `__subclasses__` or `__globals__`).

### B. Regex & Literal Token Filtering
A rapid regular expression parsing layer serves as a lightweight firewall for immediate pattern filtering[cite: 1].
* **Command Blacklisting:** Scans for explicit usage of system execution keywords or dangerous builtins such as `os.system`, `subprocess`, `eval`, `exec`, or `open`[cite: 1].
* **File System Guardrails:** Instantly drops commands containing malicious system instructions or destructive path strings (e.g., `rm -rf` or arbitrary disk writes)[cite: 1].

---

## 3. Core API Methods

### `validate_payload(code_str: str) -> Tuple[bool, Optional[str]]`
* **Purpose:** The main entry point called by the pipeline before passing code to the SymPy engine[cite: 1].
* **Logic:** Accepts the generated code string, passes it sequentially through the Regex filter and the AST parser, and returns a boolean status alongside an optional validation error message[cite: 1].
* **Creative Freedom:** You can design this to return highly descriptive, customized syntax hints specifically structured to help your local `DebuggerAgent` patch the syntax error on its very next attempt.

### `is_ast_safe(code_str: str) -> bool`
* **Purpose:** Safely attempts to build and traverse an AST from the provided string[cite: 1].
* **Logic:** Catches structural `SyntaxError` exceptions at compile-time. If compilation succeeds, it runs a custom `ast.NodeVisitor` subclass to verify that no forbidden nodes are embedded in the tree[cite: 1].

---

## 4. Creative Implementation Areas
When building out the actual implementation files referenced in **Research Document.pdf**, think about how you want to handle these advanced guardrails:
* **SymPy Symbol Scoping:** You could implement a system where the Sanitizer actively reads from the `SymbolicStateManager` to verify that the Coder Agent is *only* declaring variables that are already formally registered in the state registry.
* **Execution Timeout Bounds:** Consider pairing this static sanitization with runtime constraints (such as an execution timeout block) to prevent code containing intentional or accidental infinite loops from locking up your multi-agent pipeline.
