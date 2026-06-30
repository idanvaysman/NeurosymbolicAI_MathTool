import sys
import json
from src.pipeline import initialize_pipeline

def run_integration_test():
    print("=" * 60)
    print("LAUNCHING NEURO-SYMBOLIC INITIALIZATION TEST")
    print("=" * 60)
    
    # 1. Define a classic test problem requiring variable isolation
    test_problem = (
        "A particle accelerates over time. Find its velocity function if "
        "acceleration is a(t) = 3*t and initial velocity at t=0 is 4."
    )
    
    print(f"\n[1/3] Feeding raw input string to pipeline:\n'{test_problem}'")
    
    try:
        # Simulate a response
        simulated_response = '''
        {
          "variables": [
            {
              "name": "t",
              "assumptions": {
                "real": true,
                "positive": true
              }
            },
            {
              "name": "v_0",
              "assumptions": {
                "real": true,
                "constant": true
              }
            },
            {
              "name": "a",
              "assumptions": {
                "real": true
              }
            }
          ]
        }
        '''
        
        # Process the simulated response as if it came from the LLM
        response, symbols = initialize_pipeline(test_problem)
        
        print("\n" + "=" * 40)
        print("PIPELINE TEST SUCCESSFUL!")
        print("=" * 40)
        
        # 3. Print the resulting auto-generated Mathematical Brief
        print("\n[3/3] Inspecting the generated Symbolic State Manager Brief:")
        print(json.dumps(symbols, indent=2))
        
    except Exception as e:
        print("\n" + "!" * 40)
        print("PIPELINE TEST FAILED!")
        print("!" * 40)
        print(f"Detailed Error Traceback: {e}")
        print("\nPossible Troubleshooting Steps:")
        print("1. Double check that your lab machine server at 10.16.121.138 is awake.")
        print("2. Ensure your laptop is on the same local network or VPN as the server.")
        print("3. Verify that the model tag (e.g., 'llama3.1:8b') matches a model downloaded on that server.")

if __name__ == "__main__":
    run_integration_test()
