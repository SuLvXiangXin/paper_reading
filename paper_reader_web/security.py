from __future__ import annotations

from pathlib import Path

from fastapi import HTTPException

from .config import KB_DIR


def ensure_state_dirs() -> None:
    from .config import ARTIFACTS_DIR, JOB_LOG_DIR, STATE_DIR

    STATE_DIR.mkdir(parents=True, exist_ok=True)
    ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)
    JOB_LOG_DIR.mkdir(parents=True, exist_ok=True)


def available_domains() -> list[str]:
    if not KB_DIR.exists():
        return []
    domains = []
    for item in sorted(KB_DIR.iterdir()):
        if item.is_dir() and (item / "index.md").exists():
            domains.append(item.name)
    return domains


def validate_domain(domain: str | None) -> str:
    domains = available_domains()
    if not domain:
        if domains:
            return domains[0]
        raise HTTPException(status_code=404, detail="No knowledge domains found")
    if domain not in domains:
        raise HTTPException(status_code=404, detail=f"Unknown domain: {domain}")
    return domain


def normalize_kb_path(path: str) -> str:
    if not path:
        raise HTTPException(status_code=400, detail="Missing path")
    raw = path.strip().replace("\\", "/")
    if raw.startswith("knowledge_base/"):
        raw = raw[len("knowledge_base/") :]
    if raw.startswith("/") or raw.startswith("../") or "/../" in raw or raw == "..":
        raise HTTPException(status_code=403, detail="Path traversal is not allowed")
    normalized = Path(raw)
    if normalized.is_absolute() or any(part in {"..", ""} for part in normalized.parts):
        raise HTTPException(status_code=403, detail="Path traversal is not allowed")
    if normalized.suffix and normalized.suffix != ".md":
        raise HTTPException(status_code=400, detail="Only Markdown files can be read")
    if len(normalized.parts) < 2:
        raise HTTPException(status_code=400, detail="Path must include domain and file")
    validate_domain(normalized.parts[0])
    return normalized.as_posix()


def resolve_kb_file(path: str, *, must_exist: bool = True) -> Path:
    normalized = normalize_kb_path(path)
    target = (KB_DIR / normalized).resolve()
    kb_root = KB_DIR.resolve()
    if target != kb_root and kb_root not in target.parents:
        raise HTTPException(status_code=403, detail="Path is outside knowledge_base")
    if must_exist and not target.exists():
        raise HTTPException(status_code=404, detail=f"Document not found: {normalized}")
    if must_exist and not target.is_file():
        raise HTTPException(status_code=404, detail=f"Document not found: {normalized}")
    return target


def safe_read_text(path: str) -> str:
    return resolve_kb_file(path).read_text(encoding="utf-8")


def normalize_domain_relative(domain: str, path: str) -> str:
    clean = path.strip().replace("\\", "/")
    if clean.startswith("knowledge_base/"):
        clean = clean[len("knowledge_base/") :]
    if clean.startswith(f"{domain}/"):
        clean = clean[len(domain) + 1 :]
    if clean.startswith("/") or clean.startswith("../") or "/../" in clean or clean == "..":
        raise HTTPException(status_code=403, detail="Path traversal is not allowed")
    return normalize_kb_path(f"{domain}/{clean}")
