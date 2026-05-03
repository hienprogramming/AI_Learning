import ollama

MODEL = "llama3"

def run(code: str) -> str:
    return ollama.chat(
        model=MODEL,
        messages=[
            {"role": "system", "content": "You are a strict tester. Find bugs and logical issues."},
            {"role": "user", "content": code}
        ]
    )["message"]["content"]