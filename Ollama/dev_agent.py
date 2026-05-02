import ollama

MODEL = "qwen2.5-coder"

def run(requirement: str) -> str:
    return ollama.chat(
        model=MODEL,
        messages=[
            {"role": "system", "content": "You are an embedded C developer. No malloc."},
            {"role": "user", "content": requirement}
        ]
    )["message"]["content"]