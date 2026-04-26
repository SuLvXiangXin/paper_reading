from __future__ import annotations

import os
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parents[1]
KB_DIR = BASE_DIR / "knowledge_base"
WEB_DIR = BASE_DIR / "web"
WEB_DIST_DIR = WEB_DIR / "dist"
STATE_DIR = BASE_DIR / ".paper_reader_web"
STATE_DB = STATE_DIR / "state.sqlite"
ARTIFACTS_DIR = STATE_DIR / "artifacts"
JOB_LOG_DIR = BASE_DIR / "logs" / "web_jobs"

DEFAULT_HOST = os.environ.get("PAPER_READER_WEB_HOST", "127.0.0.1")
DEFAULT_PORT = int(os.environ.get("PAPER_READER_WEB_PORT", "7860"))
DEFAULT_DOMAIN = os.environ.get("PAPER_READER_DOMAIN", "vla")
CONDA_ENV = os.environ.get("PAPER_READER_CONDA_ENV", "paper_reader")
CODEX_MODEL = os.environ.get("PAPER_READER_CODEX_MODEL", "")

MAX_CONTEXT_CHARS = int(os.environ.get("PAPER_READER_WEB_CONTEXT_CHARS", "36000"))
CODEX_TIMEOUT_SECONDS = int(os.environ.get("PAPER_READER_CODEX_TIMEOUT_SECONDS", "240"))
