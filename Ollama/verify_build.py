"""
Build System Verification
Check if embedded C build pipeline is ready to use
"""

import sys
import subprocess
from pathlib import Path
import shutil
import os


def check_compiler() -> tuple[bool, str]:
    """Check if C compiler is available"""
    compilers = ["gcc", "clang", "cc"]
    
    for compiler in compilers:
        if shutil.which(compiler):
            try:
                result = subprocess.run([compiler, "--version"], 
                                      capture_output=True, 
                                      timeout=5,
                                      text=True)
                version = result.stdout.split('\n')[0]
                return True, f"{compiler}: {version}"
            except:
                continue
    
    return False, "No C compiler found (gcc, clang, cc)"


def check_python() -> tuple[bool, str]:
    """Check Python version"""
    try:
        version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
        if sys.version_info >= (3, 8):
            return True, f"Python {version} (OK)"
        else:
            return False, f"Python {version} (requires 3.8+)"
    except:
        return False, "Could not determine Python version"


def check_source_files() -> tuple[bool, str]:
    """Check if C source files are present"""
    workspace_root = Path(__file__).parent
    src_root = workspace_root / "SrcCodeProduct"
    
    if not src_root.exists():
        return False, f"SrcCodeProduct directory not found at {src_root}"
    
    c_files = list(src_root.rglob("*.c"))
    h_files = list(src_root.rglob("*.h"))
    
    if not c_files:
        return False, "No .c files found in SrcCodeProduct"
    
    return True, f"Found {len(c_files)} .c files and {len(h_files)} .h files"


def check_build_scripts() -> tuple[bool, str]:
    """Check if build scripts are present"""
    workspace_root = Path(__file__).parent
    scripts = [
        "build.py",
        "compile_manager.py",
        "error_fixer.py",
        "BUILD_SYSTEM.md"
    ]
    
    missing = []
    for script in scripts:
        if not (workspace_root / script).exists():
            missing.append(script)
    
    if missing:
        return False, f"Missing: {', '.join(missing)}"
    
    return True, f"All {len(scripts)} build scripts found"


def check_ai_provider() -> tuple[bool, str]:
    """Check AI provider configuration"""
    workspace_root = Path(__file__).parent
    env_file = workspace_root / ".env"
    
    # Check Gemini
    try:
        import google.generativeai as genai
        gemini_available = True
    except ImportError:
        gemini_available = False
    
    # Check Ollama
    try:
        import ollama
        ollama_available = True
    except ImportError:
        ollama_available = False
    
    # Check .env
    provider = None
    api_key = None
    
    if env_file.exists():
        content = env_file.read_text()
        for line in content.splitlines():
            if line.startswith("DEV_AGENT_PROVIDER="):
                provider = line.split("=", 1)[1].strip().lower()
            elif line.startswith("GOOGLE_API_KEY="):
                api_key = line.split("=", 1)[1].strip()
    
    status = []
    if gemini_available:
        if api_key:
            status.append(f"✓ Gemini configured")
        else:
            status.append(f"⚠ Gemini installed but GOOGLE_API_KEY not set")
    else:
        status.append(f"✗ Gemini not installed (pip install google-generativeai)")
    
    if ollama_available:
        status.append(f"✓ Ollama available (ensure it's running)")
    else:
        status.append(f"⚠ Ollama not installed")
    
    msg = "\n  ".join(status)
    has_provider = gemini_available or ollama_available
    
    return has_provider, msg


def main():
    """Run all checks"""
    print("\n" + "="*70)
    print("  BUILD SYSTEM VERIFICATION")
    print("="*70 + "\n")
    
    checks = [
        ("Compiler", check_compiler),
        ("Python", check_python),
        ("Source Files", check_source_files),
        ("Build Scripts", check_build_scripts),
        ("AI Provider", check_ai_provider),
    ]
    
    results = []
    all_ok = True
    
    for name, check_func in checks:
        try:
            ok, message = check_func()
            status = "✓" if ok else "✗"
            print(f"{status} {name}:")
            print(f"  {message}\n")
            results.append((name, ok))
            if not ok:
                all_ok = False
        except Exception as e:
            print(f"✗ {name}:")
            print(f"  Error: {e}\n")
            results.append((name, False))
            all_ok = False
    
    print("="*70)
    
    if all_ok:
        print("\n✓ All checks passed! Ready to build.\n")
        print("Quick start:")
        print("  python build.py          # Full pipeline with auto-fix")
        print("  python build.py --no-fix # Only compile")
        print("  python build.py --help   # Show options")
        print()
        return 0
    else:
        failed = [name for name, ok in results if not ok]
        print(f"\n✗ Failed checks: {', '.join(failed)}")
        print("\nFix the issues above and try again.")
        print()
        return 1


if __name__ == "__main__":
    sys.exit(main())
