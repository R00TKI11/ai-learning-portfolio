"""
Simple test to verify LLM API configuration works correctly.
Run this to check if your API credentials and endpoint are properly configured.
"""
import sys
from pathlib import Path

# Add the src directory to the path so we can import our modules
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "src"))

from ai_log_triage.llm_client import call_llm


def test_llm_connection():
    """Test basic LLM API connectivity and response."""
    print("Testing LLM API connection...")
    print("-" * 50)

    prompt = "What is the meaning of life?"
    print(f"Prompt: {prompt}")
    print("-" * 200)

    try:
        result = call_llm(prompt)
        print(f"Response: {result}")
        print("-" * 50)
        print("[PASS] Test passed! LLM API is working correctly.")
        return True
    except Exception as e:
        print(f"[FAIL] Test failed with error: {e}")
        print("-" * 50)
        return False


if __name__ == "__main__":
    success = test_llm_connection()
    sys.exit(0 if success else 1)
