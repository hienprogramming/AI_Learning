from pathlib import Path
import re
import subprocess
import sys
import logging
from datetime import datetime
import platform
import os
import json


class RTEConfig:
    """Runtime Environment Configuration"""
    def __init__(self, os_name: str, os_version: str, python_version: str, architecture: str):
        self.os_name = os_name
        self.os_version = os_version
        self.python_version = python_version
        self.architecture = architecture
        self.shell = self._get_shell()
        self.path_sep = os.path.sep
        self.line_sep = os.linesep
        
    def _get_shell(self) -> str:
        """Get default shell for OS"""
        if self.os_name == "Windows":
            return "powershell"
        elif self.os_name == "Darwin":
            return "zsh" if os.path.exists("/bin/zsh") else "bash"
        else:  # Linux
            return "bash"
    
    def to_dict(self) -> dict:
        """Convert RTE config to dictionary"""
        return {
            "os_name": self.os_name,
            "os_version": self.os_version,
            "python_version": self.python_version,
            "architecture": self.architecture,
            "shell": self.shell,
            "path_sep": self.path_sep,
            "line_sep": repr(self.line_sep),
        }


class OSTaskMapper:
    """Map tasks to OS-specific implementations"""
    
    def __init__(self, rte_config: RTEConfig):
        self.rte = rte_config
        self.os_type = rte_config.os_name
        self.task_map = self._initialize_task_map()
    
    def _initialize_task_map(self) -> dict:
        """Initialize OS-specific task mappings"""
        if self.os_type == "Windows":
            return self._get_windows_tasks()
        elif self.os_type == "Darwin":
            return self._get_macos_tasks()
        else:  # Linux
            return self._get_linux_tasks()
    
    def _get_windows_tasks(self) -> dict:
        """Windows-specific task mappings"""
        return {
            "activate_venv": "venv\\Scripts\\Activate.ps1",
            "python_exec": "python.exe",
            "pip_exec": "pip.exe",
            "shell_exec": "powershell",
            "run_script": lambda script: f"powershell -ExecutionPolicy Bypass -File {script}",
            "set_env": lambda key, val: f"$env:{key} = '{val}'",
            "path_join": lambda *args: "\\".join(args),
        }
    
    def _get_macos_tasks(self) -> dict:
        """macOS-specific task mappings"""
        return {
            "activate_venv": "venv/bin/activate",
            "python_exec": "python3",
            "pip_exec": "pip3",
            "shell_exec": "zsh",
            "run_script": lambda script: f"bash {script}",
            "set_env": lambda key, val: f"export {key}={val}",
            "path_join": lambda *args: "/".join(args),
        }
    
    def _get_linux_tasks(self) -> dict:
        """Linux-specific task mappings"""
        return {
            "activate_venv": "venv/bin/activate",
            "python_exec": "python3",
            "pip_exec": "pip3",
            "shell_exec": "bash",
            "run_script": lambda script: f"bash {script}",
            "set_env": lambda key, val: f"export {key}={val}",
            "path_join": lambda *args: "/".join(args),
        }
    
    def get_task(self, task_name: str):
        """Get OS-specific task implementation"""
        return self.task_map.get(task_name)
    
    def get_all_tasks(self) -> dict:
        """Get all OS-specific task mappings"""
        return self.task_map.copy()
    
    def get_activate_venv_command(self) -> str:
        """Get virtualenv activation command"""
        venv_path = self.get_task("activate_venv")
        if self.os_type == "Windows":
            return f"& {venv_path}"
        else:
            return f"source {venv_path}"


def detect_rte() -> RTEConfig:
    """Detect and configure Runtime Environment"""
    os_name = platform.system()  # 'Windows', 'Darwin', 'Linux'
    os_version = platform.release()
    python_version = platform.python_version()
    architecture = platform.machine()
    
    rte = RTEConfig(os_name, os_version, python_version, architecture)
    return rte


def setup_rte() -> tuple:
    """Setup RTE and Task Mapper"""
    rte = detect_rte()
    task_mapper = OSTaskMapper(rte)
    return rte, task_mapper


def log_rte_info(rte: RTEConfig):
    """Log Runtime Environment information"""
    print("\n" + "=" * 60, flush=True)
    print("[*] Runtime Environment Configuration", flush=True)
    print("=" * 60, flush=True)
    for key, value in rte.to_dict().items():
        print(f"    {key:<18}: {value}", flush=True)
    print("=" * 60 + "\n", flush=True)


