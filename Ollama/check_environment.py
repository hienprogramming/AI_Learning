#!/usr/bin/env python3
"""
Environment checker for the local AI agents.

The script checks the Python packages used by dev_agent.py, tester_agent.py,
and fixer_agent.py. Missing Python packages are installed automatically into
the same interpreter that runs this file.
"""

from __future__ import annotations

import argparse
import importlib.util
import os
import re
import subprocess
import sys
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parent
LOG_DIR = ROOT_DIR / "Logs"

REQUIRED_PACKAGES = {
    "google-generativeai": "google.generativeai",
    "ollama": "ollama",
}

OPTIONAL_PACKAGES = {
    "openai": "openai",
}

LOG_MODULE_PACKAGE_MAP = {
    "google.generativeai": "google-generativeai",
    "ollama": "ollama",
    "openai": "openai",
}

REQUIRED_ENV_VARS = ["GOOGLE_API_KEY"]
OPTIONAL_ENV_VARS = ["OPENAI_API_KEY"]
REQUIRED_OLLAMA_MODELS = ["llama3", "qwen2.5-coder"]


def load_local_env() -> None:
    env_file = ROOT_DIR / ".env"
    if not env_file.exists():
        return

    for line in env_file.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


def module_installed(module_name: str) -> bool:
    return importlib.util.find_spec(module_name) is not None


def run_command(command: list[str], timeout: int = 120) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        command,
        cwd=ROOT_DIR,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        timeout=timeout,
    )


def install_package(package_name: str) -> bool:
    print(f"  Installing {package_name} with {sys.executable}")
    result = run_command([sys.executable, "-m", "pip", "install", package_name], timeout=300)
    if result.returncode == 0:
        print(f"  [OK] {package_name} installed")
        return True

    print(f"  [FAILED] {package_name}")
    print(result.stdout.strip())
    return False


def latest_log_file() -> Path | None:
    if not LOG_DIR.exists():
        return None

    logs = sorted(
        LOG_DIR.glob("run_main_*.txt"),
        key=lambda path: path.stat().st_mtime,
        reverse=True,
    )
    return logs[0] if logs else None


def packages_from_latest_log() -> dict[str, str]:
    log_file = latest_log_file()
    if not log_file:
        return {}

    text = log_file.read_text(encoding="utf-8", errors="replace")
    missing_modules = set(re.findall(r"No module named ['\"]([^'\"]+)['\"]", text))
    packages: dict[str, str] = {}

    for module_name in missing_modules:
        package_name = LOG_MODULE_PACKAGE_MAP.get(module_name)
        if package_name:
            packages[package_name] = module_name

    if packages:
        print(f"\n[LOG] Latest log: {log_file}")
        for package_name, module_name in packages.items():
            print(f"  Found missing module in log: {module_name} -> {package_name}")

    return packages


def check_packages(auto_install: bool) -> bool:
    print("\n[CHECK] Python packages")
    packages = dict(REQUIRED_PACKAGES)
    packages.update(packages_from_latest_log())

    missing: list[str] = []
    for package_name, module_name in packages.items():
        if module_installed(module_name):
            print(f"  [OK] {package_name} ({module_name})")
        else:
            print(f"  [MISSING] {package_name} ({module_name})")
            missing.append(package_name)

    for package_name, module_name in OPTIONAL_PACKAGES.items():
        status = "OK" if module_installed(module_name) else "OPTIONAL"
        print(f"  [{status}] {package_name} ({module_name})")

    if not missing:
        return True

    if not auto_install:
        print("  Auto install disabled. Run without --no-install to install missing packages.")
        return False

    failed = [package for package in missing if not install_package(package)]
    if failed:
        print(f"  [ERROR] Failed packages: {', '.join(failed)}")
        return False

    still_missing = [
        package
        for package, module in packages.items()
        if package in missing and not module_installed(module)
    ]
    if still_missing:
        print(f"  [ERROR] Installed but still not importable: {', '.join(still_missing)}")
        return False

    return True


def check_environment_variables() -> bool:
    print("\n[CHECK] Environment variables")
    ok = True

    for var_name in REQUIRED_ENV_VARS:
        value = os.getenv(var_name)
        if value:
            print(f"  [OK] {var_name} is set")
        else:
            print(f"  [MISSING] {var_name}")
            print(f"      PowerShell: $env:{var_name} = 'your-key'")
            ok = False

    for var_name in OPTIONAL_ENV_VARS:
        value = os.getenv(var_name)
        status = "OK" if value else "OPTIONAL"
        print(f"  [{status}] {var_name}")

    return ok


def check_ollama(install_models: bool) -> bool:
    print("\n[CHECK] Ollama service and models")

    if not module_installed("ollama"):
        print("  [SKIP] Python package 'ollama' is not importable yet")
        return False

    try:
        import ollama

        response = ollama.list()
    except Exception as exc:
        print(f"  [ERROR] Cannot connect to Ollama: {exc}")
        print("      Start Ollama, then run this script again.")
        return False

    installed_models = set()
    models = response.get("models", []) if isinstance(response, dict) else getattr(response, "models", [])
    for model in models:
        if isinstance(model, dict):
            name = model.get("name") or model.get("model")
        else:
            name = getattr(model, "name", None) or getattr(model, "model", None)
        if name:
            installed_models.add(name)

    ok = True
    for model_name in REQUIRED_OLLAMA_MODELS:
        has_model = any(
            installed == model_name or installed.startswith(f"{model_name}:")
            for installed in installed_models
        )
        if has_model:
            print(f"  [OK] model {model_name}")
            continue

        print(f"  [MISSING] model {model_name}")
        if install_models:
            print(f"  Pulling {model_name}...")
            pull_result = run_command(["ollama", "pull", model_name], timeout=1800)
            if pull_result.returncode == 0:
                print(f"  [OK] model {model_name} pulled")
                continue
            else:
                print(pull_result.stdout.strip())
        ok = False

    return ok


def warn_if_local_venv_looks_moved() -> None:
    cfg = ROOT_DIR / "venv" / "pyvenv.cfg"
    if not cfg.exists():
        return

    text = cfg.read_text(encoding="utf-8", errors="replace")
    expected = str(ROOT_DIR / "venv")
    if expected.lower() not in text.lower():
        print("\n[WARNING] Local venv looks moved or copied.")
        print(f"  Expected venv path: {expected}")
        print("  Current script will install packages into:")
        print(f"  {sys.executable}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Check and prepare AI agent environment.")
    parser.add_argument("--no-install", action="store_true", help="Only check; do not install packages.")
    parser.add_argument(
        "--install-models",
        action="store_true",
        help="Pull missing Ollama models. This may download large files.",
    )
    args = parser.parse_args()
    load_local_env()

    print("=" * 70)
    print("[*] AI Agent Environment Checker")
    print("=" * 70)
    print(f"[INFO] Python: {sys.executable}")
    print(f"[INFO] Version: {sys.version.split()[0]}")

    warn_if_local_venv_looks_moved()

    python_ok = sys.version_info >= (3, 10)
    if python_ok:
        print("[OK] Python version is supported")
    else:
        print("[ERROR] Python 3.10+ is recommended")

    packages_ok = check_packages(auto_install=not args.no_install)
    env_ok = check_environment_variables()
    ollama_ok = check_ollama(install_models=args.install_models)

    print("\n" + "=" * 70)
    if python_ok and packages_ok and env_ok and ollama_ok:
        print("[SUCCESS] Environment is ready for the agents.")
        return 0

    print("[WARNING] Environment still needs attention.")
    if not ollama_ok:
        print("  Tip: run with --install-models to pull missing Ollama models automatically.")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
