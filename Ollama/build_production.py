#!/usr/bin/env python3
"""
Production Embedded C Build with Full Linking
Compile → Link → Generate ELF/HEX → Verify
"""

import sys
import argparse
import logging
from pathlib import Path

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

from compile_manager import CompileManager


def print_banner(title: str):
    """Print formatted banner"""
    print("\n" + "="*70)
    print(f"  {title}")
    print("="*70)


def run_production_build(auto_fix: bool = False) -> int:
    """Run production build with full linking"""
    
    print_banner("🏭 PRODUCTION EMBEDDED C BUILD (WITH LINKING)")
    
    # Step 1: Compile and Link
    print_banner("STEP 1: COMPILATION & LINKING")
    manager = CompileManager(link_mode=True)
    
    c_files = manager.get_all_c_files()
    print(f"\n📁 Found {len(c_files)} C source files")
    
    success, output = manager.compile_check()
    manager.print_summary()
    
    # Check if there are actual errors
    has_errors = len(manager.errors) > 0
    
    if not has_errors:
        print("\n✅ BUILD SUCCESSFUL!")
        if manager.elf_file and manager.elf_file.exists():
            print(f"   ELF file: {manager.elf_file}")
            print(f"   Size: {manager.elf_file.stat().st_size} bytes")
        if manager.hex_file and manager.hex_file.exists():
            print(f"   HEX file: {manager.hex_file}")
            print(f"   Ready to flash!")
        print()
        return 0
    
    print("\n❌ BUILD FAILED - Linker Errors Detected")
    print(f"   Errors: {len(manager.errors)}")
    print(f"   Warnings: {len(manager.warnings)}")
    
    # Generate report
    report_file = manager.generate_error_report("production_build_errors.json")
    print(f"\n📋 Error report: {report_file}")
    
    print("\n" + "="*70)
    print("⚠️  FIX REQUIRED")
    print("="*70)
    print("\nLinker errors indicate:")
    print("  - Missing implementations in stub functions")
    print("  - Undefined external symbols")
    print("  - Memory layout conflicts")
    print("\nNext steps:")
    print("  1. Review error report")
    print("  2. Fix undefined symbols")
    print("  3. Ensure all functions have implementations")
    print("  4. Run again: python build_production.py\n")
    
    return 1


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Production Build with Full Linking",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Production build creates:
  - firmware.elf   (full executable with debug symbols)
  - firmware.hex   (Intel HEX format for flashing)

This mode performs full linking and will report:
  - Linker errors (undefined symbols, memory conflicts)
  - Full symbol resolution checking
  - Binary size information

Use for:
  - Final production builds
  - Flashing to hardware
  - Binary analysis
        """
    )
    
    args = parser.parse_args()
    
    try:
        return run_production_build()
    except KeyboardInterrupt:
        print("\n\n⚠️  Build cancelled by user")
        return 130
    except Exception as e:
        logger.error(f"Build failed with error: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())