def log_os_tasks(task_mapper: OSTaskMapper):
    """Log OS-specific task mappings"""
    print("\n" + "=" * 60, flush=True)
    print("[*] OS Task Mappings", flush=True)
    print("=" * 60, flush=True)
    
    tasks = task_mapper.get_all_tasks()
    for task_name, task_impl in tasks.items():
        if callable(task_impl):
            print(f"    {task_name:<20}: <callable>", flush=True)
        else:
            print(f"    {task_name:<20}: {task_impl}", flush=True)
    print("=" * 60 + "\n", flush=True)


def save_rte_config(rte: RTEConfig, output_dir: Path = None):
    """Save RTE configuration to JSON file"""
    if output_dir is None:
        output_dir = Path(".")
    
    output_dir.mkdir(exist_ok=True)
    config_file = output_dir / "rte_config.json"
    
    config_data = {
        "timestamp": datetime.now().isoformat(),
        "rte": rte.to_dict(),
    }
    
    with open(config_file, "w", encoding="utf-8") as f:
        json.dump(config_data, f, indent=2, ensure_ascii=False)
    
    print(f"[RTE] Configuration saved to: {config_file}", flush=True)
    return config_file


def load_autosar_rte_os_mapping(mapping_file: Path = None) -> dict:
    """Load product AUTOSAR RTE to OS task mapping."""
    if mapping_file is None:
        mapping_file = Path("SrcCodeProduct") / "Config" / "Rte_Os_Task_Mapping.json"

    if not mapping_file.exists():
        return {}

    with open(mapping_file, "r", encoding="utf-8") as f:
        return json.load(f)


def log_autosar_rte_os_mapping(mapping_file: Path = None):
    """Log AUTOSAR product RTE/OS mapping if configured."""
    mapping = load_autosar_rte_os_mapping(mapping_file)
    if not mapping:
        print("[WARN] AUTOSAR RTE/OS mapping file not found", flush=True)
        return

    print("\n" + "=" * 60, flush=True)
    print("[*] AUTOSAR Product RTE -> OS Task Mapping", flush=True)
    print("=" * 60, flush=True)
    print(f"    Project: {mapping.get('project', 'unknown')}", flush=True)
    print("", flush=True)

    for task in mapping.get("osTasks", []):
        runnables = ", ".join(task.get("runnables", []))
        print(
            f"    {task['task']:<22} "
            f"period={str(task['periodMs']) + 'ms':<7} "
            f"priority={task['priority']:<2} "
            f"activation={task['activation']:<12} "
            f"-> {runnables}",
            flush=True,
        )

    print("=" * 60 + "\n", flush=True)


def execute_os_task(task_mapper: OSTaskMapper, task_name: str, *args, **kwargs) -> bool:
    """Execute OS-specific task with error handling"""
    try:
        task = task_mapper.get_task(task_name)
        
        if task is None:
            print(f"[ERROR] Task '{task_name}' not supported on {task_mapper.os_type}", flush=True)
            return False
        
        if callable(task):
            result = task(*args, **kwargs)
            print(f"[OK] Task '{task_name}' executed: {result}", flush=True)
            return True
        else:
            print(f"[INFO] Task '{task_name}': {task}", flush=True)
            return True
            
    except Exception as e:
        print(f"[ERROR] Failed to execute task '{task_name}': {str(e)}", flush=True)
        return False


def run_os_command(rte: RTEConfig, command: str, shell: bool = True) -> int:
    """Run OS-specific command using detected shell"""
    try:
        if rte.os_name == "Windows":
            # Use PowerShell on Windows
            result = subprocess.run(
                f"powershell -Command \"{command}\"",
                shell=True,
                capture_output=False
            )
        else:
            # Use bash/zsh on Unix-like systems
            result = subprocess.run(
                command,
                shell=shell,
                executable=rte.shell
            )
        return result.returncode
    except Exception as e:
        print(f"[ERROR] Failed to run OS command: {str(e)}", flush=True)
        return -1


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


