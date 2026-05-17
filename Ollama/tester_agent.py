import json
import re
from pathlib import Path

MODEL = "llama3"
SOURCE_ROOT = Path("SrcCodeProduct")

TESTING_CHECKLIST = {
    "autosar_compliance": {
        "title": "AUTOSAR Compliance",
        "items": [
            "Naming conventions follow AUTOSAR style",
            "Function/variable names use the correct module prefix",
            "Return types follow AUTOSAR/project conventions",
        ],
    },
    "embedded_c": {
        "title": "Embedded C Best Practices",
        "items": [
            "No malloc/dynamic memory allocation",
            "All variables are initialized before use",
            "No undefined behavior",
            "No buffer overflow risks",
            "Static/local scope is used appropriately",
        ],
    },
    "code_correctness": {
        "title": "Code Correctness",
        "items": [
            "Code matches the requirement",
            "Logic handles edge cases",
            "Constants and limits are respected",
            "No dead code or unreachable statements",
        ],
    },
    "type_safety": {
        "title": "Type Safety",
        "items": [
            "Project typedefs are used correctly",
            "No inappropriate type casting",
            "Enums and defines are declared before use",
            "Data sizes match values and buffer lengths",
        ],
    },
    "code_structure": {
        "title": "Code Structure",
        "items": [
            "Header guards are present in .h files",
            "Declarations and implementations are separated",
            "Include dependencies are correct and minimal",
            "No circular includes",
        ],
    },
    "unit_testability": {
        "title": "Unit Test Compatibility",
        "items": [
            "Functions are testable in isolation",
            "Functions have single responsibility",
            "No hardcoded dependencies that prevent mocking",
            "Error handling and edge cases are testable",
            "Return values indicate success/failure clearly",
        ],
    },
}


def _strip_comments_and_strings(code: str) -> str:
    code = re.sub(r"/\*.*?\*/", " ", code, flags=re.DOTALL)
    code = re.sub(r"//.*", " ", code)
    code = re.sub(r'"(?:\\.|[^"\\])*"', '""', code)
    code = re.sub(r"'(?:\\.|[^'\\])*'", "''", code)
    return code


def _workspace_defined_symbols() -> set[str]:
    symbols = {"NULL", "TRUE", "FALSE", "E_OK", "E_NOT_OK"}
    if not SOURCE_ROOT.exists():
        return symbols

    for path in SOURCE_ROOT.rglob("*.[ch]"):
        text = path.read_text(encoding="utf-8", errors="replace")
        symbols.update(re.findall(r"^\s*#\s*define\s+([A-Za-z_][A-Za-z0-9_]*)\b", text, re.MULTILINE))
        symbols.update(re.findall(r"\btypedef\s+(?:struct\s+|enum\s+)?[^{;]*?\b([A-Za-z_][A-Za-z0-9_]*)\s*;", text))
        symbols.update(re.findall(r"}\s*([A-Za-z_][A-Za-z0-9_]*)\s*;", text))
    return symbols


def run_static_checks(code: str) -> list[dict]:
    """Run deterministic checks before the LLM review."""
    findings = []
    clean_code = _strip_comments_and_strings(code)
    defined_symbols = _workspace_defined_symbols()
    defined_symbols.update(re.findall(r"^\s*#\s*define\s+([A-Za-z_][A-Za-z0-9_]*)\b", code, re.MULTILINE))
    defined_symbols.update(re.findall(r"\btypedef\s+(?:struct\s+|enum\s+)?[^{;]*?\b([A-Za-z_][A-Za-z0-9_]*)\s*;", code))
    defined_symbols.update(re.findall(r"}\s*([A-Za-z_][A-Za-z0-9_]*)\s*;", code))

    ignored_tokens = {"NULL", "UINT8_MAX", "UINT16_MAX", "UINT32_MAX", "STD_ON", "STD_OFF"}
    uppercase_tokens = sorted(set(re.findall(r"\b[A-Z][A-Z0-9_]{2,}\b", clean_code)))
    for token in uppercase_tokens:
        if token not in defined_symbols and token not in ignored_tokens:
            findings.append(
                {
                    "severity": "ERROR",
                    "check": "undefined_symbol",
                    "message": (
                        f"Symbol {token} is used but no #define/typedef was found "
                        "in generated code or SrcCodeProduct headers."
                    ),
                    "fix_hint": (
                        f"Define {token} in the module header/config header, include the "
                        "header that defines it, or replace it with an existing project constant."
                    ),
                }
            )

    known_types = {
        "bool",
        "char",
        "float",
        "double",
        "int",
        "long",
        "short",
        "signed",
        "unsigned",
        "void",
        "size_t",
        "uint8_t",
        "uint16_t",
        "uint32_t",
        "uint64_t",
        "int8_t",
        "int16_t",
        "int32_t",
        "int64_t",
    }
    type_like_tokens = sorted(set(re.findall(r"\b[A-Za-z_][A-Za-z0-9_]*(?:Type|_t)\b", clean_code)))
    for token in type_like_tokens:
        if token not in defined_symbols and token not in known_types:
            findings.append(
                {
                    "severity": "ERROR",
                    "check": "undefined_type",
                    "message": (
                        f"Type {token} is used but no typedef was found in generated code "
                        "or SrcCodeProduct headers."
                    ),
                    "fix_hint": (
                        f"Use an existing project type, add the missing typedef for {token}, "
                        "or include the header that declares it."
                    ),
                }
            )

    placeholder_patterns = ["Define your", "Add more types as needed", "placeholder", "TODO", "FIXME", "Implement "]
    for line_no, line in enumerate(code.splitlines(), 1):
        if any(pattern.lower() in line.lower() for pattern in placeholder_patterns):
            findings.append(
                {
                    "severity": "WARNING",
                    "check": "placeholder_code",
                    "line": line_no,
                    "message": f"Placeholder/incomplete implementation text remains: {line.strip()}",
                    "fix_hint": "Replace placeholder text with concrete project constants or real implementation.",
                }
            )

    if re.search(r"\b(malloc|calloc|realloc|free)\s*\(", clean_code):
        findings.append(
            {
                "severity": "ERROR",
                "check": "dynamic_memory",
                "message": "Dynamic memory API is used, but the project requires static allocation only.",
                "fix_hint": "Use fixed-size static buffers with explicit bounds checks.",
            }
        )

    return findings


