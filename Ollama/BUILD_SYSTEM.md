# 🔨 Embedded C Build Pipeline

Complete compilation system for embedded C code with automatic error detection and AI-powered fixing.

## Overview

This build system provides:

- **✓ Compilation** - Compile all embedded C source code
- **✓ Error Detection** - Parse and categorize compilation errors  
- **✓ Error Reporting** - Detailed JSON reports with code context
- **✓ Auto-Fix** - Use AI (Gemini/Ollama) to automatically fix errors
- **✓ Iterative Building** - Multiple fix attempts until success

## Quick Start

### Option 1: Windows Batch Script

```batch
build.bat                    # Full pipeline with auto-fix
build.bat --no-fix           # Only compile, don't fix
build.bat --max-iter 5       # More aggressive fixing (5 iterations)
```

### Option 2: Direct Python

```bash
python build.py              # Full pipeline
python build.py --help       # Show all options
```

### Option 3: Individual Tools

```bash
# Just compile and report errors
python compile_manager.py

# Fix existing compilation errors  
python error_fixer.py
```

## What Gets Compiled

The system automatically compiles all C files from:

```
SrcCodeProduct/
├── App/              (Application layer)
├── BootLoader/       (Bootloader)
├── ComStack/         (Communication stack)
├── Common/           (Standard types)
├── Config/           (Configuration)
├── Os/               (Operating system)
└── Rte/              (Runtime environment)
```

## Compilation Settings

**Compiler Flags:**
- `-Wall -Wextra` - All warnings enabled
- `-std=c99` - C99 standard
- `-fPIC` - Position-independent code
- `-I` - Include paths for all source directories

**Auto-Detected:**
- Compiler: GCC, Clang, or CC (whichever available)
- Platform-specific headers and settings

## Error Reporting

### Console Output

```
==============================================================
COMPILATION SUMMARY
==============================================================

❌ ERRORS (5):
  SrcCodeProduct/App/App_Main.c:42:5: error: implicit declaration of function 'init_module'
  SrcCodeProduct/Rte/Rte.c:18:10: error: conflicting types for 'Rte_Init'
  ...

⚠️  WARNINGS (3):
  SrcCodeProduct/Os/Os.c:100:12: warning: unused variable 'temp_val'
  ...
```

### Detailed Report

Errors are saved as JSON with full context:

```json
{
  "timestamp": "2026-05-09T10:15:30.123456",
  "total_errors": 5,
  "total_warnings": 3,
  "errors": [
    {
      "file": "SrcCodeProduct/App/App_Main.c",
      "line": 42,
      "column": 5,
      "error_type": "error",
      "message": "implicit declaration of function 'init_module'",
      "context": ">>> 42: init_module();"
    }
  ]
}
```

Reports are saved to: `Logs/compile_errors_YYYYMMDD_HHMMSS.json`

## Auto-Fix System

### How It Works

1. **Detect** - Identifies compilation errors
2. **Categorize** - Groups fixable vs. non-fixable errors
3. **Generate Prompt** - Creates detailed fix request for AI
4. **Get Fix** - Sends to Gemini or Ollama
5. **Apply** - Writes fixed code back to files
6. **Verify** - Recompiles to check if fixed
7. **Repeat** - Continues until all errors fixed or max iterations reached

### Supported Errors

The system can auto-fix:
- ✓ Undefined references
- ✓ Undeclared identifiers
- ✓ Missing function prototypes
- ✓ Incompatible pointer types
- ✓ Unused variables
- ✓ Syntax errors (in many cases)

### Prerequisites

**For Gemini (Recommended):**
```bash
# Install the package
pip install google-generativeai

# Set your API key in .env
GOOGLE_API_KEY=your_key_here
```

**For Ollama (Local):**
```bash
# Install and run Ollama
# https://ollama.ai

# Start Ollama with qwen2.5-coder model
ollama pull qwen2.5-coder:latest
ollama serve
```

## Configuration

### .env File

