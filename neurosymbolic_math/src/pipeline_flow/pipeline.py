import json
from src.core.state_manager import SymbolicStateManager
from src.agents.llm_client import call_local_model

def initialize_pipeline(prompt):
    state_manager = SymbolicStateManager()
    
    # Example of registering a symbol
    state_manager.register_symbol("example_symbol", 42)
    
    # Define the system prompt for the LLM client
    system_prompt = (
        "You are an assistant that helps with mathematical problem solving. "
        "Ensure your responses are in JSON format as specified."
    )
    
    # Call the local model with the given prompt and system prompt
    response = call_local_model(system_prompt, prompt)
    
    # Process the response and update symbols if necessary
    try:
        response_data = json.loads(response)  # Assuming JSON-like string response
        for variable in response_data.get("variables", []):
            name = variable.get("name")
            assumptions = variable.get("assumptions", {})
            state_manager.register_symbol(name, assumptions)
    except Exception as e:
        print(f"Error processing response: {e}")
    
    return response, state_manager.symbols
