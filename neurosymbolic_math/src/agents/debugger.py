import json
from agents.llm_client import call_local_model

class DebuggerAgent:
    def __init__(self, system_prompt: str):
        self.system_prompt = (
            f"{system_prompt}\n\n"
            "You are a headless script patcher. Return ONLY the raw executable Python code. "
            "Do not include markdown code blocks (```), do not include explanations, do not use placeholder brackets."
        )

    def refine_code(self, faulty_code: str, traceback_str: str) -> str:
        refined_system_prompt = (
            f"{self.system_prompt}\n\n"
            "Faulty Code:\n{faulty_code}\n\n"
            "Traceback:\n{traceback_str}"
        )
        
        response = call_local_model(refined_system_prompt, "", require_json=False)
        return response.strip()
