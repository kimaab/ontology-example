import os
from pathlib import Path

from langchain_openai import ChatOpenAI

ENV_FILE = Path(__file__).resolve().parents[2] / ".env"     # 프로젝트 폴더의 .env


def load_env(path=ENV_FILE):
    """간단한 .env 로더 (이미 설정된 환경변수가 우선)"""
    if not path.exists():
        return
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


def make_llm():
    load_env()
    thinking = os.environ.get("LLM_THINKING", "false").strip().lower()
    extra_body = {"chat_template_kwargs": {"enable_thinking": thinking == "true"}}
    return ChatOpenAI(
        base_url=os.environ["LLM_BASE_URL"].rstrip("/"),
        api_key=os.environ.get("LLM_API_KEY") or "EMPTY",
        model=os.environ.get("LLM_MODEL") or "default",
        max_tokens=int(os.environ.get("LLM_MAX_TOKENS", "16384")),
        temperature=0,
        extra_body=extra_body,
    )