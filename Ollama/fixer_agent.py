import ollama

MODEL = "qwen2.5-coder"

def run(code: str, feedback: str) -> str:
    return ollama.chat(
        model=MODEL,
        messages=[
            {
                "role": "system",
                "content": (
                    "You are an embedded C fixer. Fix only the issues listed by the tester. "
                    "Preserve the requested module behavior, use static allocation only, "
                    "define or include missing symbols, add bounds/null checks, and return "
                    "only the corrected C/header code blocks with filenames when possible."
                ),
            },
            {"role": "user", "content": f"CODE:\n{code}\n\nTESTER ISSUES:\n{feedback}"},
        ]
    )["message"]["content"]