class TestReport:
    """Track and report detailed test results, errors, and fixes"""
    
    def __init__(self, module_name: str, files: list):
        self.module_name = module_name
        self.files = files
        self.test_results = []
        self.errors_found = []
        self.fixes_applied = []
        self.code_generated = None
        self.test_feedback = None
        self.code_fixed = None
        
    def log_code_generation(self, code: str):
        """Log generated code"""
        self.code_generated = code
        lines = code.count('\n')
        self.test_results.append({
            "stage": "CODE GENERATION",
            "status": "SUCCESS",
            "details": f"Generated {lines} lines of code",
            "timestamp": datetime.now().isoformat(),
        })
    
    def log_test_feedback(self, feedback: str):
        """Log test feedback and extract errors"""
        self.test_feedback = feedback
        
        # Parse feedback for errors and issues
        self._parse_errors(feedback)
        
        if self.errors_found:
            self.test_results.append({
                "stage": "TESTING",
                "status": "ISSUES FOUND",
                "error_count": len(self.errors_found),
                "timestamp": datetime.now().isoformat(),
            })
        else:
            self.test_results.append({
                "stage": "TESTING",
                "status": "PASSED",
                "details": "No issues found",
                "timestamp": datetime.now().isoformat(),
            })
    
    def _parse_errors(self, feedback: str):
        """Parse and extract errors from feedback"""
        if isinstance(feedback, dict):
            for finding in feedback.get("static_checks", []):
                self.errors_found.append({
                    "line": finding.get("line", "-"),
                    "content": finding.get("message", ""),
                    "severity": finding.get("severity", "INFO"),
                    "check": finding.get("check", "static_check"),
                    "fix_hint": finding.get("fix_hint", ""),
                })

            llm_review = feedback.get("llm_review", {})
            if isinstance(llm_review, dict):
                for category, result in llm_review.items():
                    if category == "summary" or not isinstance(result, dict):
                        continue
                    for failed in result.get("failed", []):
                        self.errors_found.append({
                            "line": "-",
                            "content": f"{category}: {failed}",
                            "severity": "WARNING",
                            "check": "llm_checklist",
                            "fix_hint": "Review the failed checklist item and update the generated code.",
                        })

            if feedback.get("error"):
                self.errors_found.append({
                    "line": "-",
                    "content": f"tester_agent response parse error: {feedback['error']}",
                    "severity": "WARNING",
                    "check": "tester_agent",
                    "fix_hint": "Check the raw LLM response in test_reports.json.",
                })
            return

        # Look for common error patterns
        error_keywords = [
            "error", "failed", "issue", "problem", "warning",
            "bug", "invalid", "missing", "undefined", "syntax"
        ]
        
        lines = feedback.split('\n')
        for i, line in enumerate(lines):
            line_lower = line.lower()
            if any(keyword in line_lower for keyword in error_keywords):
                self.errors_found.append({
                    "line": i + 1,
                    "content": line.strip(),
                    "severity": self._classify_error_severity(line),
                })
    
    def _classify_error_severity(self, line: str) -> str:
        """Classify error severity"""
        line_lower = line.lower()
        if "critical" in line_lower or "fatal" in line_lower:
            return "CRITICAL"
        elif "error" in line_lower:
            return "ERROR"
        elif "warning" in line_lower:
            return "WARNING"
        else:
            return "INFO"
    
    def log_fix_applied(self, fixed_code: str, fix_description: str = None):
        """Log fixes applied"""
        self.code_fixed = fixed_code
        
        # Calculate diff
        if self.code_generated:
            added_lines = fixed_code.count('\n') - self.code_generated.count('\n')
        else:
            added_lines = fixed_code.count('\n')
        
        self.fixes_applied.append({
            "description": fix_description or "Fixes applied by fixer_agent",
            "lines_changed": added_lines,
            "timestamp": datetime.now().isoformat(),
        })
        
        self.test_results.append({
            "stage": "FIXING",
            "status": "FIXES APPLIED",
            "details": f"Fixed {len(self.errors_found)} issues",
            "timestamp": datetime.now().isoformat(),
        })
    
    def to_dict(self) -> dict:
        """Convert report to dictionary"""
        return {
            "module": self.module_name,
            "files": self.files,
            "test_results": self.test_results,
            "errors_found": self.errors_found,
            "test_feedback": self.test_feedback,
            "fixes_applied": self.fixes_applied,
            "summary": {
                "total_stages": len(self.test_results),
                "issues_found": len(self.errors_found),
                "fixes_applied": len(self.fixes_applied),
            }
        }
    
    def print_report(self):
        """Print detailed test report"""
        print(f"\n{'='*70}", flush=True)
        print(f"[REPORT] Test Report for: {self.module_name}", flush=True)
        print(f"{'='*70}", flush=True)
        
        # Print test stages
        print(f"\n[STAGES]", flush=True)
        for stage in self.test_results:
            status_str = f"[{stage['status']}]" if stage['status'] else ""
            details_str = f" - {stage.get('details', '')}" if stage.get('details') else ""
            print(f"  {stage['stage']:<20} {status_str:<20} {details_str}", flush=True)
        
        # Print errors found
        if self.errors_found:
            print(f"\n[ERRORS FOUND] ({len(self.errors_found)} issues)", flush=True)
            for i, error in enumerate(self.errors_found, 1):
                severity = f"[{error['severity']}]"
                check = f" {error.get('check', '')}" if error.get("check") else ""
                print(f"  {i}. {severity:<10} Line {error['line']}:{check} {error['content'][:80]}", flush=True)
                if error.get("fix_hint"):
                    print(f"     Fix hint: {error['fix_hint'][:100]}", flush=True)
        
        # Print fixes applied
        if self.fixes_applied:
            print(f"\n[FIXES APPLIED] ({len(self.fixes_applied)} fix(es))", flush=True)
            for i, fix in enumerate(self.fixes_applied, 1):
                print(f"  {i}. {fix['description']}", flush=True)
                if fix['lines_changed'] != 0:
                    print(f"     Lines changed: {fix['lines_changed']:+d}", flush=True)
        
        print(f"\n{'='*70}\n", flush=True)


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
        # Write to original stdout, gracefully handling encoding issues
        try:
            self.original_stdout.write(text)
        except UnicodeEncodeError:
            enc = getattr(self.original_stdout, "encoding", None) or "utf-8"
            safe_text = text.encode(enc, errors="replace").decode(enc, errors="replace")
            self.original_stdout.write(safe_text)

        if self.file:
            # File is opened with utf-8 encoding; write directly
            try:
                self.file.write(text)
            except Exception:
                # Fallback: write a safe replacement version
                enc = getattr(self.file, "encoding", None) or "utf-8"
                safe_text = text.encode(enc, errors="replace").decode(enc, errors="replace")
                self.file.write(safe_text)

        try:
            self.original_stdout.flush()
        except Exception:
            pass

        if self.file:
            try:
                self.file.flush()
            except Exception:
                pass
    
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
    """Generate code for all modules while each agent owns its execution details."""
    import dev_agent
    import fixer_agent
    import tester_agent

    print("\n" + "=" * 70)
    print(f"[*] {project_name} Code Generation with Detailed Logging")
    print("=" * 70)
    print_agent_plan(modules, agents)

    all_reports = []

    for module_info in modules:
        print(f"\n[MODULE] {module_info['name']}")
        print(f"{'='*70}")
        print(f"  Files:       {', '.join(module_info['files'])}")
        print(f"  Description: {module_info['desc']}")
        print(f"{'='*70}")

        report = TestReport(module_info["name"], module_info["files"])

        try:
            code = dev_agent.execute_module(project_context, module_info, report)
        except Exception as e:
            print(f"  Status:  FAILED - {str(e)}", flush=True)
            continue

        try:
            feedback = tester_agent.execute_module(code, module_info, report)
        except Exception as e:
            print(f"  Status:  Test FAILED - {str(e)}", flush=True)
            continue

        try:
            code = fixer_agent.execute_module(code, feedback, module_info, report)
        except Exception as e:
            print(f"  Status:  Fixing FAILED - {str(e)}", flush=True)
            print("  Fallback: Using original generated code", flush=True)

        print(f"\n[PHASE 4/4] SAVING FILES", flush=True)
        print(f"  Output:  {output_dir.absolute()}", flush=True)
        print("  Files to save:", flush=True)
        for filename in module_info["files"]:
            try:
                content = extract_code(code, file_marker=filename)
                save_file(output_dir, filename, content)
            except Exception as e:
                print(f"      {filename} - FAILED: {str(e)}", flush=True)

        report.print_report()
        all_reports.append(report)

    save_detailed_reports(all_reports, output_dir / "test_reports.json")

    print("\n" + "=" * 70)
    print(f"[SUCCESS] {project_name} generation complete!")
    print(f"[OUTPUT] All files saved to: {output_dir.absolute()}")
    print(f"[REPORTS] Detailed test reports: {output_dir / 'test_reports.json'}")
    print("=" * 70)


