from __future__ import annotations

import re
from pathlib import Path

from fastapi import HTTPException

from .config import KB_DIR
from .schemas import DocumentResponse, SearchResult, TreeNode
from .security import available_domains, normalize_kb_path, resolve_kb_file, validate_domain


def infer_page_type(path: str) -> str:
    parts = path.split("/")
    if len(parts) < 2:
        return "document"
    if len(parts) >= 3 and parts[1] == "papers" and parts[-1] != "index.md":
        return "paper"
    if len(parts) >= 3 and parts[1] == "reports":
        return "report"
    if len(parts) >= 3 and parts[1] == "surveys":
        return "survey"
    if len(parts) >= 3 and parts[1] == "methods":
        return "method"
    if len(parts) >= 3 and parts[1] == "components":
        return "component"
    if len(parts) >= 3 and parts[1] == "tasks":
        return "task"
    if len(parts) >= 3 and parts[1] == "benchmarks":
        return "benchmark"
    if len(parts) >= 3 and parts[1] == "tags":
        return "tag_taxonomy"
    if parts[-1] == "index.md":
        return "index"
    return "document"


def extract_title(content: str, fallback: str) -> str:
    for line in content.splitlines():
        match = re.match(r"^#\s+(.+?)\s*$", line)
        if match:
            return match.group(1).strip()
    return Path(fallback).stem.replace("_", " ")


def list_domains() -> list[str]:
    return available_domains()


def build_tree(domain: str | None = None) -> TreeNode:
    domain = validate_domain(domain)
    root_dir = KB_DIR / domain

    def build_dir(path: Path) -> TreeNode:
        rel = path.relative_to(KB_DIR).as_posix()
        node = TreeNode(name=path.name, path=rel, kind="directory")
        children = []
        for item in sorted(path.iterdir(), key=lambda p: (p.is_file(), p.name.lower())):
            if item.name.startswith("."):
                continue
            if item.is_dir():
                children.append(build_dir(item))
            elif item.suffix == ".md":
                children.append(TreeNode(name=item.name, path=item.relative_to(KB_DIR).as_posix(), kind="document"))
        node.children = children
        return node

    return build_dir(root_dir)


def read_document(path: str) -> DocumentResponse:
    normalized = normalize_kb_path(path)
    target = resolve_kb_file(normalized)
    content = target.read_text(encoding="utf-8")
    stat = target.stat()
    return DocumentResponse(
        path=normalized,
        domain=normalized.split("/", 1)[0],
        page_type=infer_page_type(normalized),
        title=extract_title(content, normalized),
        content=content,
        updated_at=stat.st_mtime,
        size=len(content),
    )


def search_knowledge(query: str, domain: str | None = None, limit: int = 30) -> list[SearchResult]:
    query = query.strip()
    if not query:
        return []
    domain = validate_domain(domain) if domain else None
    roots = [KB_DIR / domain] if domain else [KB_DIR / item for item in list_domains()]
    terms = [term.lower() for term in re.split(r"\s+", query) if term.strip()]
    results: list[SearchResult] = []
    for root in roots:
        if not root.exists():
            continue
        for md_file in sorted(root.rglob("*.md")):
            try:
                content = md_file.read_text(encoding="utf-8")
            except UnicodeDecodeError:
                continue
            haystack = content.lower()
            score = sum(haystack.count(term) for term in terms)
            if score <= 0:
                continue
            first_pos = min((haystack.find(term) for term in terms if haystack.find(term) >= 0), default=0)
            start = max(0, first_pos - 80)
            end = min(len(content), first_pos + 220)
            snippet = re.sub(r"\s+", " ", content[start:end]).strip()
            rel = md_file.relative_to(KB_DIR).as_posix()
            results.append(SearchResult(path=rel, title=extract_title(content, rel), snippet=snippet, score=score))
    results.sort(key=lambda item: (-item.score, item.path))
    return results[:limit]


def recent_documents(domain: str, subdir: str, limit: int = 8) -> list[SearchResult]:
    domain = validate_domain(domain)
    root = KB_DIR / domain / subdir
    if not root.exists():
        return []
    files = [item for item in root.glob("*.md") if item.name != "index.md"]
    files.sort(key=lambda item: item.stat().st_mtime, reverse=True)
    rows = []
    for md_file in files[:limit]:
        content = md_file.read_text(encoding="utf-8")
        rel = md_file.relative_to(KB_DIR).as_posix()
        first_para = ""
        for line in content.splitlines()[1:]:
            line = line.strip()
            if line and not line.startswith("#"):
                first_para = line
                break
        rows.append(SearchResult(path=rel, title=extract_title(content, rel), snippet=first_para[:240], score=1))
    return rows
