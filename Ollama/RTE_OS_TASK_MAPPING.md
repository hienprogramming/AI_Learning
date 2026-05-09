# Runtime Environment (RTE) and OS Task Mapping Documentation

## AUTOSAR Product RTE/OS Layer

The project now contains a concrete AUTOSAR-like product structure under
`SrcCodeProduct`:

| Layer | Folder | Main files |
| --- | --- | --- |
| Common AUTOSAR types | `SrcCodeProduct/Common` | `Std_Types.h` |
| RTE | `SrcCodeProduct/Rte` | `Rte.h`, `Rte.c`, `Rte_Cfg.h`, `Rte_Type.h` |
| OS | `SrcCodeProduct/Os` | `Os.h`, `Os.c`, `Os_Cfg.h` |
| Configuration | `SrcCodeProduct/Config` | `Rte_Os_Task_Mapping.json`, `AUTOSAR_PROJECT_MANIFEST.md` |

### AUTOSAR Runnable To OS Task Mapping

| OS task | Activation | Period | Runnable | Responsibility |
| --- | --- | ---: | --- | --- |
| `OsTask_Init` | Autostart | once | `Rte_Runnable_App_Init` | Initialize App, services, and RTE mode |
| `OsTask_App_10ms` | Alarm | 10 ms | `Rte_Runnable_App_10ms` | COM Rx, app command processing, COM Tx |
| `OsTask_App_100ms` | Alarm | 100 ms | `Rte_Runnable_App_100ms` | Slow app status publication |
| `OsTask_Background` | Cooperative | idle | `Rte_Runnable_Background` | Background/idle hook |

Machine-readable mapping is available at
`SrcCodeProduct/Config/Rte_Os_Task_Mapping.json`.

### AUTOSAR Startup Flow

1. `Os_Init()` resets task states and OS tick count.
2. `Os_Start()` activates `OsTask_Init`.
3. `OsTask_Init` dispatches `Rte_Runnable_App_Init()`.
4. `Rte_Runnable_App_Init()` initializes application services and moves RTE to
   `RTE_MODE_RUN`.
5. `Os_Tick()` activates `OsTask_App_10ms` and `OsTask_App_100ms` according to
   their periods.

The older Python classes below still describe the host runtime used by the
generator tool itself. They are intentionally separate from the AUTOSAR product
RTE above.

## Overview

The `main.py` file has been enhanced with **Runtime Environment (RTE)** configuration and **OS Task Mapping** capabilities. These features enable the system to:

- Detect the current operating system and environment
- Provide OS-specific task implementations
- Handle platform differences transparently
- Log environment information for debugging

## Features

### 1. Runtime Environment (RTE) Detection

The `RTEConfig` class automatically detects and stores information about the current runtime environment:

```python
from main import detect_rte

rte = detect_rte()
print(f"OS: {rte.os_name}")
print(f"Python: {rte.python_version}")
print(f"Architecture: {rte.architecture}")
print(f"Shell: {rte.shell}")
```

**Detected Information:**
- **OS Name**: Windows, Darwin (macOS), or Linux
- **OS Version**: Operating system version/release
- **Python Version**: Python interpreter version
- **Architecture**: CPU architecture (AMD64, ARM64, etc.)
- **Shell**: Default shell for the OS (PowerShell, bash, zsh)
- **Path Separator**: OS-specific path separator (\\ or /)

### 2. OS Task Mapping

The `OSTaskMapper` class provides OS-specific implementations for common tasks:

```python
from main import setup_rte

rte, task_mapper = setup_rte()

# Get OS-specific task
python_exec = task_mapper.get_task("python_exec")
shell = task_mapper.get_task("shell_exec")
```

**Available Tasks by OS:**

#### Windows Tasks
```python
{
    "activate_venv": "venv\\Scripts\\Activate.ps1",
    "python_exec": "python.exe",
    "pip_exec": "pip.exe",
    "shell_exec": "powershell",
    "run_script": lambda script: f"powershell -ExecutionPolicy Bypass -File {script}",
    "set_env": lambda key, val: f"$env:{key} = '{val}'",
    "path_join": lambda *args: "\\".join(args),
}
```

#### macOS Tasks
```python
{
    "activate_venv": "venv/bin/activate",
    "python_exec": "python3",
    "pip_exec": "pip3",
    "shell_exec": "zsh",  # or bash if zsh not available
    "run_script": lambda script: f"bash {script}",
    "set_env": lambda key, val: f"export {key}={val}",
    "path_join": lambda *args: "/".join(args),
}
```

#### Linux Tasks
```python
{
    "activate_venv": "venv/bin/activate",
    "python_exec": "python3",
    "pip_exec": "pip3",
    "shell_exec": "bash",
    "run_script": lambda script: f"bash {script}",
    "set_env": lambda key, val: f"export {key}={val}",
    "path_join": lambda *args: "/".join(args),
}
```

