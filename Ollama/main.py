from pathlib import Path
import re
import subprocess
import sys


def extract_code(response: str, file_marker: str = None) -> str:
    """Extract code block from response, optionally filtered by file marker"""
    if file_marker:
        # Try to find code block after file marker
        pattern = rf"{file_marker}.*?```(?:c|h)?\s*(.*?)```"
        match = re.search(pattern, response, re.DOTALL | re.IGNORECASE)
        if match:
            return match.group(1).strip() + "\n"
    
    # Fallback: extract first code block
    match = re.search(r"```(?:c|h)?\s*(.*?)```", response, re.DOTALL | re.IGNORECASE)
    if match:
        return match.group(1).strip() + "\n"

    return response.strip() + "\n"


def save_file(output_dir: Path, filename: str, content: str):
    """Save content to file"""
    output_file = output_dir / filename
    output_file.write_text(content, encoding="utf-8")
    print(f"      [OK] {filename}")
    return output_file


def log_agent(agent_name: str, module_name: str, message: str):
    print(f"         [{agent_name}] {message}: {module_name}", flush=True)


def print_agent_plan(modules, agents):
    print("\n" + "=" * 60, flush=True)
    print("[*] Agent/module pre-check plan", flush=True)
    print("=" * 60, flush=True)
    print("[AGENTS]", flush=True)
    for role, agent_name in agents.items():
        print(f"        {role:<6}: {agent_name}", flush=True)
    print("", flush=True)

    for module_info in modules:
        module_name = module_info["name"]
        files = ", ".join(module_info["files"])
        print(f"[CHECK] {module_name} -> {files}", flush=True)
        print(f"        dev    -> {agents['dev']}    : generate code", flush=True)
        print(f"        test   -> {agents['test']}   : review generated code", flush=True)
        print(f"        fix    -> {agents['fix']}    : fix issues from tester feedback", flush=True)