```env
# AI Provider (gemini or ollama)
DEV_AGENT_PROVIDER=gemini

# Gemini API Key (if using Gemini)
GOOGLE_API_KEY=your_api_key_here

# Ollama Model (if using Ollama)
OLLAMA_DEV_MODEL=qwen2.5-coder:latest
```

### Compiler Configuration

VS Code settings are already configured in `.vscode/c_cpp_properties.json`:

- **Windows**: Uses MinGW GCC
- **Linux/Mac**: Uses system GCC

## File Structure

```
workspace/
├── build.py                  # Main build script
├── build.bat                 # Windows batch launcher
├── compile_manager.py        # Compilation manager
├── error_fixer.py           # Error auto-fixer
├── build/                   # Build artifacts directory
└── Logs/                    # Error reports and logs
    ├── compile_errors_*.json
    └── *.txt
```

## Usage Examples

### Basic Compilation Check

```bash
python compile_manager.py
```

Output:
- Shows all found C files
- Reports compilation results
- Lists errors and warnings
- Suggests next steps

### Compile with Auto-Fix

```bash
python build.py
```

Output:
- Compiles code
- If errors found, automatically fixes them
- Recompiles to verify fixes
- Shows final status

### Manual Error Review

```bash
python compile_manager.py
# View Logs/compile_errors_*.json for details
```

### Advanced Options

```bash
# Disable auto-fix
python build.py --no-fix

# Use more iterations for aggressive fixing
python build.py --max-iter 5

# Show help
python build.py --help
```

## Troubleshooting

### No Compiler Found

**Error:** `No C compiler found`

**Fix:**
```bash
# Windows
choco install mingw-w64

# Ubuntu/Debian
sudo apt-get install build-essential

# macOS
brew install gcc
```

### AI Provider Not Available

**Error:** `No AI provider configured`

**Fix:**
- For Gemini: Set `GOOGLE_API_KEY` in `.env`
- For Ollama: Ensure Ollama is running on localhost:11434

### Files Not Found

**Error:** `Source root not found`

**Fix:** Ensure you're running from the project root directory:
```bash
cd c:\Working\AI-LEARNING\AI-Agent\AI_Learning\Ollama
python build.py
```

### Build Artifacts

Build output is saved to:
- **Compiled objects**: `build/check_iter*.o`
- **Error reports**: `Logs/compile_errors_*.json`

Clean up with:
```bash
rm -rf build/
rm -rf Logs/compile_errors_*.json
```

## Integration

### With VS Code

1. Create `.vscode/tasks.json`:

```json
{
  "version": "2.0.0",
  "tasks": [
    {
      "label": "Build Embedded C",
      "type": "shell",
      "command": "python",
      "args": ["build.py"],
      "problemMatcher": [],
      "group": {
        "kind": "build",
        "isDefault": true
      }
    }
  ]
}
```

2. Run with: `Ctrl+Shift+B` or `Cmd+Shift+B`

### CI/CD Pipeline

```bash
#!/bin/bash
python build.py --no-fix

if [ $? -eq 0 ]; then
    echo "Build successful"
    exit 0
else
    echo "Build failed"
    exit 1
fi
```

## Performance

- **Compilation**: ~5-10 seconds for full project
- **Error Fixing**: 30-60 seconds per iteration (depends on AI response time)
- **Total Build**: 1-5 minutes with auto-fix

## Limitations

- No linking (object files only) - prevents build artifacts
- GCC/Clang only (no MSVC support yet)
- Auto-fix works best for simple errors
- Requires internet for Gemini, or local Ollama running

## Future Enhancements

- [ ] Linking support
- [ ] MSVC compiler support
- [ ] Test integration
- [ ] Coverage reporting
- [ ] Performance profiling
- [ ] Custom compilation rules per module

## Documentation

- **Main README**: See workspace root
- **Error Reports**: Check `Logs/` directory
- **Source Code**: All code files are well-commented

## Support

For issues:

1. Check error report: `Logs/compile_errors_*.json`
2. Review source file context in report
3. Check AI provider configuration
4. Run with verbose output: `python build.py 2>&1 | tee build.log`

---

**Happy building!** 🎉