## API Reference

### RTEConfig Class

```python
class RTEConfig:
    def __init__(self, os_name, os_version, python_version, architecture)
    def _get_shell() -> str
    def to_dict() -> dict
```

**Methods:**
- `to_dict()`: Returns RTE configuration as a dictionary (JSON-serializable)

### OSTaskMapper Class

```python
class OSTaskMapper:
    def __init__(self, rte_config: RTEConfig)
    def get_task(task_name: str)
    def get_all_tasks() -> dict
    def get_activate_venv_command() -> str
```

**Methods:**
- `get_task(task_name)`: Get OS-specific task implementation
- `get_all_tasks()`: Get all available tasks for current OS
- `get_activate_venv_command()`: Get virtualenv activation command formatted for current OS

### Utility Functions

#### detect_rte() -> RTEConfig
Detects and returns current runtime environment configuration.

```python
rte = detect_rte()
```

#### setup_rte() -> Tuple[RTEConfig, OSTaskMapper]
Sets up both RTE detection and OS task mapper.

```python
rte, task_mapper = setup_rte()
```

#### log_rte_info(rte: RTEConfig)
Logs runtime environment information to console.

```python
log_rte_info(rte)
```

#### log_os_tasks(task_mapper: OSTaskMapper)
Logs OS-specific task mappings to console.

```python
log_os_tasks(task_mapper)
```

#### save_rte_config(rte: RTEConfig, output_dir: Path = None) -> Path
Saves RTE configuration to JSON file.

```python
config_file = save_rte_config(rte, Path("Logs"))
# Creates: Logs/rte_config.json
```

#### execute_os_task(task_mapper: OSTaskMapper, task_name: str, *args, **kwargs) -> bool
Executes OS-specific task with error handling.

```python
success = execute_os_task(task_mapper, "python_exec", "script.py")
```

#### run_os_command(rte: RTEConfig, command: str, shell: bool = True) -> int
Runs OS-specific command using detected shell.

```python
exit_code = run_os_command(rte, "echo 'Hello'")
```

## Integration in main.py

The RTE is automatically initialized when `main()` is called:

```python
def main():
    # Setup RTE
    rte, task_mapper = setup_rte()
    
    # Log RTE information
    log_rte_info(rte)
    log_os_tasks(task_mapper)
    
    # Save RTE configuration
    save_rte_config(rte, logs_dir)
    
    # ... rest of the code
```

## Output Example

When running the main script on Windows:

```
============================================================
[*] Runtime Environment Configuration
============================================================
    os_name            : Windows
    os_version         : 11
    python_version     : 3.12.10
    architecture       : AMD64
    shell              : powershell
    path_sep           : \
    line_sep           : '\\n'
============================================================

============================================================
[*] OS Task Mappings
============================================================
    activate_venv        : venv\Scripts\Activate.ps1
    python_exec          : python.exe
    pip_exec             : pip.exe
    shell_exec           : powershell
    run_script           : <callable>
    set_env              : <callable>
    path_join            : <callable>
============================================================

[RTE] Configuration saved to: Logs/rte_config.json
```

## Use Cases

### 1. Cross-platform Script Execution
```python
rte, task_mapper = setup_rte()
activate_cmd = task_mapper.get_activate_venv_command()
run_os_command(rte, activate_cmd)
```

### 2. OS-specific Path Construction
```python
task_mapper.get_task("path_join")("folder1", "folder2", "file.txt")
# Windows: "folder1\folder2\file.txt"
# Unix: "folder1/folder2/file.txt"
```

### 3. Environment Debugging
```python
# Log RTE info for bug reports
log_rte_info(rte)

# Save RTE config for reproducibility
save_rte_config(rte, Path("debug_info"))
```

### 4. Conditional Task Execution
```python
if rte.os_name == "Windows":
    print("Running Windows-specific code")
else:
    print("Running Unix-like code")
```

## Testing

A test script is provided: `test_rte.py`

```bash
python test_rte.py
```

Output:
```
[TEST] RTE Detection
============================================================
  OS Name:        Windows
  OS Version:     11
  Python Version: 3.12.10
  Architecture:   AMD64
  Shell:          powershell
  Path Separator: \

[TEST] OS Task Mapper
============================================================
  Operating System: Windows
  Available Tasks:
    - activate_venv       : venv\Scripts\Activate.ps1
    - python_exec         : python.exe
    - pip_exec            : pip.exe
    - shell_exec          : powershell
    - run_script          : <callable>
    - set_env             : <callable>
    - path_join           : <callable>

  Virtualenv Activation Command:
    & venv\Scripts\Activate.ps1

[SUCCESS] All tests passed!
```

## Future Enhancements

- Add support for custom task definitions per OS
- Implement task composition for complex workflows
- Add performance monitoring for OS-specific operations
- Support for Docker/container environment detection
- Custom shell selection override
