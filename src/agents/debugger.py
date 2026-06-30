import json
from agents.llm_client import call_local_model

class DebuggerAgent:
    def __init__(self, system_prompt: str):
        self.system_prompt = system_prompt

    def refine_code(self, faulty_code: str, traceback: str) -> str:
        refined_system_prompt = (
            f"{self.system_prompt}\n\n"
            "You are a highly specialized debugger. "
            "Your task is to analyze the provided faulty code and traceback, "
            "and return a refined logic patch that fixes syntax anomalies or runtime exceptions "
            "without breaking the core mathematical plan.\n\n"
            "Faulty Code:\n```\n{faulty_code}\n```\n\n"
            "Traceback:\n```\n{traceback}\n```"
        )
        
        response = call_local_model(refined_system_prompt, "", require_json=False)
        return response.strip()
