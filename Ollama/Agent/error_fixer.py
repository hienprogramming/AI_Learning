"""
Automatic C Compilation Error Fixer
Uses AI agents (Gemini/Ollama) to fix compilation errors
"""

import json
import sys
import logging
from pathlib import Path
from typing import List, Optional
import warnings

warnings.filterwarnings("ignore", category=FutureWarning)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

from compile_manager import CompileManager, CompileError

try:
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", FutureWarning)
        import google.generativeai as genai
except ImportError:
    genai = None

try:
    import ollama
except ImportError:
    ollama = None


class ErrorFixer:
    """Fix compilation errors using AI"""
    
    def __init__(self, workspace_root: str = None):
        self.workspace_root = Path(workspace_root) if workspace_root else Path(__file__).parent
        self.compile_manager = CompileManager(workspace_root, link_mode=False)
        self.fixed_errors = []
        self.ai_provider = self._detect_ai_provider()
        self._init_ai()
    
    def _detect_ai_provider(self) -> str:
        """Detect available AI provider"""
        import os
        env_file = self.workspace_root / ".env"
        env_provider = "gemini"
        
        if env_file.exists():
            for line in env_file.read_text().splitlines():
                if line.startswith("DEV_AGENT_PROVIDER="):
                    env_provider = line.split("=")[1].strip().lower()
        
        # Check availability
        if env_provider == "gemini" and os.getenv("GOOGLE_API_KEY"):
            return "gemini"
        elif ollama:
            return "ollama"
        else:
            logger.warning("No AI provider configured. Install google-generativeai or ensure Ollama is running.")
            return None
    
    def _init_ai(self):
        """Initialize AI client"""
        if self.ai_provider == "gemini" and genai:
            import os
            api_key = os.getenv("GOOGLE_API_KEY")
            if api_key:
                genai.configure(api_key=api_key)
                self.gemini_model = genai.GenerativeModel("gemini-2.0-flash")
        elif self.ai_provider == "ollama" and ollama:
            self.ollama_model = "qwen2.5-coder:latest"
    
    def get_fix_prompt(self, error: CompileError, file_content: str) -> str:
        """Generate prompt for AI to fix error"""
        context = self.compile_manager.get_error_context(error)
        
        prompt = f"""You are an embedded C developer. Fix the following compilation error.

## Compilation Error
{error}

## Error Context (source code)
```c
{context}
```

## Full Source File
```c
{file_content}
```

## Task
Provide ONLY the corrected C code that fixes this error. 
- Do NOT include explanations
- Do NOT include markdown formatting
- Do NOT include code blocks or backticks
- Start directly with the corrected code
- Keep the code style consistent with the original
- No malloc - use stack allocation only

Return the complete corrected source file:"""
        
        return prompt
    
    def fix_error_with_gemini(self, error: CompileError) -> Optional[str]:
        """Fix error using Gemini"""
        if not genai:
            logger.error("google-generativeai not installed")
            return None
        
        try:
            file_path = Path(error.file)
            if not file_path.exists():
                logger.error(f"File not found: {error.file}")
                return None
            
            file_content = file_path.read_text(encoding='utf-8', errors='ignore')
            prompt = self.get_fix_prompt(error, file_content)
            
            logger.info(f"Sending to Gemini: {error.file}:{error.line}")
            response = self.gemini_model.generate_content(prompt, safety_settings={})
            
            fixed_code = response.text.strip()
            
            # Clean up if wrapped in code blocks
            if fixed_code.startswith("```"):
                fixed_code = "\n".join(fixed_code.split("\n")[1:-1])
            
            return fixed_code
        
        except Exception as e:
            logger.error(f"Gemini fix failed: {e}")
            return None
    
    def fix_error_with_ollama(self, error: CompileError) -> Optional[str]:
        """Fix error using Ollama"""
        if not ollama:
            logger.error("ollama not installed or not running")
            return None
        
        try:
            file_path = Path(error.file)
            if not file_path.exists():
                logger.error(f"File not found: {error.file}")
                return None
            
            file_content = file_path.read_text(encoding='utf-8', errors='ignore')
            prompt = self.get_fix_prompt(error, file_content)
            
            logger.info(f"Sending to Ollama: {error.file}:{error.line}")
            response = ollama.generate(
                model=self.ollama_model,
                prompt=prompt,
                stream=False
            )
            
            fixed_code = response["response"].strip()
            
            if fixed_code.startswith("```"):
                fixed_code = "\n".join(fixed_code.split("\n")[1:-1])
            
            return fixed_code
        
        except Exception as e:
            logger.error(f"Ollama fix failed: {e}")
            return None
    
    def apply_fix(self, error: CompileError, fixed_code: str) -> bool:
        """Apply fix to file"""
        try:
            file_path = Path(error.file)
            
            # Backup original
            backup_path = file_path.with_suffix(file_path.suffix + '.bak')
            file_path.write_text(file_path.read_text(encoding='utf-8', errors='ignore'), 
                                encoding='utf-8')
            
            # Write fixed code
            file_path.write_text(fixed_code, encoding='utf-8')
            logger.info(f"✓ Fixed: {error.file}:{error.line}")
            self.fixed_errors.append(error)
            return True
        
        except Exception as e:
            logger.error(f"Failed to apply fix: {e}")
            return False
    
    def fix_compilation_errors(self, max_iterations: int = 3) -> bool:
        """Iteratively fix compilation errors"""
        if not self.ai_provider:
            logger.error("No AI provider available")
            return False
        
        iteration = 0
        while iteration < max_iterations:
            iteration += 1
            logger.info(f"\n{'='*60}")
            logger.info(f"Iteration {iteration}/{max_iterations}")
            logger.info(f"{'='*60}")
            
            # Compile
            success, output = self.compile_manager.compile_check(f"check_iter{iteration}.o")
            
            if success:
                logger.info("✓ All compilation errors fixed!")
                return True
            
            # Get errors
            errors = self.compile_manager.errors
            if not errors:
                logger.info("✓ No compilation errors")
                return True
            
            logger.info(f"Found {len(errors)} errors to fix")
            
            # Fix errors (limit to 3 per iteration)
            fixed_count = 0
            for error in errors[:3]:
                logger.info(f"\nFixing: {error}")
                
                fixed_code = None
                if self.ai_provider == "gemini":
                    fixed_code = self.fix_error_with_gemini(error)
                elif self.ai_provider == "ollama":
                    fixed_code = self.fix_error_with_ollama(error)
                
                if fixed_code:
                    if self.apply_fix(error, fixed_code):
                        fixed_count += 1
            
            if fixed_count == 0:
                logger.error("Could not fix any errors. Manual intervention needed.")
                return False
        
        logger.warning(f"Max iterations ({max_iterations}) reached. Some errors may remain.")
        return False


def main():
    """Main execution"""
    print("\n" + "="*60)
    print("COMPILATION ERROR AUTO-FIXER")
    print("="*60)
    
    fixer = ErrorFixer()
    
    if not fixer.ai_provider:
        print("\n❌ Error: No AI provider configured")
        print("   - Set GOOGLE_API_KEY for Gemini")
        print("   - Or ensure Ollama is running")
        return 1
    
    print(f"\n🤖 Using AI Provider: {fixer.ai_provider}")
    
    # Try to fix errors
    success = fixer.fix_compilation_errors(max_iterations=3)
    
    print("\n" + "="*60)
    if success:
        print("✓ All errors fixed successfully!")
        print("="*60)
        return 0
    else:
        print("✗ Some errors remain. Manual review needed.")
        print("="*60)
        return 1


if __name__ == "__main__":
    sys.exit(main())
