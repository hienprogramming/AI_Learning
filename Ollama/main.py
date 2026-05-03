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

    output_dir = Path("SrcCodeProduct")
    output_dir.mkdir(exist_ok=True)

    # Define AUTOSAR Comstack modules to generate
    modules = [
        {
            "name": "ComStack_Types",
            "files": ["ComStack_Types.h"],
            "desc": "Type definitions and configuration",
            "req": """Create AUTOSAR ComStack type definitions header file (ComStack_Types.h) with:
- Signal types (uint8, uint16, uint32, etc.)
- PDU configuration structures
- Signal configuration structures  
- Com_SignalType enum
- PduR_PduIdType, CanIf_HrhType definitions
- Maximum limits (MAX_SIGNALS=8, MAX_PDUS=4)
- Status and return codes (E_OK, E_NOT_OK)
No implementation, only type definitions and macros."""
        },
        {
            "name": "COM Module",
            "files": ["Com.h", "Com.c"],
            "desc": "Signal encoding/decoding, filtering, triggering",
            "req": """Implement AUTOSAR COM Module (Com.c, Com.h) for ARM Cortex-M:
- Com_Init(): Initialize COM module
- Com_SendSignal(SignalId, SignalDataPtr): Send signal
- Com_ReceiveSignal(SignalId, SignalDataPtr): Receive signal
- Com_MainFunctionTx(): Main function for transmission (10ms)
- Com_MainFunctionRx(): Main function for reception (10ms)
- Signal filtering and triggering logic
- Event-triggered and periodic transmission support
- Support 8 signals maximum
- Use static buffers (no malloc)
- For STM32F4, include types from ComStack_Types.h"""
        },
        {
            "name": "PDU Router",
            "files": ["PduR.h", "PduR.c"],
            "desc": "PDU routing between layers",
            "req": """Implement AUTOSAR PDU Router Module (PduR.c, PduR.h) for ARM Cortex-M:
- PduR_Init(): Initialize PDU Router
- PduR_Transmit(PduId, PduInfoPtr): Transmit PDU down
- PduR_RxIndication(PduId, PduInfoPtr): Indicate PDU reception
- PduR_TxConfirmation(PduId): Confirm transmission
- Static routing table for COM <-> CanIf
- Handle 4 PDUs maximum
- Use static buffers (no malloc)
- Clear separation between upper and lower layers
- For STM32F4, include types from ComStack_Types.h"""
        },
        {
            "name": "CAN Interface",
            "files": ["CanIf.h", "CanIf.c"],
            "desc": "CAN frame transmission/reception",
            "req": """Implement AUTOSAR CAN Interface Module (CanIf.c, CanIf.h) for ARM Cortex-M:
- CanIf_Init(): Initialize CAN interface
- CanIf_Transmit(CanTxPduId, PduInfoPtr): Send CAN frame
- CanIf_RxIndication(HrhId, CanId, DataPtr): Receive CAN frame callback
- CanIf_TxConfirmation(CanTxPduId): TX confirmation callback
- Frame ID mapping (PDU ID <-> CAN ID)
- Support 4 CAN frames (IDs: 0x100, 0x200, 0x300, 0x400)
- Hardware abstraction for STM32F4 CAN
- Use static buffers (no malloc)
- Include types from ComStack_Types.h"""
        },
        {
            "name": "CAN Transport Protocol",
            "files": ["CanTp.h", "CanTp.c"],
            "desc": "Segmentation, reassembly, flow control",
            "req": """Implement AUTOSAR CAN Transport Protocol Module (CanTp.c, CanTp.h) for ARM Cortex-M:
- CanTp_Init(): Initialize CAN TP
- CanTp_Transmit(TxPduId, PduInfoPtr): Transmit large data (segmentation)
- CanTp_RxIndication(RxPduId, PduInfoPtr): Receive segmented data
- CanTp_MainFunction(): Main state machine (10ms)
- Consecutive Frame numbering
- Flow Control handling (CTS, WAIT, OVERFLOW)
- Timeout management (BS=0, STmin=0)
- Support SF (Single Frame) and FF (First Frame) types
- Use static buffers (no malloc)
- For STM32F4, include types from ComStack_Types.h"""
        }
    ]

    print("=" * 60)
    print("[*] AUTOSAR Comstack Code Generation")
    print("=" * 60)
    print_agent_plan(modules, agents)

    for module_info in modules:
        print(f"\n[MODULE] Generating: {module_info['name']}")
        print(f"         Files: {', '.join(module_info['files'])}")
        print(f"         Desc: {module_info['desc']}")
        
        # Generate code for this module
        log_agent("dev_agent", module_info["name"], "Loading module")
        code = dev_agent.run(module_info['req'])
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
    print("[SUCCESS] AUTOSAR Comstack generation complete!")
    print(f"[OUTPUT] All files saved to: {output_dir.absolute()}")
    print("=" * 60)

if __name__ == "__main__":
    sys.exit(main() or 0)
