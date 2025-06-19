import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

def get_llm(model="gpt-4o-mini", temperature=0.1, max_tokens=2048):
    return ChatOpenAI(
        model=model,
        temperature=temperature,
        openai_api_key=OPENAI_API_KEY,
        max_tokens=max_tokens
    )