from pathlib import Path
import re
import subprocess
import sys
import logging
from datetime import datetime


def setup_logging():
    """Setup logging to both console and file"""
    logs_dir = Path("Logs")
    logs_dir.mkdir(exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = logs_dir / f"run_main_{timestamp}.txt"
    
    # Create logger
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    
    # File handler
    file_handler = logging.FileHandler(log_file, encoding="utf-8")
    file_handler.setLevel(logging.DEBUG)
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.DEBUG)
    
    # Formatter
    formatter = logging.Formatter("%(message)s")
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    
    # Add handlers
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return log_file


class OutputCapture:
    """Capture print output to both console and file"""
    def __init__(self, log_file):
        self.log_file = log_file
        self.file = None
        self.original_stdout = sys.stdout
        
    def __enter__(self):
        self.file = open(self.log_file, "w", encoding="utf-8")
        return self
    
    def __exit__(self, *args):
        if self.file:
            self.file.close()
    
    def write(self, text):
        self.original_stdout.write(text)
        if self.file:
            self.file.write(text)
        self.original_stdout.flush()
        if self.file:
            self.file.flush()
    
    def flush(self):
        self.original_stdout.flush()
        if self.file:
            self.file.flush()


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


def setup_bootloader_modules():
    """Initialize bootloader project configuration and module definitions"""
    output_dir = Path("SrcCodeProduct") / "BootLoader"
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

    return output_dir, project_context, modules


def setup_app_modules():
    """Initialize app digital key project configuration and module definitions"""
    output_dir = Path("SrcCodeProduct") / "App"
    output_dir.mkdir(parents=True, exist_ok=True)

    project_context = (
        "I am coding for an embedded STM32F103C8T6 microcontroller. "
        "I need to create a digital key application that integrates with Bootloader and ComStack. "
        "Application starts at 0x08008000. Leverage existing Boot_Safety, Boot_Jump, Com, and CanIf modules.\n\n"
    )

    # Define app modules to generate
    modules = [
        {
            "name": "Key Storage",
            "files": ["App_Key_Storage.h", "App_Key_Storage.c"],
            "desc": "Digital key storage with metadata and validation support",
            "req": """Create digital key storage module for STM32F103C8T6 app:
- App_Key_Init(): initialize key storage system
- App_Key_Store(key_id, key_data, key_size): store key in secure area
- App_Key_Retrieve(key_id, key_data, key_size): retrieve stored key
- App_Key_Exists(key_id): check if key exists
- Use Boot_Safety functions for CRC verification
- Static buffers only, no malloc
- Provide App_Key_Storage.h and App_Key_Storage.c""",
        },
        {
            "name": "Key Manager",
            "files": ["App_Key_Manager.h", "App_Key_Manager.c"],
            "desc": "Key lifecycle management, validation, and expiration",
            "req": """Create key manager module for digital key application:
- App_KeyManager_Init(): initialize key manager
- App_KeyManager_ValidateKey(key_id): validate key integrity and expiration
- App_KeyManager_IsKeyValid(key_id): check if key is valid
- App_KeyManager_GetKeyInfo(key_id, info): retrieve key metadata
- Support key versioning and rollback protection
- Use Boot_Safety for verification
- Static allocation only
- Provide App_Key_Manager.h and App_Key_Manager.c""",
        },
        {
            "name": "Security Handler",
            "files": ["App_Security.h", "App_Security.c"],
            "desc": "Cryptographic operations and security primitives",
            "req": """Create security handler module:
- App_Security_Init(): initialize security subsystem
- App_Security_HashData(data, length, hash): compute hash (use CRC32 or similar)
- App_Security_VerifySignature(data, signature): verify digital signature
- App_Security_EncryptKey(key, encrypted): basic encryption wrapper
- App_Security_DecryptKey(encrypted, key): basic decryption wrapper
- Do not use malloc
- Provide App_Security.h and App_Security.c""",
        },
        {
            "name": "ComStack Interface",
            "files": ["App_ComInterface.h", "App_ComInterface.c"],
            "desc": "Communication interface using ComStack (Com, CanIf, CanTp)",
            "req": """Create communication interface module:
- App_ComInterface_Init(): initialize communication layer
- App_ComInterface_SendKeyRequest(request): send key request via CAN
- App_ComInterface_ReceiveKeyData(buffer, length): receive key data
- App_ComInterface_HandleMessage(msg): process incoming CAN messages
- Integrate with Com module for message handling
- Use CanIf for CAN frame transmission
- Static buffers, no malloc
- Provide App_ComInterface.h and App_ComInterface.c""",
        },
        {
            "name": "App Main",
            "files": ["App_Main.h", "App_Main.c"],
            "desc": "Application entry point and main control loop",
            "req": """Create app main module:
- App_Init(): initialize all app subsystems (Key Manager, Security, ComInterface)
- App_Run(): main application loop
- App_ProcessCommands(): handle incoming commands
- App_HandleError(error_code): error handling and recovery
- Validate app integrity using Boot_Safety
- Check application validity using Boot_Jump functions
- Static allocation only
- Provide App_Main.h and App_Main.c""",
        },
    ]

    return output_dir, project_context, modules


def generate_modules(project_name: str, output_dir: Path, project_context: str, modules: list, agents: dict):
    """Generate code for all modules in a project"""
    import dev_agent
    import fixer_agent
    import tester_agent

    print("\n" + "=" * 60)
    print(f"[*] {project_name} Code Generation")
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
    print(f"[SUCCESS] {project_name} generation complete!")
    print(f"[OUTPUT] All files saved to: {output_dir.absolute()}")
    print("=" * 60)


def main():
    # Setup logging
    logs_dir = Path("Logs")
    logs_dir.mkdir(exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = logs_dir / f"run_main_{timestamp}.txt"
    
    # Redirect stdout to capture both console and file
    with OutputCapture(log_file) as output:
        sys.stdout = output
        try:
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

            # Generate Bootloader
            output_dir, project_context, modules = setup_bootloader_modules()
            generate_modules("Bootloader", output_dir, project_context, modules, agents)

            # Generate App (Digital Key)
            output_dir, project_context, modules = setup_app_modules()
            generate_modules("App (Digital Key)", output_dir, project_context, modules, agents)

            print("\n" + "=" * 60)
            print("[SUCCESS] All projects generation complete!")
            print("=" * 60)
        finally:
            sys.stdout = output.original_stdout

if __name__ == "__main__":
    sys.exit(main() or 0)