def save_detailed_reports(reports: list, output_file: Path):
    """Save all test reports to JSON file"""
    try:
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        reports_data = {
            "generated_at": datetime.now().isoformat(),
            "total_modules": len(reports),
            "modules": [report.to_dict() for report in reports],
        }
        
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(reports_data, f, indent=2, ensure_ascii=False)
        
        print(f"\n[REPORTS] Test reports saved to: {output_file}", flush=True)
    except Exception as e:
        print(f"\n[ERROR] Failed to save test reports: {str(e)}", flush=True)


def run_post_generation_build():
    """Auto-compile and fix generated embedded C code"""
    print("\n" + "=" * 70, flush=True)
    print("[*] POST-GENERATION BUILD & AUTO-FIX", flush=True)
    print("=" * 70, flush=True)
    
    try:
        from compile_manager import CompileManager
        from error_fixer import ErrorFixer
        
        print("\n[STEP 1] COMPILATION", flush=True)
        print("-" * 70, flush=True)
        
        manager = CompileManager()
        c_files = manager.get_all_c_files()
        print(f"Found {len(c_files)} C source files", flush=True)
        
        success, output = manager.compile_check()
        manager.print_summary()
        
        # Check if there are actual errors
        has_errors = len(manager.errors) > 0
        
        if not has_errors:
            print(f"\n[OK] BUILD SUCCESSFUL - No errors found!", flush=True)
            return True
        
        print(f"\n[WARN] COMPILATION ISSUES DETECTED", flush=True)
        print(f"Errors: {len(manager.errors)}", flush=True)
        print(f"Warnings: {len(manager.warnings)}", flush=True)
        
        # Generate error report
        report_file = manager.generate_error_report()
        print(f"\n[REPORT] Error report: {report_file}", flush=True)
        
        # Try to auto-fix
        print("\n[STEP 2] AUTO-FIX", flush=True)
        print("-" * 70, flush=True)
        
        fixer = ErrorFixer()
        
        if not fixer.ai_provider:
            print("\n[WARN] AI provider not available for auto-fixing", flush=True)
            print("    - Set GOOGLE_API_KEY for Gemini")
            print("    - Or ensure Ollama is running")
            print(f"\n    Review error report: {report_file}", flush=True)
            return False
        
        print(f"Using AI Provider: {fixer.ai_provider}", flush=True)
        print(f"Attempting to fix {len(manager.errors)} error(s)...", flush=True)
        
        fix_success = fixer.fix_compilation_errors(max_iterations=3)
        
        if fix_success:
            print(f"\n[OK] ALL ERRORS FIXED!", flush=True)
            print(f"   Fixed {len(fixer.fixed_errors)} error(s)", flush=True)
            return True
        else:
            print(f"\n[WARN] Some errors could not be auto-fixed", flush=True)
            print(f"   Fixed: {len(fixer.fixed_errors)}")
            print(f"   Remaining: {len(fixer.compile_manager.errors)}")
            print(f"\n   Review and fix manually: {report_file}", flush=True)
            return False
    
    except Exception as e:
        print(f"\n[ERROR] ERROR during build/fix: {str(e)}", flush=True)
        import traceback
        traceback.print_exc()
        return False




