from __future__ import annotations

import re
from collections import Counter, defaultdict
from pathlib import Path

from .config import KB_DIR
from .documents import extract_title
from .schemas import PaperListItem, PaperTag, PaperTagFacet, PaperTagOption
from .security import available_domains, validate_domain


FACET_LABELS = {
    "domain": "Domain",
    "method_tags": "Method",
    "task_tags": "Task",
    "component_tags": "Component",
    "benchmark_tags": "Benchmark",
    "data_tags": "Data",
    "robot_tags": "Robot",
    "application_tags": "Application",
    "year_tags": "Year",
}

FACET_ORDER = list(FACET_LABELS)

PREFERRED_METHOD_TAGS = [
    "VLM + Action Token",
    "VLM + Diffusion/Flow Head",
    "Transformer + Diffusion Head",
    "Latent Action Pretraining",
    "Human Data Pretraining",
    "Hierarchical VLA",
    "World Model + VLA",
    "VLA RL Post-training",
    "Lightweight VLA",
    "VLA Reasoning",
]

METHOD_ALIASES = {
    "flow matching": "VLM + Diffusion/Flow Head",
    "diffusion/flow": "VLM + Diffusion/Flow Head",
    "diffusion head": "Transformer + Diffusion Head",
    "action token": "VLM + Action Token",
    "latent action": "Latent Action Pretraining",
    "human data": "Human Data Pretraining",
    "human video": "Human Data Pretraining",
    "hierarchical": "Hierarchical VLA",
    "world model": "World Model + VLA",
    "world-action": "World Model + VLA",
    "wam": "World Model + VLA",
    "后训练": "VLA RL Post-training",
    "post-training": "VLA RL Post-training",
    "lightweight": "Lightweight VLA",
    "reasoning": "VLA Reasoning",
}

PREFERRED_BENCHMARK_TAGS = [
    "LIBERO",
    "ALOHA",
    "CALVIN",
    "RLBench",
    "RoboCasa",
    "SimplerEnv",
    "DROID",
    "BridgeData V2",
    "Open X-Embodiment",
    "real-robot",
]

TAG_FIELD_ALIASES = {
    "domain": "domain",
    "method": "method_tags",
    "methods": "method_tags",
    "method_tags": "method_tags",
    "task": "task_tags",
    "tasks": "task_tags",
    "task_tags": "task_tags",
    "component": "component_tags",
    "components": "component_tags",
    "component_tags": "component_tags",
    "benchmark": "benchmark_tags",
    "benchmarks": "benchmark_tags",
    "benchmark_tags": "benchmark_tags",
    "data": "data_tags",
    "data_tags": "data_tags",
    "robot": "robot_tags",
    "robots": "robot_tags",
    "robot_tags": "robot_tags",
    "application": "application_tags",
    "application_tags": "application_tags",
    "custom_tags": "application_tags",
    "tags": "application_tags",
    "year": "year_tags",
    "year_tags": "year_tags",
}


def normalize_tag_key(facet: str, label: str) -> str:
    normalized = re.sub(r"\s+", "-", label.strip().lower())
    normalized = re.sub(r"[/\\]+", "-", normalized)
    normalized = re.sub(r"[\[\](),;:]+", "-", normalized)
    normalized = re.sub(r"-{2,}", "-", normalized).strip("-")
    return f"{facet}:{normalized or label.strip().lower()}"


def _tag(facet: str, label: str) -> PaperTag | None:
    label = re.sub(r"\s+", " ", label).strip().strip("`*_")
    if not label or label.lower() in {"none", "unknown", "n/a", "na"}:
        return None
    return PaperTag(facet=facet, label=label, key=normalize_tag_key(facet, label))


def _add_tag(tags: list[PaperTag], seen: set[str], facet: str, label: str) -> None:
    tag = _tag(facet, label)
    if tag and tag.key not in seen:
        tags.append(tag)
        seen.add(tag.key)


def _extract_field(content: str, names: list[str]) -> str:
    for name in names:
        pattern = rf"(?:-+\s*)?(?:\*{{0,2}}{re.escape(name)}\*{{0,2}})\s*[：:]\s*(.+)"
        match = re.search(pattern, content, re.IGNORECASE)
        if match:
            return match.group(1).strip().strip("*")
    return ""


def _split_values(value: str) -> list[str]:
    value = value.strip()
    if value.startswith("[") and value.endswith("]"):
        value = value[1:-1]
    value = value.replace("；", ";").replace("，", ",")
    parts = re.split(r"\s*[,;]\s*", value)
    return [part.strip().strip("\"'") for part in parts if part.strip().strip("\"'")]


def _short_value(value: str) -> str:
    value = re.split(r"[；;。]\s*", value.strip(), maxsplit=1)[0]
    value = re.split(r"[（(]\s*", value, maxsplit=1)[0]
    return value.strip()


def _method_values(value: str) -> list[str]:
    lower = value.lower()
    matched = [tag for tag in PREFERRED_METHOD_TAGS if tag.lower() in lower]
    for alias, canonical in METHOD_ALIASES.items():
        if alias in lower and canonical not in matched:
            matched.append(canonical)
    return matched or [_short_value(value)]


def _benchmark_values(value: str) -> list[str]:
    lower = value.lower()
    matched = [tag for tag in PREFERRED_BENCHMARK_TAGS if tag.lower() in lower]
    return matched or [_short_value(item) for item in _split_values(value)]


