"""
Embedded C Compilation Manager
Handles compilation of all SrcCodeProduct C files, error detection, and auto-fixing
"""

import os
import subprocess
import re
import sys
from pathlib import Path
from dataclasses import dataclass
from typing import List, Dict, Optional, Tuple
from datetime import datetime
import json
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@dataclass
class CompileError:
    """Represents a single compilation error"""
    file: str
    line: int
    column: int
    error_type: str  # 'error', 'warning'
    message: str
    context: str = ""
    
    def __str__(self):
        return f"{self.file}:{self.line}:{self.column}: {self.error_type}: {self.message}"
    
    def to_dict(self):
        return {
            "file": self.file,
            "line": self.line,
            "column": self.column,
            "error_type": self.error_type,
            "message": self.message,
            "context": self.context
        }


class CompileManager:
    """Manages compilation of embedded C code"""
    
    def __init__(self, workspace_root: str = None, link_mode: bool = True):
        if workspace_root is None:
            workspace_root = Path(__file__).parent
        self.workspace_root = Path(workspace_root)
        self.src_root = self.workspace_root / "SrcCodeProduct"
        self.build_dir = self.workspace_root / "build"
        self.log_dir = self.workspace_root / "Logs"
        self.linker_script = self.workspace_root / "STM32F103C8T6.ld"
        self.link_mode = link_mode
        self.object_files: List[Path] = []
        self.elf_file: Optional[Path] = None
        self.hex_file: Optional[Path] = None
        self.errors: List[CompileError] = []
        self.warnings: List[CompileError] = []
        
        # Create build directory
        self.build_dir.mkdir(exist_ok=True)
        self.log_dir.mkdir(exist_ok=True)
        
        # Compiler configuration
        self.compiler = self._find_compiler()
        self.linker = self.compiler  # Use same tool for linking
        self.compile_flags = [
            "-Wall",           # All warnings
            "-Wextra",         # Extra warnings
            "-std=c99",        # C99 standard
            "-g",              # Debug symbols
            "-Iinclude",       # Include directories
        ]
        self._add_include_paths()
    
    def _find_compiler(self) -> str:
        """Find available C compiler"""
        compilers = ["gcc", "clang", "cc"]
        for compiler in compilers:
            try:
                subprocess.run([compiler, "--version"], 
                             capture_output=True, 
                             timeout=5,
                             check=True)
                logger.info(f"Found compiler: {compiler}")
                return compiler
            except (subprocess.SubprocessError, FileNotFoundError):
                continue
        
        raise RuntimeError("No C compiler found. Please install GCC or Clang.")
    
    def _add_include_paths(self):
        """Add all relevant include paths"""
        include_dirs = [
            self.src_root / "Common",
            self.src_root / "Config",
            self.src_root / "Os",
            self.src_root / "Rte",
            self.src_root / "ComStack",
            self.src_root / "App",
            self.src_root / "BootLoader",
        ]
        
        for include_dir in include_dirs:
            if include_dir.exists():
                self.compile_flags.append(f"-I{include_dir}")
    
    def get_all_c_files(self) -> List[Path]:
        """Get all C source files from SrcCodeProduct"""
        if not self.src_root.exists():
            logger.error(f"Source root not found: {self.src_root}")
            return []
        
        c_files = list(self.src_root.rglob("*.c"))
        logger.info(f"Found {len(c_files)} C source files")
        return c_files
    
    def compile_check(self, output_file: str = "check.o") -> Tuple[bool, str]:
        """Compile all files and return status"""
        c_files = self.get_all_c_files()
        
        if not c_files:
            logger.error("No C files found to compile")
            return False, "No C files found"
        
        if self.link_mode:
            # Compile each file to object file
            logger.info(f"Compiling {len(c_files)} files to object files...")
            self.object_files = []
            
            for c_file in c_files:
                obj_file = self.build_dir / f"{c_file.stem}.o"
                cmd = [self.compiler] + self.compile_flags + [
                    "-o", str(obj_file),
                    "-c",
                    str(c_file)
                ]
                
                try:
                    result = subprocess.run(
                        cmd,
                        capture_output=True,
                        text=True,
                        timeout=30
                    )
                    
                    output = result.stdout + result.stderr
                    self.parse_errors(output, [c_file])
                    
                    if result.returncode == 0:
                        self.object_files.append(obj_file)
                        logger.debug(f"✓ {c_file.name}")
                    else:
                        logger.error(f"✗ {c_file.name}")
                
                except Exception as e:
                    logger.error(f"Failed to compile {c_file.name}: {e}")
            
            # Link object files to ELF
            if self.object_files and not self.errors:
                return self._link_elf()
            else:
                return False, "Compilation errors occurred"
        
        else:
            # Original compile-only mode
            output_path = self.build_dir / output_file
            cmd = [self.compiler] + self.compile_flags + [
                "-o", str(output_path),
                "-c",
                *[str(f) for f in c_files]
            ]
            
            logger.info(f"Compiling {len(c_files)} files...")
            logger.debug(f"Compile command: {' '.join(cmd)}")
            
            try:
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=60
                )
                
                output = result.stdout + result.stderr
                self.parse_errors(output, c_files)
                
                if result.returncode == 0:
                    logger.info("✓ Compilation check completed")
                else:
                    logger.debug("Compiler exited with non-zero code")
                return True, output
            
            except subprocess.TimeoutExpired:
                logger.error("Compilation timeout")
                return False, "Compilation timeout"
            except Exception as e:
                logger.error(f"Compilation error: {e}")
                return False, str(e)
    
    def _link_elf(self) -> Tuple[bool, str]:
        """Link object files to create ELF executable"""
        if not self.object_files:
            logger.error("No object files to link")
            return False, "No object files"
        
        self.elf_file = self.build_dir / "firmware.elf"
        
        # Check for linker script
        if not self.linker_script.exists():
            logger.warning(f"Linker script not found: {self.linker_script}")
            linker_args = []
        else:
            logger.info(f"Using linker script: {self.linker_script}")
            linker_args = ["-T", str(self.linker_script)]
        
        cmd = [self.compiler] + linker_args + [
            "-o", str(self.elf_file),
            *[str(obj) for obj in self.object_files]
        ]
        
        logger.info(f"Linking {len(self.object_files)} object files to {self.elf_file.name}...")
        logger.debug(f"Link command: {' '.join(cmd)}")
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=60
            )
            
            output = result.stdout + result.stderr
            self.parse_errors(output, [])
            
            if result.returncode == 0:
                logger.info("✓ Linking successful")
                
                # Generate HEX file
                self._generate_hex()
                
                # Print binary info
                self._print_elf_info()
                
                return True, output
            else:
                logger.error("✗ Linking failed")
                return False, output
        
        except subprocess.TimeoutExpired:
            logger.error("Linking timeout")
            return False, "Linking timeout"
        except Exception as e:
            logger.error(f"Linking error: {e}")
            return False, str(e)
    
    def _generate_hex(self):
        """Generate HEX file from ELF using objcopy"""
        if not self.elf_file or not self.elf_file.exists():
            logger.warning("ELF file not found for hex generation")
            return
        
        self.hex_file = self.elf_file.with_suffix('.hex')
        
        # Try to use objcopy
        objcopy_names = ["arm-none-eabi-objcopy", "objcopy"]
        objcopy = None
        
        for name in objcopy_names:
            try:
                subprocess.run([name, "--version"], 
                             capture_output=True, 
                             timeout=5,
                             check=True)
                objcopy = name
                break
            except:
                continue
        
        if not objcopy:
            logger.warning("objcopy not found - skipping HEX generation")
            return
        
        cmd = [objcopy, "-O", "ihex", str(self.elf_file), str(self.hex_file)]
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                logger.info(f"✓ Generated HEX file: {self.hex_file.name}")
            else:
                logger.warning(f"HEX generation failed: {result.stderr}")
        
        except Exception as e:
            logger.warning(f"HEX generation error: {e}")
    
    def _print_elf_info(self):
        """Print ELF file information"""
        if not self.elf_file or not self.elf_file.exists():
            return
        
        try:
            # Get file size
            file_size = self.elf_file.stat().st_size
            logger.info(f"ELF file size: {file_size} bytes ({file_size/1024:.2f} KB)")
            
            # Try to get detailed info with readelf/objdump
            for tool in ["arm-none-eabi-size", "size"]:
                try:
                    result = subprocess.run(
                        [tool, str(self.elf_file)],
                        capture_output=True,
                        text=True,
                        timeout=5
                    )
                    if result.returncode == 0:
                        logger.info(f"\nBinary size information:\n{result.stdout}")
                    break
                except:
                    continue
        
        except Exception as e:
            logger.debug(f"Could not get ELF info: {e}")
    
    def parse_errors(self, compiler_output: str, source_files: List[Path]):
        """Parse compiler output to extract errors and warnings"""
        self.errors.clear()
        self.warnings.clear()
        
        # GCC/Clang error pattern: file:line:column: error/warning: message
        pattern = r"([^:]+):(\d+):(\d+):\s*(error|warning):\s*(.+)"
        
        for match in re.finditer(pattern, compiler_output):
            file_path = match.group(1)
            line_num = int(match.group(2))
            col_num = int(match.group(3))
            error_type = match.group(4)
            message = match.group(5)
            
            error = CompileError(
                file=file_path,
                line=line_num,
                column=col_num,
                error_type=error_type,
                message=message
            )
            
            if error_type == "error":
                self.errors.append(error)
            else:
                self.warnings.append(error)
        
        logger.info(f"Found {len(self.errors)} errors, {len(self.warnings)} warnings")
    
    def is_compilation_success(self) -> bool:
        """Check if compilation was successful"""
        return len(self.errors) == 0
    
    def get_error_context(self, error: CompileError) -> str:
        """Get source code context around the error"""
        try:
            with open(error.file, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()
                start_line = max(0, error.line - 3)
                end_line = min(len(lines), error.line + 2)
                
                context = []
                for i in range(start_line, end_line):
                    line_num = i + 1
                    prefix = ">>> " if line_num == error.line else "    "
                    context.append(f"{prefix}{line_num:4d}: {lines[i].rstrip()}")
                
                return "\n".join(context)
        except Exception as e:
            logger.warning(f"Could not read file {error.file}: {e}")
            return ""
    
    def generate_error_report(self, filename: str = None) -> str:
        """Generate detailed error report"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"compile_errors_{timestamp}.json"
        
        report_path = self.log_dir / filename
        
        errors_data = []
        for error in self.errors:
            error_dict = error.to_dict()
            error_dict["context"] = self.get_error_context(error)
            errors_data.append(error_dict)
        
        warnings_data = [w.to_dict() for w in self.warnings]
        
        report = {
            "timestamp": datetime.now().isoformat(),
            "total_errors": len(self.errors),
            "total_warnings": len(self.warnings),
            "errors": errors_data,
            "warnings": warnings_data
        }
        
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)
        
        logger.info(f"Error report saved to {report_path}")
        return str(report_path)
    
    def print_summary(self):
        """Print compilation summary"""
        print("\n" + "="*60)
        if self.link_mode:
            print("LINK & BUILD SUMMARY")
        else:
            print("COMPILATION SUMMARY")
        print("="*60)
        
        if not self.errors and not self.warnings:
            print("✓ No errors or warnings!")
            if self.link_mode and self.elf_file and self.elf_file.exists():
                print(f"✓ ELF file: {self.elf_file.name}")
                if self.hex_file and self.hex_file.exists():
                    print(f"✓ HEX file: {self.hex_file.name}")
        else:
            if self.errors:
                print(f"\n❌ ERRORS ({len(self.errors)}):")
                for error in self.errors[:10]:  # Show first 10
                    print(f"  {error}")
                if len(self.errors) > 10:
                    print(f"  ... and {len(self.errors) - 10} more")
            
            if self.warnings:
                print(f"\n⚠️  WARNINGS ({len(self.warnings)}):")
                for warning in self.warnings[:5]:  # Show first 5
                    print(f"  {warning}")
                if len(self.warnings) > 5:
                    print(f"  ... and {len(self.warnings) - 5} more")
        
        print("\n" + "="*60)
    
    def get_fixable_errors(self) -> List[CompileError]:
        """Filter errors that can be auto-fixed"""
        fixable_patterns = [
            "undefined reference",
            "undeclared identifier",
            "missing function prototype",
            "incompatible pointer",
            "unused variable",
        ]
        
        fixable = []
        for error in self.errors:
            for pattern in fixable_patterns:
                if pattern.lower() in error.message.lower():
                    fixable.append(error)
                    break
        
        return fixable


def main():
    """Main execution"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Embedded C Compilation Manager",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python compile_manager.py          # Compile-only (default)
  python compile_manager.py --link   # Full build with linking
        """
    )
    parser.add_argument("--link", action="store_true",
                       help="Link object files to create ELF executable")
    args = parser.parse_args()
    
    link_mode = args.link
    manager = CompileManager(link_mode=link_mode)
    
    print("\n" + "="*60)
    if link_mode:
        print("EMBEDDED C BUILD SYSTEM (WITH LINKING)")
    else:
        print("EMBEDDED C COMPILATION MANAGER (COMPILE-ONLY)")
    print("="*60)
    
    # Get all C files
    c_files = manager.get_all_c_files()
    print(f"\n📁 Found {len(c_files)} C source files:")
    for f in c_files:
        print(f"   - {f.relative_to(manager.workspace_root)}")
    
    # Compile
    print(f"\n🔨 Building {'(with linking)' if link_mode else '(compile-only)'}...")
    success, output = manager.compile_check()
    
    # Print summary
    manager.print_summary()
    
    # Generate report if there are errors
    if manager.errors:
        report_file = manager.generate_error_report()
        print(f"\n📋 Detailed report: {report_file}")
        
        fixable_errors = manager.get_fixable_errors()
        if fixable_errors:
            print(f"\n🔧 {len(fixable_errors)} fixable errors detected!")
            print("   Use 'python error_fixer.py' to auto-fix")
        
        return 1
    
    if link_mode and manager.elf_file:
        print(f"\n✅ Build successful!")
        print(f"   ELF: {manager.elf_file}")
        if manager.hex_file and manager.hex_file.exists():
            print(f"   HEX: {manager.hex_file}")
    else:
        print("\n✓ Compilation successful!")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
