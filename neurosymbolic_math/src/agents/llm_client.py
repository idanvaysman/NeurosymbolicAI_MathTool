"""
src/agents/llm_client.py

Handles the direct network connection to the local cluster hosting the Qwen model.
Bypasses intermediate routing frameworks to avoid index parsing exceptions.
"""

try:
    from openai import OpenAI
except ImportError:
    # Fallback absolute namespace routing for strict virtual environments
    from openai.client import OpenAI

# Initialize the native client targeting your network machine's Ollama port
client = OpenAI(
    base_url="http://10.16.121.138:11434/v1",  # Your local lab server interface
    api_key="ollama"                           # Required dummy placeholder string
)

def call_local_model(system_prompt: str, user_content: str, require_json: bool = True) -> str:
    """
    Executes a deterministic inference pass against the local network Qwen instance
    using the structural Chat Completions protocol.
    
    Args:
        system_prompt (str): Defines the operational guardrails/identity of the agent.
        user_content (str): The dynamic data payload or problem instance.
        require_json (bool): If True, appends rigorous grammar formatting rules to the prompt.
        
    Returns:
        str: Cleaned, whitespace-shaved raw response content from the model.
    """
    try:
        # If structural data is requested, we inject formatting boundaries directly
        # into the system role to bypass version-brittle client API parameters.
        if require_json:
            system_prompt += (
                "\n\nCRITICAL: You must respond ONLY with a raw JSON object. "
                "Do not include any conversational text, pleasantries, explanations, "
                "markdown formatting blocks, or backticks (e.g., do NOT wrap in ```json). "
                "Return pure valid JSON syntax matching the requested target schema."
            )

        # Execute the network call over the local network interface
        response = client.chat.completions.create(
            model="qwen2.5-coder:14b-instruct-q6_K",  # Adjust if your cluster uses a distinct tag flavor (e.g., 'qwen2.5-math')
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_content}
            ],
            temperature=0.0,     # Enforce strict determinism for symbolic translations
            max_tokens=1000      # Ensure sufficient token headroom for deep AST dictionaries
        )
        
        # Clean trailing lines or padding whitespaces immediately upon retrieval
        return response.choices[0].message.content.strip()

    except Exception as e:
        print(f"\n[!] Network Pipeline Connection Error encountered inside llm_client.py: {e}")
        raise e