def build_test_prompt(code: str, static_findings: list[dict]) -> str:
    checklist_text = "TESTING CHECKLIST:\n"
    for data in TESTING_CHECKLIST.values():
        checklist_text += f"\n{data['title']}:\n"
        for item in data["items"]:
            checklist_text += f"  - {item}\n"

    return f"""{checklist_text}

DETERMINISTIC STATIC FINDINGS TO VERIFY:
{json.dumps(static_findings, indent=2, ensure_ascii=False)}

CODE TO TEST:
```c
{code}
```

Review the code against every checklist item. Return ONLY valid JSON:
{{
  "category_name": {{
    "passed": ["item - reason"],
    "failed": ["item - reason"],
    "score": "X/Y"
  }},
  "summary": {{
    "total_checks": N,
    "passed": X,
    "failed": Y,
    "pass_rate": "X%"
  }}
}}"""


def run(code: str) -> dict:
    """Test code with static checks plus LLM checklist review."""
    import ollama

    static_findings = run_static_checks(code)
    prompt = build_test_prompt(code, static_findings)

    response = ollama.chat(
        model=MODEL,
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a strict embedded C code tester. Evaluate code against "
                    "the checklist and deterministic findings. Return ONLY valid JSON."
                ),
            },
            {"role": "user", "content": prompt},
        ],
    )["message"]["content"]

    try:
        json_start = response.find("{")
        json_end = response.rfind("}") + 1
        if json_start != -1 and json_end > json_start:
            return {
                "static_checks": static_findings,
                "llm_review": json.loads(response[json_start:json_end]),
                "summary": {
                    "static_issue_count": len(static_findings),
                    "llm_review_available": True,
                },
            }
    except json.JSONDecodeError:
        pass

    return {
        "static_checks": static_findings,
        "error": "Failed to parse JSON response",
        "raw": response,
        "summary": {
            "static_issue_count": len(static_findings),
            "llm_review_available": False,
        },
    }


def label() -> str:
    """Return a human-readable execution label for logs."""
    return f"tester_agent / Ollama:{MODEL}"


def execute_module(code: str, module_info: dict, report=None) -> dict:
    """Validate generated code and own the tester-agent execution logs."""
    module_name = module_info["name"]

    print(f"\n[PHASE 2/3] TESTING & VALIDATION", flush=True)
    print(f"  Agent:   {label()}", flush=True)
    print(f"  Purpose: Validate code quality, syntax, symbols, and functionality", flush=True)
    print(f"  Checks:  deterministic static checks + LLM checklist review", flush=True)
    print(f"           - undefined #define/typedef-like symbols", flush=True)
    print(f"           - placeholder/TODO text", flush=True)
    print(f"           - dynamic memory usage", flush=True)
    print(f"           - AUTOSAR/embedded C checklist", flush=True)
    print(f"  Status:  Running tester_agent...", flush=True)

    print(f"         [tester_agent] Loading module: {module_name}", flush=True)
    feedback = run(code)
    print(f"         [tester_agent] Finished module: {module_name}", flush=True)

    if report is not None:
        report.log_test_feedback(feedback)

    if isinstance(feedback, dict):
        summary = feedback.get("summary", {})
        print(
            f"  Static:  {summary.get('static_issue_count', 0)} deterministic issue(s)",
            flush=True,
        )
        print(
            f"  LLM:     review {'available' if summary.get('llm_review_available') else 'unavailable/parse failed'}",
            flush=True,
        )

    errors_found = getattr(report, "errors_found", [])
    if errors_found:
        print(f"  Status:  Issues detected - {len(errors_found)} problem(s) found", flush=True)
        print(f"\n  [ISSUES DETECTED]", flush=True)
        for i, error in enumerate(errors_found[:5], 1):
            severity = error["severity"]
            content = error["content"][:70]
            print(f"    {i}. [{severity:8s}] {content}", flush=True)
        if len(errors_found) > 5:
            print(f"    ... and {len(errors_found) - 5} more issues", flush=True)
    else:
        print(f"  Status:  All tests passed", flush=True)
        print(f"  Details: No issues detected", flush=True)

    return feedback
