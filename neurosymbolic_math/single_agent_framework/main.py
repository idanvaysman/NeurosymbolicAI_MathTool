import os
import sys
from io import StringIO
from pydantic import BaseModel, Field
from ollama import Client  # Swapped from google import genai


# ---------------------------------------------------------------------------
# 1. Define the Schema for Structured Output
# ---------------------------------------------------------------------------
class SymPyScript(BaseModel):
    reasoning: str = Field(description="Step-by-step logic on how to translate the English prompt into SymPy math.")
    sympy_code: str = Field(
        description="Pure Python code using SymPy. The final result MUST be assigned to a variable named 'result'.")


# ---------------------------------------------------------------------------
# 2. Define the Agent Wrapper Class
# ---------------------------------------------------------------------------
class SymPyAgent:
    def __init__(self):
        # Initializes the Ollama client pointing to your local network instance
        self.client = Client(host="http://10.16.121.138:11434")
        self.model_name = "qwen2.5-coder:14b-instruct-q6_K"

        self.system_instruction = (
            "You are an expert mathematical agent that translates English word problems "
            "into precise SymPy code. You must define all necessary symbols using sp.symbols(). "
            "Crucially, you must always assign the final symbolic answer to a variable named 'result'."
            #"If the problem does not logically make sense or does not have enough context, reject the prompt and explain why to the user."
        )
    def _generate_code(self, english_prompt: str) -> SymPyScript:
        """Queries local Ollama instance to get a structured JSON object containing the code."""
        response = self.client.chat(
            model=self.model_name,
            messages=[
                {
                    "role": "system",
                    "content": self.system_instruction
                },
                {
                    "role": "user",
                    "content": f"Translate this problem into SymPy code: {english_prompt}"
                }
            ],
            options={
                "temperature": 0.1,  # Low temperature for consistent code generation
            },
            # Enforces Ollama to match the structured schema output
            format=SymPyScript.model_json_schema(),
        )
        # The response.message.content contains the raw JSON string matching the schema
        return SymPyScript.model_validate_json(response.message.content)

    def _execute_code(self, code_str: str) -> str:
        """Safely executes the generated SymPy script and captures the 'result' variable."""
        # Fix: Pass a single dictionary to exec to avoid the list comprehension scoping bug
        exec_scope = {"sp": __import__("sympy")}

        old_stdout = sys.stdout
        redirected_output = StringIO()
        sys.stdout = redirected_output

        try:
            # Running with the same dict for globals and locals fixes NameErrors
            exec(code_str, exec_scope, exec_scope)
            sys.stdout = old_stdout

            if "result" in exec_scope:
                return str(exec_scope["result"])
            else:
                return "Error: Code executed successfully, but 'result' variable was not defined."

        except Exception as e:
            sys.stdout = old_stdout
            return f"Runtime Execution Error: {str(e)}"

    def _format_final_answer(self, original_prompt: str, calculation_result: str) -> str:
        """Feeds the execution result back into the LLM for clean mathematical formatting."""
        formatting_instruction = (
            "You are a helpful math assistant. Your job is to take a user's original question "
            "and the raw mathematical result calculated by a computer, and combine them into a "
            "clean, clear, and well-formatted final response. If there's an error of any kind just say 'Error, try another prompt...'"
        )

        response = self.client.chat(
            model=self.model_name,
            messages=[
                {"role": "system", "content": formatting_instruction},
                {
                    "role": "user",
                    "content": f"Original Question: {original_prompt}\n"
                               f"Calculated Raw Result: {calculation_result}\n\n"
                               f"Please provide the final formatted answer:"
                }
            ],
            options={"temperature": 0.3}  # Slightly higher for more natural language framing
        )
        return response.message.content.strip()

    def run(self, english_prompt: str):
        """Public API to run the agent pipeline."""
        print(f"[Input]: {english_prompt}\n")

        # Step 1: Generate the SymPy code via Ollama
        structured_output = self._generate_code(english_prompt)
        #print(f"[Agent Reasoning]: {structured_output.reasoning}\n")
        #print(f"[Generated Code]:\n---\n{structured_output.sympy_code}\n---")

        # Step 2: Execute code and get raw answer
        raw_answer = self._execute_code(structured_output.sympy_code)
        #print(f"\n[Raw Code Output]: {raw_answer}")

        # Step 3: Format the output nicely via the LLM
        final_formatted_answer = self._format_final_answer(english_prompt, raw_answer)
        print(f"\n[Final Formatted Answer]:\n{final_formatted_answer}")
        return final_formatted_answer


# ---------------------------------------------------------------------------
# 3. Execution
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    # Ensure you have run: pip install ollama sympy pydantic
    agent = SymPyAgent()

    prompt = input("Please enter your prompt: ")
    agent.run(prompt)