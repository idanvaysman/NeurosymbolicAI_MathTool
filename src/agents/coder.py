import json
from agents.llm_client import call_local_model
from core_modules.state_manager import SymbolicStateManager

class CoderAgent:
    def __init__(self, system_prompt: str):
        self.system_prompt = system_prompt
        self.state_manager = SymbolicStateManager()

    def generate_code(self) -> str:
        mathematical_brief = self.state_manager.generate_brief()
        response = call_local_model(self.system_prompt, json.dumps(mathematical_brief), require_json=False)
        return response.strip()
