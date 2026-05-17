import os
import warnings
from pathlib import Path

warnings.filterwarnings(
    "ignore",
    message=".*google\\.generativeai.*",
    category=FutureWarning,
)

with warnings.catch_warnings():
    warnings.simplefilter("ignore", FutureWarning)
    import google.generativeai as genai
import ollama


def load_local_env() -> None:
    agent_dir = Path(__file__).resolve().parent
    candidate_files = [agent_dir / ".env", agent_dir.parent / ".env"]
    env_file = next((path for path in candidate_files if path.exists()), None)
    if env_file is None:
        return

    for line in env_file.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


load_local_env()

# Initialize Gemini client (uses GOOGLE_API_KEY from environment or .env)
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")
OLLAMA_FALLBACK_MODEL = os.getenv("OLLAMA_DEV_MODEL", "qwen2.5-coder:latest")
DEV_AGENT_PROVIDER = os.getenv("DEV_AGENT_PROVIDER", "gemini").lower()
_gemini_disabled_reason: str | None = None


def build_prompt(requirement: str) -> str:
    return f"""You are an embedded C developer. No malloc.

Requirement:
{requirement}"""


def run_with_gemini(requirement: str) -> str:
    model = genai.GenerativeModel(GEMINI_MODEL)
    response = model.generate_content(build_prompt(requirement))
    return response.text


def run_with_ollama(requirement: str) -> str:
    response = ollama.chat(
        model=OLLAMA_FALLBACK_MODEL,
        messages=[
            {"role": "system", "content": "You are an embedded C developer. No malloc."},
            {"role": "user", "content": requirement},
        ],
    )
    return response["message"]["content"]


def run(requirement: str) -> str:
    global _gemini_disabled_reason

    if DEV_AGENT_PROVIDER == "ollama":
        return run_with_ollama(requirement)

    if _gemini_disabled_reason:
        print(
            f"         [INFO] Using Ollama model {OLLAMA_FALLBACK_MODEL} "
            f"because Gemini is unavailable: {_gemini_disabled_reason}."
        )
        return run_with_ollama(requirement)

    try:
        return run_with_gemini(requirement)
    except Exception as exc:
        message = str(exc)
        quota_or_rate_limit = (
            "ResourceExhausted" in exc.__class__.__name__
            or "429" in message
            or "quota" in message.lower()
            or "rate limit" in message.lower()
        )
        if not quota_or_rate_limit:
            raise

        _gemini_disabled_reason = "quota/rate limit"
        print(
            f"         [WARNING] Gemini quota/rate limit hit. "
            f"Falling back to Ollama model {OLLAMA_FALLBACK_MODEL}."
        )
        return run_with_ollama(requirement)


def label() -> str:
    """Return a human-readable execution label for logs."""
    if DEV_AGENT_PROVIDER == "ollama":
        return f"dev_agent / Ollama:{OLLAMA_FALLBACK_MODEL}"

    return (
        f"dev_agent / Gemini:{GEMINI_MODEL} "
        f"(fallback Ollama:{OLLAMA_FALLBACK_MODEL})"
    )


def execute_module(project_context: str, module_info: dict, report=None) -> str:
    """Generate code for one module and own the dev-agent execution logs."""
    module_name = module_info["name"]

    print(f"\n[PHASE 1/3] CODE GENERATION", flush=True)
    print(f"  Agent:   {label()}", flush=True)
    print(f"  Status:  Running dev_agent...", flush=True)

    print(f"         [dev_agent] Loading module: {module_name}", flush=True)
    code = run(project_context + module_info["req"])
    print(f"         [dev_agent] Finished module: {module_name}", flush=True)

    if report is not None:
        report.log_code_generation(code)

    print(f"  Status:  Code generated successfully", flush=True)
    print(f"  Details: {code.count(chr(10))} lines, ~{len(code)} bytes", flush=True)
    return code
