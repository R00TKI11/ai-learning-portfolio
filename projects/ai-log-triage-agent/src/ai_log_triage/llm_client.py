import os
import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("LLM_OPENROUTER_API_KEY")
ENDPOINT = os.getenv("LLM_ENDPOINT")
MODEL = os.getenv("LLM_DEEPSEEK_FREE_R1T2")

def call_llm(prompt: str) -> str:
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    body = {
        "model": MODEL,
        "prompt": prompt,
        "max_tokens": 200
    }
    resp = requests.post(ENDPOINT, headers=headers, json=body)
    resp.raise_for_status()
    data = resp.json()
    return data["choices"][0]["text"]

