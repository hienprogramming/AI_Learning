#!/usr/bin/env python3
"""Test host RTE and AUTOSAR RTE/OS task mapping functionality"""

from main import setup_rte, detect_rte
import json
from pathlib import Path

def test_rte_detection():
    """Test RTE detection"""
    print("[TEST] RTE Detection")
    print("=" * 60)
    
    rte = detect_rte()
    print(f"  OS Name:        {rte.os_name}")
    print(f"  OS Version:     {rte.os_version}")
    print(f"  Python Version: {rte.python_version}")
    print(f"  Architecture:   {rte.architecture}")
    print(f"  Shell:          {rte.shell}")
    print(f"  Path Separator: {rte.path_sep}")
    print()

def test_os_task_mapper():
    """Test OS task mapper"""
    print("[TEST] OS Task Mapper")
    print("=" * 60)
    
    rte, mapper = setup_rte()
    
    print(f"  Operating System: {mapper.os_type}")
    print(f"  Available Tasks:")
    
    tasks = mapper.get_all_tasks()
    for task_name, task_impl in tasks.items():
        if callable(task_impl):
            print(f"    - {task_name:<20}: <callable>")
        else:
            print(f"    - {task_name:<20}: {task_impl}")
    
    print()
    
    # Test venv activation command
    venv_cmd = mapper.get_activate_venv_command()
    print(f"  Virtualenv Activation Command:")
    print(f"    {venv_cmd}")
    print()


def test_autosar_rte_os_project():
    """Validate AUTOSAR-like RTE/OS project artifacts"""
    print("[TEST] AUTOSAR RTE/OS Project")
    print("=" * 60)

    required_files = [
        Path("SrcCodeProduct/Common/Std_Types.h"),
        Path("SrcCodeProduct/Rte/Rte.h"),
        Path("SrcCodeProduct/Rte/Rte.c"),
        Path("SrcCodeProduct/Rte/Rte_Cfg.h"),
        Path("SrcCodeProduct/Rte/Rte_Type.h"),
        Path("SrcCodeProduct/Os/Os.h"),
        Path("SrcCodeProduct/Os/Os.c"),
        Path("SrcCodeProduct/Os/Os_Cfg.h"),
        Path("SrcCodeProduct/Config/Rte_Os_Task_Mapping.json"),
        Path("SrcCodeProduct/Config/AUTOSAR_PROJECT_MANIFEST.md"),
    ]

    for file_path in required_files:
        if not file_path.exists():
            raise AssertionError(f"Missing AUTOSAR artifact: {file_path}")
        print(f"    [OK] {file_path}")

    mapping_file = Path("SrcCodeProduct/Config/Rte_Os_Task_Mapping.json")
    mapping = json.loads(mapping_file.read_text(encoding="utf-8"))
    rte_source = Path("SrcCodeProduct/Rte/Rte.c").read_text(encoding="utf-8")
    os_source = Path("SrcCodeProduct/Os/Os.c").read_text(encoding="utf-8")

    for task in mapping["osTasks"]:
        task_name = task["task"]
        if task_name not in os_source:
            raise AssertionError(f"Task {task_name} is in mapping but not in Os.c")
        for runnable in task["runnables"]:
            if runnable not in rte_source and runnable not in os_source:
                raise AssertionError(f"Runnable {runnable} is not implemented")
        print(f"    [MAP] {task_name:<20} -> {', '.join(task['runnables'])}")

    print()

if __name__ == "__main__":
    test_rte_detection()
    test_os_task_mapper()
    test_autosar_rte_os_project()
    print("[SUCCESS] All tests passed!")
