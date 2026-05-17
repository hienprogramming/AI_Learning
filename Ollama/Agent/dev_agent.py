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
    env_file = Path(__file__).resolve().parent / ".env"
    if not env_file.exists():
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
