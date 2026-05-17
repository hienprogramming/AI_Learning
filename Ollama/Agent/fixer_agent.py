import ollama
import json

MODEL = "qwen2.5-coder"

def run(code: str, feedback: str) -> str:
    return ollama.chat(
        model=MODEL,
        messages=[
            {
                "role": "system",
                "content": (
                    "You are an embedded C fixer. Fix only the issues listed by the tester. "
                    "Preserve the requested module behavior, use static allocation only, "
                    "define or include missing symbols, add bounds/null checks, and return "
                    "only the corrected C/header code blocks with filenames when possible."
                ),
            },
            {"role": "user", "content": f"CODE:\n{code}\n\nTESTER ISSUES:\n{feedback}"},
        ]
    )["message"]["content"]


def label() -> str:
    """Return a human-readable execution label for logs."""
    return f"fixer_agent / Ollama:{MODEL}"


def format_feedback(feedback) -> str:
    """Build a compact, actionable issue list for fixer_agent."""
    if not isinstance(feedback, dict):
        return str(feedback)

    lines = []
    static_checks = feedback.get("static_checks", [])
    if static_checks:
        lines.append("Deterministic static findings:")
        for finding in static_checks:
            location = f" line {finding['line']}" if finding.get("line") else ""
            lines.append(
                f"- [{finding.get('severity', 'INFO')}] {finding.get('check', 'check')}{location}: "
                f"{finding.get('message', '')}"
            )
            if finding.get("fix_hint"):
                lines.append(f"  Fix hint: {finding['fix_hint']}")

    llm_review = feedback.get("llm_review", {})
    if isinstance(llm_review, dict):
        failed_items = []
        for category, result in llm_review.items():
            if category == "summary" or not isinstance(result, dict):
                continue
            for failed in result.get("failed", []):
                failed_items.append(f"- {category}: {failed}")
        if failed_items:
            lines.append("LLM checklist failures:")
            lines.extend(failed_items)

    if feedback.get("error"):
        lines.append(f"Tester response issue: {feedback['error']}")
        if feedback.get("raw"):
            lines.append(f"Raw tester response: {feedback['raw'][:1000]}")

    return "\n".join(lines) if lines else json.dumps(feedback, indent=2, ensure_ascii=False)


def execute_module(code: str, feedback, module_info: dict, report=None) -> str:
    """Fix generated code and own the fixer-agent execution logs."""
    module_name = module_info["name"]
    issue_count = len(getattr(report, "errors_found", []))

    if issue_count == 0:
        print(f"\n[PHASE 3/3] No fixes needed - code quality is good", flush=True)
        return code

    print(f"\n[PHASE 3/3] FIXING & IMPROVEMENT", flush=True)
    print(f"  Agent:   {label()}", flush=True)
    print(f"  Purpose: Fix issues and improve code quality", flush=True)
    print(f"  Issues:  Fixing {issue_count} detected problem(s)", flush=True)
    print(f"  Status:  Running fixer_agent...", flush=True)

    print(f"         [fixer_agent] Loading module: {module_name}", flush=True)
    fix_input = format_feedback(feedback)
    print(f"  Fix log: Passing actionable issue list to fixer_agent", flush=True)
    for line in fix_input.splitlines()[:8]:
        print(f"           {line[:100]}", flush=True)
    if len(fix_input.splitlines()) > 8:
        print(f"           ...", flush=True)

    fixed = run(code, fix_input)
    print(f"         [fixer_agent] Finished module: {module_name}", flush=True)

    fix_description = f"Fixed {issue_count} issue(s) from tester feedback"
    if report is not None:
        report.log_fix_applied(fixed, fix_description)

    print(f"  Status:  Fixes applied successfully", flush=True)
    print(f"  Details: {fix_description}", flush=True)
    return fixed
