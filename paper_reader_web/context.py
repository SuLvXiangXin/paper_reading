from __future__ import annotations

import hashlib
import re
from pathlib import Path

from .config import KB_DIR, MAX_CONTEXT_CHARS
from .documents import extract_title, infer_page_type, search_knowledge
from .schemas import ContextBundle, ContextDocument, ContextSnippet
from .security import normalize_kb_path, resolve_kb_file


ROLE_LABELS = {
    "current_page": "当前页面",
    "current_paper": "当前论文",
    "domain_overview": "领域总览",
    "papers_index": "论文清单",
    "explicit_link": "显式链接",
    "method_line": "方法线",
    "component": "组件",
    "task": "任务",
    "benchmark": "Benchmark",
    "neighbor_paper": "相邻论文",
}


def _add_doc(docs: list[ContextDocument], seen: set[str], path: str, role: str) -> None:
    try:
        normalized = normalize_kb_path(path)
        target = resolve_kb_file(normalized)
    except Exception:
        return
    if normalized in seen:
        return
    content = target.read_text(encoding="utf-8")
    docs.append(ContextDocument(path=normalized, role=role, title=extract_title(content, normalized), size=len(content)))
    seen.add(normalized)


def _resolve_relative_link(page_path: str, href: str) -> str | None:
    if not href or re.match(r"^[a-zA-Z]+:", href) or href.startswith("#"):
        return None
    href = href.split("#", 1)[0].strip()
    if not href.endswith(".md"):
        return None
    domain = page_path.split("/", 1)[0]
    if href.startswith("/"):
        candidate = href.lstrip("/")
        if candidate.startswith("knowledge_base/"):
            candidate = candidate[len("knowledge_base/") :]
        return candidate
    base = Path(page_path).parent
    return (base / href).as_posix()


def _extract_field(content: str, names: list[str]) -> str:
    for name in names:
        pattern = rf"(?:-+\s*)?(?:\*{{0,2}}{re.escape(name)}\*{{0,2}})\s*[：:]\s*(.+)"
        match = re.search(pattern, content, re.IGNORECASE)
        if match:
            return match.group(1).strip().strip("*")
    return ""


def _keywords(*values: str) -> list[str]:
    text = " ".join(v for v in values if v)
    words = re.findall(r"[A-Za-z][A-Za-z0-9_\-.+]{2,}|[\u4e00-\u9fff]{2,}", text)
    stop = {"the", "and", "with", "for", "方法线归属", "benchmark", "none", "unknown"}
    result = []
    for word in words:
        lower = word.lower()
        if lower not in stop and lower not in result:
            result.append(lower)
    return result[:12]


def _match_taxonomy_docs(domain: str, content: str, docs: list[ContextDocument], seen: set[str]) -> None:
    method_line = _extract_field(content, ["方法线归属", "方法线", "Method line"])
    benchmark = _extract_field(content, ["Benchmark", "Benchmarks"])
    task = _extract_field(content, ["任务", "Task"])
    component_text = _extract_field(content, ["关键技术点", "组件", "Components"])
    groups = [
        ("methods", "method_line", method_line),
        ("benchmarks", "benchmark", benchmark),
        ("tasks", "task", task),
        ("components", "component", component_text),
    ]
    for subdir, role, seed in groups:
        terms = _keywords(seed)
        if not terms:
            continue
        root = KB_DIR / domain / subdir
        if not root.exists():
            continue
        candidates: list[tuple[int, str]] = []
        for md_file in sorted(root.glob("*.md")):
            rel = md_file.relative_to(KB_DIR).as_posix()
            text = md_file.read_text(encoding="utf-8")
            title = extract_title(text, rel)
            headline = f"{md_file.stem} {title}".lower()
            body = text[:3000].lower()
            score = sum((4 if term in headline else 0) + body.count(term) for term in terms)
            if score:
                candidates.append((score, rel))
        if candidates:
            _add_doc(docs, seen, sorted(candidates, reverse=True)[0][1], role)


