import json
from src.agents.llm_client import call_local_model

TRANSLATOR_SYSTEM_PROMPT = """
You are a strict mathematical parser. Your task is to extract variables from the given input string and map them to our JSON schema.
The JSON schema should contain two keys: "name" and "assumptions".
The "assumptions" key should be an array of strings describing the assumptions about the variable (e.g., real, positive, constant, integer).

Example:
Input: "A particle accelerates over time. Find its velocity function if acceleration is a(t) = 3*t and initial velocity at t=0 is 4."
Output:
{
  "variables": [
    {
      "name": "a",
      "assumptions": ["real", "positive"]
    },
    {
      "name": "t",
      "assumptions": ["real", "positive"]
    },
    {
      "name": "v_0",
      "assumptions": ["real", "constant"]
    }
  ]
}
"""

def test_translator():
    raw_input = "A fluid flows through a pipe at a constant initial velocity v_0. Find its position x after a positive time duration t, given that its acceleration is zero."
    response = call_local_model(TRANSLATOR_SYSTEM_PROMPT, raw_input)
    print(json.dumps(response, indent=2))

if __name__ == '__main__':
    test_translator()
