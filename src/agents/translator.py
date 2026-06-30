import json
from agents.llm_client import call_local_model
from core_modules.sanitizer import CodeSanitizer
from core_modules.state_manager import SymbolicStateManager

class TranslatorAgent:
    def __init__(self, system_prompt: str):
        self.system_prompt = system_prompt
        self.sanitizer = CodeSanitizer()
        self.state_manager = SymbolicStateManager()

    def translate(self, user_content: str) -> str:
        response = call_local_model(self.system_prompt, user_content, require_json=True)
        sanitized_code = self.sanitize_code(response)
        return sanitized_code

    def sanitize_code(self, code: str) -> str:
        result = self.sanitizer.sanitize_code(code)
        if result != "Code is safe.":
            raise ValueError(f"Sanitization failed: {result}")
        return code

class SelfRefinerAgent:
    def __init__(self, system_prompt: str):
        self.system_prompt = system_prompt
        self.sanitizer = CodeSanitizer()
        self.state_manager = SymbolicStateManager()

    def refine(self, user_content: str, execution_trace: str) -> str:
        refined_system_prompt = f"{self.system_prompt}\n\nExecution Trace:\n{execution_trace}"
        response = call_local_model(refined_system_prompt, user_content, require_json=True)
        sanitized_code = self.sanitize_code(response)
        return sanitized_code

    def sanitize_code(self, code: str) -> str:
        result = self.sanitizer.sanitize_code(code)
        if result != "Code is safe.":
            raise ValueError(f"Sanitization failed: {result}")
        return code
