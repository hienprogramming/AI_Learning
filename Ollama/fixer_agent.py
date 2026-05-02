import ollama

MODEL = "qwen2.5-coder"

def run(code: str, feedback: str) -> str:
    return ollama.chat(
        model=MODEL,
        messages=[
            {"role": "system", "content": "Fix the code based on tester feedback."},
            {"role": "user", "content": f"{code}\n\nIssues:\n{feedback}"}
        ]
    )["message"]["content"]