def main():
    # Run environment check first
    print("[*] Running environment check...\n", flush=True)
    result = subprocess.run([sys.executable, "check_environment.py"])
    if result.returncode != 0:
        print("\n[ERROR] Environment is not ready. Fix the warnings above, then run again.\n")
        return result.returncode

    import dev_agent
    import fixer_agent
    import tester_agent

    dev_provider = getattr(dev_agent, "DEV_AGENT_PROVIDER", "gemini")
    if dev_provider == "ollama":
        dev_label = f"dev_agent / Ollama:{dev_agent.OLLAMA_FALLBACK_MODEL}"
    else:
        dev_label = (
            f"dev_agent / Gemini:{dev_agent.GEMINI_MODEL} "
            f"(fallback Ollama:{dev_agent.OLLAMA_FALLBACK_MODEL})"
        )

    agents = {
        "dev": dev_label,
        "test": f"tester_agent / Ollama:{tester_agent.MODEL}",
        "fix": f"fixer_agent / Ollama:{fixer_agent.MODEL}",
    }

    output_dir = Path("BootLoader")
    output_dir.mkdir(exist_ok=True)

    project_context = (
        "I am coding for an embedded STM32F103C8T6 microcontroller. "
        "I need to create a bootloader with the following modules:\n\n"
    )

    # Define bootloader modules to generate
    modules = [
        {
            "name": "MCU Base",
            "files": ["Boot_Mcu.h", "Boot_Mcu.c"],
            "desc": "Startup support, interrupt control, and flash memory primitives",
            "req": """Create basic MCU support code for an STM32F103C8T6 bootloader:
- Boot_Mcu_Init(): initialize MCU resources needed by the bootloader
- Boot_Mcu_DeInit(): deinitialize resources before jumping to application
- Boot_Mcu_DisableInterrupts(): disable interrupts safely
- Boot_Flash_Erase(address, length): erase flash pages/sectors
- Boot_Flash_Write(address, data, length): write firmware bytes to flash
- Boot_Flash_Read(address, data, length): read flash bytes
- Use static allocation only, no malloc
- Provide Boot_Mcu.h and Boot_Mcu.c""",
        },
        {
            "name": "Boot Jump",
            "files": ["Boot_Jump.h", "Boot_Jump.c"],
            "desc": "Bootloader/application memory layout and jump-to-application logic",
            "req": """Create bootloader jump code for STM32F103C8T6:
- Bootloader starts at 0x08000000
- Application starts at 0x08008000
- Boot_IsApplicationValid(): validate application stack pointer and reset vector
- Boot_JumpToApplication(): set MSP and jump to application reset handler
- Disable interrupts before jump
- Do not use malloc
- Provide Boot_Jump.h and Boot_Jump.c""",
        },
        {
            "name": "Firmware Update",
            "files": ["Boot_Update.h", "Boot_Update.c"],
            "desc": "Firmware update flow over UART with erase, write, verify, and jump commands",
            "req": """Create firmware update logic for a small STM32F103C8T6 bootloader:
- Support commands CMD_ERASE, CMD_WRITE, CMD_VERIFY, CMD_JUMP
- Use UART as the transport abstraction
- Boot_Update_Init(): initialize update state
- Boot_Update_ProcessPacket(data, length): parse and execute one packet
- Write firmware to application address 0x08008000
- Verify image with CRC before allowing jump
- Use static buffers only, no malloc
- Provide Boot_Update.h and Boot_Update.c""",
        },
        {
            "name": "Boot Protocol",
            "files": ["Boot_Protocol.h", "Boot_Protocol.c"],
            "desc": "Packet protocol definitions and parser for bootloader commands",
            "req": """Create a simple bootloader protocol module:
- Define command IDs CMD_ERASE, CMD_WRITE, CMD_VERIFY, CMD_JUMP
- Define ACK/NACK response codes
- Define packet format with command, address, length, payload, and CRC
- Boot_Protocol_ParsePacket(): validate and decode a received packet
- Boot_Protocol_BuildResponse(): build ACK/NACK response packet
- No dynamic allocation
- Provide Boot_Protocol.h and Boot_Protocol.c""",
        },
        {
            "name": "Boot Safety",
            "files": ["Boot_Safety.h", "Boot_Safety.c"],
            "desc": "CRC check, image validation, rollback hooks, and dual-bank metadata",
            "req": """Create bootloader safety support code:
- CRC32 calculation for firmware image verification
- Image metadata structure with version, size, start address, CRC, and state
- Boot_Safety_VerifyImage(): verify metadata and CRC
- Boot_Safety_MarkImageValid(): mark an image as valid
- Boot_Safety_RequestRollback(): set rollback flag if update fails
- Include dual-bank A/B metadata concepts
- Use static allocation only, no malloc
- Provide Boot_Safety.h and Boot_Safety.c""",
        },
    ]

    print("=" * 60)
    print("[*] Bootloader Code Generation")
    print("=" * 60)
    print_agent_plan(modules, agents)

    for module_info in modules:
        print(f"\n[MODULE] Generating: {module_info['name']}")
        print(f"         Files: {', '.join(module_info['files'])}")
        print(f"         Desc: {module_info['desc']}")
        
        # Generate code for this module
        log_agent("dev_agent", module_info["name"], "Loading module")
        code = dev_agent.run(project_context + module_info['req'])
        log_agent("dev_agent", module_info["name"], "Finished module")
        print("         [OK] Code generated", flush=True)

        # Test the generated code
        log_agent("tester_agent", module_info["name"], "Loading module")
        feedback = tester_agent.run(code)
        log_agent("tester_agent", module_info["name"], "Finished module")
        print("         [OK] Testing completed", flush=True)

        # Fix any issues
        log_agent("fixer_agent", module_info["name"], "Loading module")
        fixed = fixer_agent.run(code, feedback)
        log_agent("fixer_agent", module_info["name"], "Finished module")
        print("         [OK] Fixes applied", flush=True)

        # Save generated files
        print("         Saving files:")
        for filename in module_info['files']:
            content = extract_code(fixed, file_marker=filename)
            save_file(output_dir, filename, content)

    print("\n" + "=" * 60)
    print("[SUCCESS] Bootloader generation complete!")
    print(f"[OUTPUT] All files saved to: {output_dir.absolute()}")
    print("=" * 60)

if __name__ == "__main__":
    sys.exit(main() or 0)
