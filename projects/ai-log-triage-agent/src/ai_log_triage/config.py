import os
from dotenv import load_dotenv

load_dotenv()  # Loads .env file automatically

class Settings:
    #OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    #ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
    #HF_TOKEN = os.getenv("HF_TOKEN")
    #LOG_INPUT_DIR = os.getenv("LOG_INPUT_DIR", "./data/input_logs")
    #MODEL_NAME = os.getenv("MODEL_NAME", "gpt-4o-mini")
    LLM_OPENROUTER_API_KEY = os.getenv("LLM_OPENROUTER_API_KEY")
    LLM_ENDPOINT = os.getenv("LLM_ENDPOINT")
    LLM_DEEPSEEK_FREE_R1T2 = os.getenv("LLM_DEEPSEEK_FREE_R1T2")
    LLM_GROK_FREE_41_FAST = os.getenv("LLM_GROK_FREE_41_FAST")

settings = Settings()