def _tag_section(content: str) -> str:
    match = re.search(r"^##\s+标签\s*$([\s\S]*?)(?=^##\s+|\Z)", content, re.MULTILINE)
    return match.group(1) if match else ""


def parse_paper_tags(content: str, path: str) -> list[PaperTag]:
    domain = path.split("/", 1)[0]
    tags: list[PaperTag] = []
    seen: set[str] = set()
    _add_tag(tags, seen, "domain", domain)

    section = _tag_section(content)
    for line in section.splitlines():
        match = re.match(r"^\s*-\s*([A-Za-z_]+)\s*[：:]\s*(.+?)\s*$", line)
        if not match:
            continue
        facet = TAG_FIELD_ALIASES.get(match.group(1).strip().lower())
        if not facet:
            continue
        for value in _split_values(match.group(2)):
            _add_tag(tags, seen, facet, value)

    method = _extract_field(content, ["方法线归属", "方法线", "Method line"])
    if method:
        for value in _method_values(method):
            _add_tag(tags, seen, "method_tags", value)

    benchmark = _extract_field(content, ["Benchmark", "Benchmarks"])
    if benchmark:
        for value in _benchmark_values(benchmark):
            _add_tag(tags, seen, "benchmark_tags", value)

    year = extract_paper_year(extract_title(content, path), content)
    if year:
        _add_tag(tags, seen, "year_tags", year)

    return tags


def extract_paper_year(title: str, content: str) -> str | None:
    for text in (title, content[:1200]):
        match = re.search(r"\((20\d{2}|19\d{2})\)|\b(20\d{2}|19\d{2})\b", text)
        if match:
            return next(group for group in match.groups() if group)
    return None


def extract_paper_summary(content: str) -> str:
    match = re.search(r"^##\s+一句话总结\s*$([\s\S]*?)(?=^##\s+|\Z)", content, re.MULTILINE)
    if match:
        return re.sub(r"\s+", " ", match.group(1)).strip()[:360]
    for line in content.splitlines()[1:]:
        stripped = line.strip()
        if stripped and not stripped.startswith("#") and not stripped.startswith("- "):
            return stripped[:360]
    return ""


def _paper_files(domain: str | None = None) -> list[Path]:
    domains = [validate_domain(domain)] if domain else available_domains()
    files: list[Path] = []
    for item in domains:
        papers_dir = KB_DIR / item / "papers"
        if papers_dir.exists():
            files.extend(path for path in papers_dir.glob("*.md") if path.name != "index.md")
    return sorted(files, key=lambda path: path.relative_to(KB_DIR).as_posix())


def _paper_item(path: Path) -> PaperListItem:
    content = path.read_text(encoding="utf-8")
    rel = path.relative_to(KB_DIR).as_posix()
    title = extract_title(content, rel)
    method = _extract_field(content, ["方法线归属", "方法线", "Method line"]) or None
    return PaperListItem(
        path=rel,
        domain=rel.split("/", 1)[0],
        title=title,
        year=extract_paper_year(title, content),
        summary=extract_paper_summary(content),
        method=method,
        tags=parse_paper_tags(content, rel),
        updated_at=path.stat().st_mtime,
    )


def _group_selected_tags(keys: list[str]) -> dict[str, set[str]]:
    grouped: dict[str, set[str]] = defaultdict(set)
    for key in keys:
        if ":" not in key:
            continue
        facet, _ = key.split(":", 1)
        grouped[facet].add(key)
    return grouped


def _matches_tags(item: PaperListItem, selected: dict[str, set[str]]) -> bool:
    if not selected:
        return True
    by_facet: dict[str, set[str]] = defaultdict(set)
    for tag in item.tags:
        by_facet[tag.facet].add(tag.key)
    return all(by_facet.get(facet, set()) & keys for facet, keys in selected.items())


def _matches_query(item: PaperListItem, query: str | None) -> bool:
    if not query:
        return True
    terms = [term.lower() for term in re.split(r"\s+", query.strip()) if term.strip()]
    haystack = " ".join(
        [item.title, item.path, item.summary, item.method or "", *[tag.label for tag in item.tags]]
    ).lower()
    return all(term in haystack for term in terms)


def list_papers(domain: str | None = None, tag_keys: list[str] | None = None, query: str | None = None) -> list[PaperListItem]:
    selected = _group_selected_tags(tag_keys or [])
    items = [_paper_item(path) for path in _paper_files(domain)]
    items = [item for item in items if _matches_tags(item, selected) and _matches_query(item, query)]
    return sorted(items, key=lambda item: item.updated_at, reverse=True)


def list_paper_tag_facets(domain: str | None = None) -> list[PaperTagFacet]:
    counts: dict[str, Counter[str]] = defaultdict(Counter)
    labels: dict[str, str] = {}
    for item in list_papers(domain):
        for tag in item.tags:
            counts[tag.facet][tag.key] += 1
            labels[tag.key] = tag.label

    facets: list[PaperTagFacet] = []
    for facet in FACET_ORDER:
        if not counts.get(facet):
            continue
        options = [
            PaperTagOption(facet=facet, label=labels[key], key=key, count=count)
            for key, count in counts[facet].most_common()
        ]
        facets.append(PaperTagFacet(facet=facet, label=FACET_LABELS[facet], tags=options))
    return facets
