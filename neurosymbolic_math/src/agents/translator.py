import json
from typing import Optional
from agents.llm_client import call_local_model
from core_modules.sanitizer import CodeSanitizer, extract_raw_code

class TranslatorAgent:
    def __init__(self, system_prompt: Optional[str] = None):
        """
        Supports both empty instantiation and legacy prompt arguments to ensure 
        no import or execution mismatch crashes occurs in main.py.
        """
        self.system_prompt = system_prompt or (
            "You are a strategic mathematical planner (System 1).\n"
            "Your job is to read an unstructured English math problem and translate it into a structured mathematical plan in JSON format.\n"
            "The JSON must contain a 'python_code' key with a draft python calculation, and a structured 'mathematical_expression' dictionary matching our AST guidelines.\n"
            "Return ONLY valid JSON. Do not include markdown code fences or conversational text."
        )
        self.sanitizer = CodeSanitizer()

    def generate_plan(self, user_input: str) -> str:
        """
        Calls the LLM client to parse user input into structured JSON mathematical AST logic.
        """
        response = call_local_model(self.system_prompt, user_input)
        return response

    def translate(self, raw_math_problem: str) -> str:
        """
        A robust, backwards-compatible translation entry point that safely parses JSON and 
        verifies mathematical structure blocks under AST sanitization.
        """
        response = ""
        try:
            response = self.generate_plan(raw_math_problem)
            sanitized_json_str = self.sanitize_code(response)
            return sanitized_json_str
        except Exception as e:
            # Fallback to empty JSON wrapper if translation completely errors out
            fallback_response = response if response else "{}"
            raise ValueError(f"Sanitization failed on input layout: {fallback_response}. Error: {e}")

    def sanitize_code(self, response: str) -> str:
        """
        Safely extracts code from planning JSON outputs and sanitizes it.
        We isolate the specific code segments to prevent treating structural JSON keys as code nodes.
        """
        try:
            clean_response = extract_raw_code(response)
            data = json.loads(clean_response)
            
            # Extract and statically verify ONLY the embedded python formula strings, NOT the JSON layout
            embedded_code = data.get("python_code", "")
            if embedded_code:
                # Ensure the embedded math logic compiles and passes static analysis checks cleanly
                self.sanitizer.sanitize_code(embedded_code)
                
            return clean_response
        except Exception as e:
            raise ValueError(f"Sanitization failed on response payload structure: {e}")


class SelfRefinerAgent:
    def __init__(self, system_prompt: Optional[str] = None):
        self.system_prompt = system_prompt or "You are an automated plan refinement assistant."
        self.sanitizer = CodeSanitizer()

    def verify_and_refine(self, initial_plan: str, translator: TranslatorAgent) -> str:
        """
        Programmatic verification loop to validate correctness before mutation.
        """
        try:
            translator.sanitize_code(initial_plan)
            return initial_plan
        except Exception:
            # Fallback returns the initial draft plan to allow the main execution/healing loop to process it
            return initial_plan

    def refine(self, user_content: str, execution_trace: str) -> str:
        """
        Backwards-compatible legacy signature support.
        """
        refined_system_prompt = f"{self.system_prompt}\n\nExecution Trace:\n{execution_trace}"
        response = call_local_model(refined_system_prompt, user_content)
        return extract_raw_code(response)