def main():
    # Setup logging
    logs_dir = Path("Logs")
    logs_dir.mkdir(exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = logs_dir / f"run_main_{timestamp}.txt"
    
    # Setup RTE
    rte, task_mapper = setup_rte()
    
    # Redirect stdout to capture both console and file
    with OutputCapture(log_file) as output:
        sys.stdout = output
        try:
            # Log RTE and OS task information
            log_rte_info(rte)
            log_os_tasks(task_mapper)
            
            # Save RTE configuration
            save_rte_config(rte, logs_dir)
            log_autosar_rte_os_mapping()
            
            # Run environment check first
            print("[*] Running environment check...\n", flush=True)
            result = subprocess.run([sys.executable, "check_environment.py"])
            if result.returncode != 0:
                print("\n[ERROR] Environment is not ready. Fix the warnings above, then run again.\n")
                return result.returncode

            import dev_agent
            import fixer_agent
            import tester_agent

            agents = {
                "dev": dev_agent.label(),
                "test": tester_agent.label(),
                "fix": fixer_agent.label(),
            }

            # ========== CODE GENERATION PHASE ==========
            print("\n\n" + "=" * 70, flush=True)
            print("[*] PHASE 1: CODE GENERATION & TESTING", flush=True)
            print("=" * 70, flush=True)
            
            # Generate Bootloader
            output_dir, project_context, modules = setup_bootloader_modules()
            generate_modules("Bootloader", output_dir, project_context, modules, agents)

            # Generate App (Digital Key)
            output_dir, project_context, modules = setup_app_modules()
            generate_modules("App (Digital Key)", output_dir, project_context, modules, agents)

            # ========== AUTO-COMPILE & AUTO-FIX PHASE ==========
            print("\n\n" + "=" * 70, flush=True)
            print("[*] PHASE 2: EMBEDDED C BUILD & AUTO-FIX", flush=True)
            print("=" * 70, flush=True)
            build_success = run_post_generation_build()

            print("\n" + "=" * 70, flush=True)
            if build_success:
                print("[COMPLETE] All generated code compiled successfully!")
            else:
                print("[ATTENTION] Some build issues remain - review the error report above")
            print("=" * 70)
        finally:
            sys.stdout = output.original_stdout

if __name__ == "__main__":
    sys.exit(main() or 0)
