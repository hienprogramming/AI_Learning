from pathlib import Path
import re

import dev_agent
import fixer_agent
import tester_agent


def extract_code(response: str) -> str:
    match = re.search(r"```(?:c)?\s*(.*?)```", response, re.DOTALL | re.IGNORECASE)
    if match:
        return match.group(1).strip() + "\n"

    return response.strip() + "\n"


def main():
    req = (
        "Write a simple embedded C program that blinks an LED connected to GPIO pin 13 every second. Use a timer interrupt for the blinking logic. The code should be suitable for an ARM Cortex-M microcontroller and should not use dynamic memory allocation (no malloc)."
    )
    output_dir = Path("SrcCodeProduct")
    output_dir.mkdir(exist_ok=True)

    code = dev_agent.run(req)
    print("=== CODE ===\n", code)

    feedback = tester_agent.run(code)
    print("\n=== TEST ===\n", feedback)

    fixed = fixer_agent.run(code, feedback)
    print("\n=== FIXED ===\n", fixed)

    output_file = output_dir / "IOHW.c"
    output_file.write_text(extract_code(fixed), encoding="utf-8")
    print(f"Created {output_file}")

if __name__ == "__main__":
    main()
