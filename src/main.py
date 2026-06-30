import sys
import traceback
from agents.translator import TranslatorAgent, SelfRefinerAgent
from agents.coder import CoderAgent
from agents.debugger import DebuggerAgent
from core_modules.sanitizer import CodeSanitizer
from core_modules.state_manager import SymbolicStateManager
import sympy as sp

sys.path.append('src')

def main():
    # Initialize agents and state manager
    translator_system_prompt = "You are a mathematical translator."
    refiner_system_prompt = "You are a code refiner."
    coder_system_prompt = "You are a code generator using SymPy."
    debugger_system_prompt = "You are a highly specialized debugger."

    translator_agent = TranslatorAgent(translator_system_prompt)
    refiner_agent = SelfRefinerAgent(refiner_system_prompt)
    coder_agent = CoderAgent(coder_system_prompt)
    debugger_agent = DebuggerAgent(debugger_system_prompt)
    state_manager = SymbolicStateManager()
    sanitizer = CodeSanitizer()

    # Example raw English math problem
    raw_math_problem = "Translate this equation into Python code: x + 2y = 5"

    try:
        # Step 1: Translate the math problem to code
        translated_code = translator_agent.translate(raw_math_problem)
        print("Translated Code:\n", translated_code)

        # Step 2: Refine the code if necessary
        execution_trace = "Initial translation failed."
        refined_code = refiner_agent.refine(translated_code, execution_trace)
        print("Refined Code:\n", refined_code)

        # Step 3: Commit the valid plan to the SymbolicStateManager
        state_manager.register_symbol('x', 'SymPy:x')
        state_manager.register_symbol('y', 'SymPy:y')

        # Step 4: Pass the state brief to the CoderAgent and generate code
        generated_code = coder_agent.generate_code()
        print("Generated Code:\n", generated_code)

        # Step 5: Run the output through our Sanitizer firewall
        sanitized_code = sanitizer.sanitize_code(generated_code)
        if sanitized_code != "Code is safe.":
            raise ValueError(f"Sanitization failed: {sanitized_code}")

        # Step 6: Execute the code in a local SymPy scope
        exec(sanitized_code, {'sp': sp})

    except Exception as e:
        print(f"\n[!] Execution Error encountered: {e}")
        execution_trace = traceback.format_exc()

        # Step 7: Trigger the DebuggerAgent to apply an inline patch up to 3 times
        for _ in range(3):
            try:
                refined_code = debugger_agent.refine_code(refined_code, execution_trace)
                print("Refined Code after Debugging:\n", refined_code)

                # Re-run the sanitized and refined code
                exec(sanitized_code, {'sp': sp})
                break  # If successful, exit the loop
            except Exception as debug_e:
                print(f"\n[!] Debugging Error encountered: {debug_e}")
                execution_trace = traceback.format_exc()

        else:
            raise ValueError("Failed to fix code after multiple debugging attempts.")

if __name__ == "__main__":
    main()
