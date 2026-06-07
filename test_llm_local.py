import sys
import os

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "src")))

try:
    from core.llm import initialize_llm
    from langchain_core.messages import HumanMessage
    
    print("Initializing LLM (codellama)...")
    llm = initialize_llm(model="codellama")
    
    if llm:
        print("Sending test message...")
        response = llm.invoke([HumanMessage(content="Hello, respond with 'Local AI Active'")])
        print(f"Response: {response.content}")
    else:
        print("Failed to initialize LLM.")
except Exception as e:
    print(f"Error: {e}")
