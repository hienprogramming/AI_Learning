#!/usr/bin/env python3
"""
All-in-One Embedded C Build Pipeline
Compile → Detect Errors → Auto-Fix → Verify
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
from error_fixer import ErrorFixer


def print_banner(title: str):
    """Print formatted banner"""
    print("\n" + "="*70)
    print(f"  {title}")
    print("="*70)


def run_build_pipeline(auto_fix: bool = True, max_iterations: int = 3) -> int:
    """Run complete build pipeline"""
    
    print_banner("🚀 EMBEDDED C BUILD PIPELINE")
    
    # Step 1: Compile
    print_banner("STEP 1: COMPILATION")
    manager = CompileManager(link_mode=False)
    
    c_files = manager.get_all_c_files()
    print(f"\n📁 Found {len(c_files)} C source files")
    
    success, output = manager.compile_check()
    manager.print_summary()
    
    # Step 2: Check results
    print_banner("STEP 2: ERROR ANALYSIS")
    
    # Check if there are actual errors (not just based on gcc return code)
    has_errors = len(manager.errors) > 0
    
    if not has_errors:
        print("\n✅ Compilation successful! No errors found.\n")
        return 0
    
    print(f"\n❌ Compilation failed!")
    print(f"   - Errors: {len(manager.errors)}")
    print(f"   - Warnings: {len(manager.warnings)}")
    
    # Generate report
    report_file = manager.generate_error_report()
    print(f"\n📋 Detailed report saved to:")
    print(f"   {report_file}")
    
    # Step 3: Auto-fix
    if auto_fix and manager.errors:
        print_banner("STEP 3: AUTO-FIX ERRORS")
        
        fixer = ErrorFixer()
        
        if not fixer.ai_provider:
            print("\n⚠️  AI provider not available. Cannot auto-fix.")
            print("    - Set GOOGLE_API_KEY for Gemini")
            print("    - Or ensure Ollama is running")
            print(f"\n📁 Review error report and fix manually:")
            print(f"   {report_file}")
            return 1
        
        print(f"\n🤖 Using AI Provider: {fixer.ai_provider}")
        print(f"   Max iterations: {max_iterations}\n")
        
        fix_success = fixer.fix_compilation_errors(max_iterations=max_iterations)
        
        if fix_success:
            print_banner("✅ BUILD SUCCESSFUL")
            print("\n✓ All compilation errors have been fixed!")
            print(f"   Fixed {len(fixer.fixed_errors)} errors")
            print("\nYour embedded C code is now ready!\n")
            return 0
        else:
            print_banner("⚠️  BUILD INCOMPLETE")
            print("\n✗ Some errors could not be automatically fixed.")
            print(f"   Fixed: {len(fixer.fixed_errors)} errors")
            print(f"   Remaining: {len(fixer.compile_manager.errors)} errors")
            print(f"\n📁 Review error report:")
            print(f"   {report_file}")
            return 1
    
    return 1


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Embedded C Build Pipeline with Auto-Fix",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python build.py                    # Full pipeline with auto-fix
  python build.py --no-fix           # Only compile, don't fix
  python build.py --max-iter 5       # More aggressive fixing
        """
    )
    
    parser.add_argument(
        "--no-fix",
        action="store_true",
        help="Skip auto-fix step"
    )
    parser.add_argument(
        "--max-iter",
        type=int,
        default=3,
        help="Maximum auto-fix iterations (default: 3)"
    )
    
    args = parser.parse_args()
    
    try:
        return run_build_pipeline(
            auto_fix=not args.no_fix,
            max_iterations=args.max_iter
        )
    except KeyboardInterrupt:
        print("\n\n⚠️  Build cancelled by user")
        return 130
    except Exception as e:
        logger.error(f"Build failed with error: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())