def _neighbor_papers(domain: str, content: str, docs: list[ContextDocument], seen: set[str]) -> None:
    method_line = _extract_field(content, ["方法线归属", "方法线", "Method line"])
    terms = _keywords(method_line, _extract_field(content, ["Benchmark", "Benchmarks"]))
    if not terms:
        return
    papers_dir = KB_DIR / domain / "papers"
    if not papers_dir.exists():
        return
    current_title = extract_title(content, "")
    scored = []
    for md_file in papers_dir.glob("*.md"):
        if md_file.name == "index.md":
            continue
        rel = md_file.relative_to(KB_DIR).as_posix()
        if rel in seen:
            continue
        paper = md_file.read_text(encoding="utf-8")
        if extract_title(paper, rel) == current_title:
            continue
        score = sum(paper.lower().count(term) for term in terms)
        if score:
            scored.append((score, rel))
    for _, rel in sorted(scored, reverse=True)[:3]:
        _add_doc(docs, seen, rel, "neighbor_paper")


def _report_snippets(domain: str, content: str) -> list[ContextSnippet]:
    title = extract_title(content, "")
    arxiv = _extract_field(content, ["arXiv", "链接"])
    terms = _keywords(title, arxiv)[:5]
    snippets: list[ContextSnippet] = []
    if not terms:
        return snippets
    for subdir in ("reports", "surveys"):
        root = KB_DIR / domain / subdir
        if not root.exists():
            continue
        for md_file in sorted(root.glob("*.md")):
            text = md_file.read_text(encoding="utf-8")
            lower = text.lower()
            positions = [lower.find(term) for term in terms if lower.find(term) >= 0]
            if not positions:
                continue
            pos = min(positions)
            snippet = re.sub(r"\s+", " ", text[max(0, pos - 160) : pos + 360]).strip()
            rel = md_file.relative_to(KB_DIR).as_posix()
            snippets.append(
                ContextSnippet(path=rel, role=subdir[:-1], title=extract_title(text, rel), snippet=snippet[:420])
            )
            if len(snippets) >= 4:
                return snippets
    return snippets


def prepare_context(path: str) -> ContextBundle:
    normalized = normalize_kb_path(path)
    target = resolve_kb_file(normalized)
    domain = normalized.split("/", 1)[0]
    page_type = infer_page_type(normalized)
    content = target.read_text(encoding="utf-8")
    docs: list[ContextDocument] = []
    seen: set[str] = set()

    _add_doc(docs, seen, normalized, "current_paper" if page_type == "paper" else "current_page")
    _add_doc(docs, seen, f"{domain}/index.md", "domain_overview")
    if (KB_DIR / domain / "papers" / "index.md").exists():
        _add_doc(docs, seen, f"{domain}/papers/index.md", "papers_index")

    for href in re.findall(r"\[[^\]]+\]\(([^)]+)\)", content):
        rel = _resolve_relative_link(normalized, href)
        if rel:
            _add_doc(docs, seen, rel, "explicit_link")

    if page_type == "paper":
        _match_taxonomy_docs(domain, content, docs, seen)
        _neighbor_papers(domain, content, docs, seen)
        snippets = _report_snippets(domain, content)
    else:
        snippets = []
        title = extract_title(content, normalized)
        for result in search_knowledge(title, domain=domain, limit=3):
            if result.path != normalized and result.path not in seen:
                snippets.append(ContextSnippet(path=result.path, role="search_hit", title=result.title, snippet=result.snippet))

    digest = hashlib.sha256()
    total = 0
    for doc in docs:
        text = resolve_kb_file(doc.path).read_text(encoding="utf-8")
        if total < MAX_CONTEXT_CHARS:
            digest.update(doc.path.encode())
            digest.update(text[: MAX_CONTEXT_CHARS - total].encode("utf-8"))
            total += len(text)
    for snippet in snippets:
        digest.update(snippet.path.encode())
        digest.update(snippet.snippet.encode("utf-8"))

    return ContextBundle(
        page_path=normalized,
        domain=domain,
        page_type=page_type,
        documents=docs[:12],
        snippets=snippets[:6],
        hash=digest.hexdigest()[:16],
    )
