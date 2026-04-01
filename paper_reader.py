#!/usr/bin/env python3
"""Paper Reader Agent — 论文速读工具

使用 Claude API + Tool Use 实现渐进式论文分析。
自动加载领域知识库，生成结构化论文卡片，并更新知识库。

Usage:
    python paper_reader.py read <pdf_path_or_arxiv_url> [--domain DOMAIN]
    python paper_reader.py batch <directory> [--domain DOMAIN]
    python paper_reader.py ask "<question>" [--domain DOMAIN]
    python paper_reader.py survey <paper1> <paper2> ... [--name NAME] [--domain DOMAIN]
    python paper_reader.py report "<topic>" [--papers P1 P2 ...] [--domain DOMAIN]
"""

import os
import sys
import json
import re
import glob
import time
import argparse
from pathlib import Path

import fitz  # PyMuPDF
import requests
import anthropic

# ─── Git Push（自动同步到 GitHub Pages） ─────────────────────────────────────

def _git_push(domain: str = None):
    """将知识库变更 commit 并 push 到 GitHub，触发 Pages 自动部署。"""
    import subprocess
    repo_dir = Path(__file__).parent
    try:
        # 检查是否有变更
        result = subprocess.run(
            ["git", "status", "--porcelain", "knowledge_base/"],
            capture_output=True, text=True, cwd=repo_dir
        )
        if not result.stdout.strip():
            print("  [跳过] 知识库无变更，无需 push")
            return
        print(f"\n{'='*60}")
        print("自动同步到 GitHub Pages...")
        print(f"{'='*60}")
        domain_msg = f" [{domain}]" if domain else ""
        msg = f"Update knowledge base{domain_msg}"
        subprocess.run(["git", "add", "knowledge_base/"], cwd=repo_dir, check=True)
        subprocess.run(["git", "commit", "-m", msg], cwd=repo_dir, check=True)
        subprocess.run(["git", "push", "origin", "master"], cwd=repo_dir, check=True)
        print("  [完成] 已推送，GitHub Actions 将自动部署")
    except subprocess.CalledProcessError as e:
        print(f"  [警告] git push 失败: {e}")

# ─── 配置 ───────────────────────────────────────────────────────────────────

BASE_DIR = Path(__file__).parent
KB_DIR = BASE_DIR / "knowledge_base"
PDF_CACHE_DIR = BASE_DIR / "pdf_cache"

DEFAULT_DOMAIN = "vla"

MODEL = os.environ.get("PAPER_READER_MODEL", "claude-sonnet-4-6")
MAX_TOKENS = 8192
MAX_TOOL_ROUNDS = 15


def get_domain_dir(domain: str = None) -> Path:
    """获取领域知识库目录。"""
    return KB_DIR / (domain or DEFAULT_DOMAIN)


# ─── 工具定义 ────────────────────────────────────────────────────────────────

TOOLS = [
    {
        "name": "read_knowledge",
        "description": "读取知识库中的某个文件。用于了解领域背景、已有方法分类、已分析的论文等。"
                       "可用路径示例: index.md, methods/index.md, methods/vlm_diffusion_head.md, "
                       "papers/index.md, papers/pi0_2024.md, components/action_repr.md, "
                       "reports/index.md 等。"
                       "建议: 先读 index.md 了解全貌，再按需读子文件。",
        "input_schema": {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "知识库内的相对路径，如 'index.md' 或 'methods/vlm_diffusion_head.md'"
                }
            },
            "required": ["path"]
        }
    },
    {
        "name": "update_knowledge",
        "description": "更新或创建知识库中的文件。用于: "
                       "1) 创建新的论文卡片 (papers/xxx.md), "
                       "2) 更新方法分类 (methods/xxx.md), "
                       "3) 更新论文清单 (papers/index.md), "
                       "4) 创建/更新调研报告 (reports/xxx.md), "
                       "5) 更新其他知识文件。"
                       "注意: 更新已有文件时，保留原有内容并追加/修改，不要覆盖。",
        "input_schema": {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "知识库内的相对路径"
                },
                "content": {
                    "type": "string",
                    "description": "文件的完整内容 (Markdown 格式)"
                }
            },
            "required": ["path", "content"]
        }
    },
    {
        "name": "search_papers",
        "description": "在已有论文卡片中搜索关键词。返回匹配的论文卡片内容。",
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "搜索关键词，如 'diffusion policy' 或 'action chunking'"
                }
            },
            "required": ["query"]
        }
    },
    {
        "name": "list_knowledge",
        "description": "列出知识库的目录结构，查看有哪些文件可以读取。",
        "input_schema": {
            "type": "object",
            "properties": {},
            "required": []
        }
    }
]

# ─── System Prompt ───────────────────────────────────────────────────────────

SYSTEM_PROMPT = """\
你是一个机器人学习领域的论文分析专家，专注于 VLA (Vision-Language-Action) 方向。

你的工作流程:
1. 收到一篇论文后，先用 read_knowledge 读取 index.md 了解领域知识全貌
2. 根据论文内容，加载相关的知识子文件（如 methods/xxx.md）
3. 在领域上下文中分析论文，生成结构化卡片
4. 用 update_knowledge 将论文卡片写入 papers/ 目录
5. 更新 papers/index.md 论文清单
6. 如果论文引入了新概念/方法，更新对应的知识文件

论文卡片格式:
```markdown
# 论文名 (年份)

## 基本信息
- 作者: xxx
- 机构: xxx
- arXiv: xxxx.xxxxx

## 一句话总结
xxx

## 问题
解决什么问题?

## 方法
- 方法线归属: (参考知识库中的方法分类)
- 核心 idea: 1-2 句话
- 关键技术点:
  - xxx
  - xxx

## 实验
- Benchmark: xxx
- 主要结果: xxx
- 对比基线: xxx

## 评价
- 优势: xxx
- 局限: xxx
- 对 VLA 领域的贡献: xxx
```

重要原则:
- 总结要精炼，抓核心贡献，不要复述论文的每个细节
- 用你对领域的理解来定位这篇论文，而不是泛泛总结
- 对比已有工作时要具体，说清楚和谁比、有什么不同
- 如果论文提出了新的重要概念，要更新知识库中的相关文件
"""

REPORT_SYSTEM_PROMPT = """\
你是一个机器人学习领域的调研分析专家。你的任务是基于知识库中的已有论文和知识，
围绕一个具体调研问题撰写深度调研报告。

你的工作流程:
1. 先用 read_knowledge 读取 index.md 了解领域知识全貌
2. 用 list_knowledge 查看知识库中有哪些论文和知识文件
3. 根据调研主题，读取所有相关的论文卡片和方法分类文件
4. 综合分析后，用 update_knowledge 将调研报告写入 reports/ 目录
5. 更新 reports/index.md 报告清单

调研报告格式:
```markdown
# {调研问题}

## 背景与动机
为什么要调研这个问题，在领域中的重要性

## 涉及论文
- **论文1** — 关键观点/贡献
- **论文2** — 关键观点/贡献
- ...

## 对比分析
核心差异、各方案的优劣、技术趋势

## 结论与建议
对研究方向选择的具体建议

## 开放问题
尚未解决的、值得进一步追踪的问题
```

重要原则:
- 报告要有深度，不是简单罗列论文，而是交叉对比得出结论
- 给出具体的、可操作的建议，而不是泛泛而谈
- 如果知识库中信息不足以回答某个方面，明确指出
- 用数据和事实说话，引用论文中的具体实验结果
"""

# ─── 工具执行 ────────────────────────────────────────────────────────────────

# 当前活跃的领域目录（在 run_agent 调用前设置）
_active_domain_dir: Path = None


def execute_tool(name: str, input_data: dict) -> str:
    """执行工具调用，返回结果字符串。"""
    if name == "read_knowledge":
        if "path" not in input_data:
            return "错误: read_knowledge 需要 'path' 参数。"
        return _read_knowledge(input_data["path"])
    elif name == "update_knowledge":
        if "path" not in input_data or "content" not in input_data:
            return "错误: update_knowledge 需要 'path' 和 'content' 参数。请重新调用并提供完整参数。"
        return _update_knowledge(input_data["path"], input_data["content"])
    elif name == "search_papers":
        if "query" not in input_data:
            return "错误: search_papers 需要 'query' 参数。"
        return _search_papers(input_data["query"])
    elif name == "list_knowledge":
        return _list_knowledge()
    else:
        return f"未知工具: {name}"


def _read_knowledge(path: str) -> str:
    filepath = _active_domain_dir / path
    if not filepath.exists():
        return f"文件不存在: {path}\n可用文件:\n{_list_knowledge()}"
    try:
        content = filepath.read_text(encoding="utf-8")
        return content if content.strip() else f"文件为空: {path}"
    except Exception as e:
        return f"读取失败: {e}"


def _update_knowledge(path: str, content: str) -> str:
    filepath = _active_domain_dir / path
    filepath.parent.mkdir(parents=True, exist_ok=True)
    try:
        filepath.write_text(content, encoding="utf-8")
        return f"已更新: {path} ({len(content)} 字符)"
    except Exception as e:
        return f"写入失败: {e}"


def _search_papers(query: str) -> str:
    papers_dir = _active_domain_dir / "papers"
    results = []
    query_lower = query.lower()
    if not papers_dir.exists():
        return f"论文目录不存在: {papers_dir.relative_to(KB_DIR)}"
    for md_file in papers_dir.glob("*.md"):
        if md_file.name == "index.md":
            continue
        content = md_file.read_text(encoding="utf-8")
        if query_lower in content.lower():
            # 返回前 500 字符作为摘要
            results.append(f"### {md_file.name}\n{content[:500]}...\n")
    if not results:
        return f"未找到匹配 '{query}' 的论文卡片"
    return "\n".join(results)


def _list_knowledge() -> str:
    lines = []
    for p in sorted(_active_domain_dir.rglob("*.md")):
        rel = p.relative_to(_active_domain_dir)
        size = len(p.read_text(encoding="utf-8"))
        lines.append(f"  {rel} ({size} 字符)")
    return "知识库文件:\n" + "\n".join(lines)


# ─── PDF 处理 ────────────────────────────────────────────────────────────────

def extract_pdf_text(pdf_path: str, max_pages: int = 30) -> str:
    """从 PDF 提取文本。"""
    doc = fitz.open(pdf_path)
    texts = []
    for i, page in enumerate(doc):
        if i >= max_pages:
            texts.append(f"\n[... 剩余 {len(doc) - max_pages} 页已截断 ...]")
            break
        texts.append(page.get_text())
    doc.close()
    full_text = "\n".join(texts)
    # 截断过长的文本（保留约 80K 字符，约 20K token）
    if len(full_text) > 80000:
        full_text = full_text[:80000] + "\n\n[... 文本已截断至 80000 字符 ...]"
    return full_text


def download_arxiv_pdf(arxiv_id: str) -> str:
    """下载 arXiv PDF 到缓存目录。"""
    PDF_CACHE_DIR.mkdir(parents=True, exist_ok=True)
    pdf_path = PDF_CACHE_DIR / f"{arxiv_id.replace('/', '_')}.pdf"
    if pdf_path.exists():
        print(f"  使用缓存: {pdf_path}")
        return str(pdf_path)

    url = f"https://arxiv.org/pdf/{arxiv_id}.pdf"
    print(f"  下载: {url}")
    resp = requests.get(url, timeout=60)
    resp.raise_for_status()
    pdf_path.write_bytes(resp.content)
    print(f"  已保存: {pdf_path}")
    return str(pdf_path)


def resolve_paper_source(source: str) -> tuple[str, str]:
    """解析输入源，返回 (pdf_path, paper_text)。"""
    # arXiv URL
    arxiv_match = re.search(r'arxiv\.org/(?:abs|pdf)/(\d{4}\.\d{4,5})', source)
    if arxiv_match:
        arxiv_id = arxiv_match.group(1)
        pdf_path = download_arxiv_pdf(arxiv_id)
        return pdf_path, extract_pdf_text(pdf_path)

    # 纯 arXiv ID
    if re.match(r'^\d{4}\.\d{4,5}$', source):
        pdf_path = download_arxiv_pdf(source)
        return pdf_path, extract_pdf_text(pdf_path)

    # 本地 PDF 文件
    if os.path.isfile(source) and source.endswith('.pdf'):
        return source, extract_pdf_text(source)

    raise ValueError(f"无法识别的输入: {source}\n支持: arXiv URL, arXiv ID, 或本地 PDF 路径")


# ─── Semantic Scholar API ────────────────────────────────────────────────────

S2_API_BASE = "https://api.semanticscholar.org/graph/v1"
S2_FIELDS = "title,abstract,year,externalIds,citationCount"
S2_REQUEST_INTERVAL = 0.5  # 秒，避免触发频率限制


def _s2_get(url: str, params: dict = None) -> dict | None:
    """调用 Semantic Scholar API，带重试和频率控制。"""
    time.sleep(S2_REQUEST_INTERVAL)
    try:
        resp = requests.get(url, params=params, timeout=30)
        if resp.status_code == 429:
            # 触发频率限制，等待后重试
            print("    Semantic Scholar API 频率限制，等待 10 秒...")
            time.sleep(10)
            resp = requests.get(url, params=params, timeout=30)
        if resp.status_code == 404:
            return None
        resp.raise_for_status()
        return resp.json()
    except requests.RequestException as e:
        print(f"    Semantic Scholar API 请求失败: {e}")
        return None


def fetch_paper_metadata(arxiv_id: str) -> dict | None:
    """获取单篇论文的元数据。"""
    data = _s2_get(f"{S2_API_BASE}/paper/ArXiv:{arxiv_id}", {"fields": S2_FIELDS})
    if not data:
        return None
    return {
        "paperId": data.get("paperId"),
        "title": data.get("title"),
        "abstract": data.get("abstract"),
        "year": data.get("year"),
        "arxiv_id": (data.get("externalIds") or {}).get("ArXiv"),
        "citationCount": data.get("citationCount", 0),
    }


def fetch_references(arxiv_id: str) -> list[dict]:
    """获取一篇论文的参考文献列表。"""
    data = _s2_get(
        f"{S2_API_BASE}/paper/ArXiv:{arxiv_id}/references",
        {"fields": S2_FIELDS, "limit": 500}
    )
    if not data or "data" not in data:
        return []
    results = []
    for item in data["data"]:
        paper = item.get("citedPaper", {})
        if not paper or not paper.get("title"):
            continue
        results.append({
            "paperId": paper.get("paperId"),
            "title": paper.get("title"),
            "abstract": paper.get("abstract"),
            "year": paper.get("year"),
            "arxiv_id": (paper.get("externalIds") or {}).get("ArXiv"),
            "citationCount": paper.get("citationCount", 0),
        })
    return results


def fetch_citations(arxiv_id: str, limit: int = 100) -> list[dict]:
    """获取引用了某篇论文的论文列表。"""
    data = _s2_get(
        f"{S2_API_BASE}/paper/ArXiv:{arxiv_id}/citations",
        {"fields": S2_FIELDS, "limit": limit}
    )
    if not data or "data" not in data:
        return []
    results = []
    for item in data["data"]:
        paper = item.get("citingPaper", {})
        if not paper or not paper.get("title"):
            continue
        results.append({
            "paperId": paper.get("paperId"),
            "title": paper.get("title"),
            "abstract": paper.get("abstract"),
            "year": paper.get("year"),
            "arxiv_id": (paper.get("externalIds") or {}).get("ArXiv"),
            "citationCount": paper.get("citationCount", 0),
        })
    return results


# ─── PDF 引用提取 ────────────────────────────────────────────────────────────

def extract_references_from_text(paper_text: str) -> list[dict]:
    """从论文 PDF 文本中提取 References 部分的引用信息。"""
    # 找到 References 部分
    ref_match = re.search(
        r'\n\s*References?\s*\n', paper_text, re.IGNORECASE
    )
    if not ref_match:
        return []

    ref_text = paper_text[ref_match.end():]

    # 提取 arXiv ID
    arxiv_ids = re.findall(r'arXiv[:\s]*(\d{4}\.\d{4,5})', ref_text, re.IGNORECASE)

    results = []
    seen = set()
    for aid in arxiv_ids:
        if aid not in seen:
            seen.add(aid)
            results.append({"arxiv_id": aid, "source": "pdf_references"})

    return results


# ─── 调研核心逻辑 ────────────────────────────────────────────────────────────

def collect_related_papers(seed_sources: list[str]) -> dict:
    """收集种子论文的相关论文。

    返回:
        {
            "seeds": [{"arxiv_id": ..., "title": ..., ...}],
            "related": {paperId: {"title": ..., "relations": [...], ...}}
        }
    """
    seeds = []
    related = {}  # paperId -> paper_info with relations

    for source in seed_sources:
        print(f"\n  处理种子论文: {source}")

        # 解析来源，获取 arXiv ID
        arxiv_id = None
        arxiv_match = re.search(r'arxiv\.org/(?:abs|pdf)/(\d{4}\.\d{4,5})', source)
        if arxiv_match:
            arxiv_id = arxiv_match.group(1)
        elif re.match(r'^\d{4}\.\d{4,5}$', source):
            arxiv_id = source

        if not arxiv_id:
            # 本地 PDF：只能从文本提取引用
            if os.path.isfile(source) and source.endswith('.pdf'):
                paper_text = extract_pdf_text(source)
                pdf_refs = extract_references_from_text(paper_text)
                seed_info = {"arxiv_id": None, "title": os.path.basename(source), "source_path": source}
                seeds.append(seed_info)
                for ref in pdf_refs:
                    _add_related_from_arxiv(related, ref["arxiv_id"], seed_info["title"], "被引用(PDF提取)")
                continue
            else:
                print(f"    跳过无法识别的输入: {source}")
                continue

        # 获取种子论文元数据
        print(f"    获取元数据 (arXiv:{arxiv_id})...")
        meta = fetch_paper_metadata(arxiv_id)
        seed_info = meta if meta else {"arxiv_id": arxiv_id, "title": f"arXiv:{arxiv_id}"}
        seeds.append(seed_info)

        seed_title = seed_info.get("title", arxiv_id)

        # 从 PDF 提取引用（获取更多 arXiv ID）
        try:
            pdf_path, paper_text = resolve_paper_source(source)
            pdf_refs = extract_references_from_text(paper_text)
            print(f"    PDF 中提取到 {len(pdf_refs)} 个 arXiv 引用")
        except Exception as e:
            print(f"    PDF 引用提取失败: {e}")
            pdf_refs = []

        # Semantic Scholar: 获取参考文献
        print(f"    获取参考文献 (Semantic Scholar)...")
        refs = fetch_references(arxiv_id)
        print(f"    获取到 {len(refs)} 篇参考文献")

        for paper in refs:
            pid = paper.get("paperId")
            if not pid:
                continue
            if pid not in related:
                related[pid] = {**paper, "relations": []}
            related[pid]["relations"].append({
                "seed": seed_title,
                "type": "被引用",
            })

        # Semantic Scholar: 获取引用（谁引用了这篇）
        print(f"    获取引用论文 (Semantic Scholar)...")
        cites = fetch_citations(arxiv_id, limit=100)
        print(f"    获取到 {len(cites)} 篇引用论文")

        for paper in cites:
            pid = paper.get("paperId")
            if not pid:
                continue
            if pid not in related:
                related[pid] = {**paper, "relations": []}
            related[pid]["relations"].append({
                "seed": seed_title,
                "type": "引用了",
            })

        # 补充 PDF 提取的 arXiv ID（Semantic Scholar 可能没覆盖到的）
        s2_arxiv_ids = {p.get("arxiv_id") for p in related.values() if p.get("arxiv_id")}
        for ref in pdf_refs:
            if ref["arxiv_id"] not in s2_arxiv_ids:
                _add_related_from_arxiv(related, ref["arxiv_id"], seed_title, "被引用(PDF提取)")

    # 排除种子论文自身
    seed_arxiv_ids = {s.get("arxiv_id") for s in seeds if s.get("arxiv_id")}
    seed_paper_ids = set()
    for s in seeds:
        if s.get("paperId"):
            seed_paper_ids.add(s["paperId"])

    related = {
        pid: info for pid, info in related.items()
        if pid not in seed_paper_ids and info.get("arxiv_id") not in seed_arxiv_ids
    }

    return {"seeds": seeds, "related": related}


def _add_related_from_arxiv(related: dict, arxiv_id: str, seed_title: str, rel_type: str):
    """通过 arXiv ID 查找并添加一篇相关论文。"""
    meta = fetch_paper_metadata(arxiv_id)
    if meta and meta.get("paperId"):
        pid = meta["paperId"]
        if pid not in related:
            related[pid] = {**meta, "relations": []}
        related[pid]["relations"].append({"seed": seed_title, "type": rel_type})


def sort_related_papers(related: dict) -> list[dict]:
    """按相关度排序：出现次数 > 引用数 > 年份(新优先)。"""
    papers = list(related.values())
    papers.sort(key=lambda p: (
        -len(p.get("relations", [])),
        -(p.get("citationCount") or 0),
        -(p.get("year") or 0),
    ))
    return papers


def generate_survey_document(seeds: list[dict], papers: list[dict], survey_name: str) -> str:
    """生成调研文档的 Markdown 内容（不通过 Agent，直接生成）。"""
    from datetime import date

    lines = [f"# 调研：{survey_name}", ""]

    # 种子论文表
    lines.append("## 种子论文")
    lines.append("| 论文 | arXiv ID | 年份 |")
    lines.append("|------|----------|------|")
    for s in seeds:
        title = s.get("title", "未知")
        aid = s.get("arxiv_id", "-")
        year = s.get("year", "-")
        lines.append(f"| {title} | {aid} | {year} |")
    lines.append("")

    # 分组：高相关（多篇种子相关）和普通相关
    high = [p for p in papers if len(p.get("relations", [])) > 1]
    normal = [p for p in papers if len(p.get("relations", [])) == 1]

    lines.append("## 待总结论文")
    lines.append("")

    idx = 1
    if high:
        lines.append("### 高相关（与多篇种子论文相关）")
        lines.append("")
        for p in high:
            idx = _append_paper_entry(lines, p, idx)
        lines.append("")

    if normal:
        lines.append("### 相关论文")
        lines.append("")
        for p in normal:
            idx = _append_paper_entry(lines, p, idx)
        lines.append("")

    # 统计信息
    lines.append("---")
    lines.append(f"生成时间: {date.today().isoformat()}")
    lines.append(f"种子论文数: {len(seeds)}")
    lines.append(f"相关论文数: {len(papers)}")

    return "\n".join(lines)


def _append_paper_entry(lines: list[str], paper: dict, idx: int) -> int:
    """往文档中追加一条论文条目。"""
    title = paper.get("title", "未知")
    year = paper.get("year", "")
    year_str = f" ({year})" if year else ""

    lines.append(f"#### {idx}. {title}{year_str}")
    if paper.get("arxiv_id"):
        lines.append(f"- **arXiv**: {paper['arxiv_id']}")
    if paper.get("abstract"):
        abstract = paper["abstract"].replace("\n", " ").strip()
        if len(abstract) > 300:
            abstract = abstract[:300] + "..."
        lines.append(f"- **摘要**: {abstract}")

    # 关系描述
    relations = paper.get("relations", [])
    if relations:
        rel_parts = []
        for r in relations:
            rel_parts.append(f"{r['type']} {r['seed']}")
        lines.append(f"- **关系**: {'; '.join(rel_parts)}")

    if paper.get("citationCount"):
        lines.append(f"- **引用数**: {paper['citationCount']}")
    lines.append(f"- **状态**: 🔲 待总结")
    lines.append("")
    return idx + 1


def update_surveys_index(survey_name: str, seeds: list[dict], paper_count: int, domain: str = None):
    """更新 surveys/index.md。"""
    from datetime import date

    surveys_dir = get_domain_dir(domain) / "surveys"
    index_path = surveys_dir / "index.md"
    surveys_dir.mkdir(parents=True, exist_ok=True)

    seed_names = ", ".join(s.get("title", s.get("arxiv_id", "?"))[:30] for s in seeds)
    new_row = f"| [{survey_name}]({survey_name}.md) | {seed_names} | {paper_count} | {date.today().isoformat()} |"

    if index_path.exists():
        content = index_path.read_text(encoding="utf-8")
        # 检查是否已有这个调研
        if f"[{survey_name}]" in content:
            # 更新已有行
            lines = content.split("\n")
            new_lines = []
            for line in lines:
                if f"[{survey_name}]" in line:
                    new_lines.append(new_row)
                else:
                    new_lines.append(line)
            content = "\n".join(new_lines)
        else:
            content = content.rstrip() + "\n" + new_row + "\n"
    else:
        content = (
            "# 论文调研清单\n\n"
            "| 调研主题 | 种子论文 | 相关论文数 | 创建时间 |\n"
            "|----------|---------|-----------|----------|\n"
            f"{new_row}\n"
        )

    index_path.write_text(content, encoding="utf-8")
    print(f"  已更新: surveys/index.md")


def update_reports_index(report_name: str, topic: str, domain: str = None):
    """更新 reports/index.md。"""
    from datetime import date

    reports_dir = get_domain_dir(domain) / "reports"
    index_path = reports_dir / "index.md"
    reports_dir.mkdir(parents=True, exist_ok=True)

    new_row = f"| [{topic}]({report_name}.md) | {date.today().isoformat()} |"

    if index_path.exists():
        content = index_path.read_text(encoding="utf-8")
        if f"[{topic}]" in content:
            # 已存在，更新日期
            lines = content.split("\n")
            new_lines = []
            for line in lines:
                if f"[{topic}]" in line:
                    new_lines.append(new_row)
                else:
                    new_lines.append(line)
            content = "\n".join(new_lines)
        else:
            content = content.rstrip() + "\n" + new_row + "\n"
    else:
        content = (
            "# 调研报告\n\n"
            "| 报告主题 | 创建时间 |\n"
            "|----------|----------|\n"
            f"{new_row}\n"
        )

    index_path.write_text(content, encoding="utf-8")


# ─── Agent 核心循环 ──────────────────────────────────────────────────────────

def run_agent(user_message: str, paper_text: str = None,
              system_prompt: str = None, domain: str = None) -> str:
    """运行 Agent，返回最终回复。"""
    global _active_domain_dir
    _active_domain_dir = get_domain_dir(domain)
    _active_domain_dir.mkdir(parents=True, exist_ok=True)

    client = anthropic.Anthropic()  # 从环境变量读取 API key 和 base URL

    messages = []

    # 如果有论文文本，作为第一条消息提供
    if paper_text:
        messages.append({
            "role": "user",
            "content": f"请分析以下论文，生成论文卡片并更新知识库。\n\n"
                       f"<paper>\n{paper_text}\n</paper>\n\n"
                       f"{user_message}"
        })
    else:
        messages.append({
            "role": "user",
            "content": user_message
        })

    final_text = ""
    active_system_prompt = system_prompt or SYSTEM_PROMPT

    for round_num in range(MAX_TOOL_ROUNDS):
        print(f"  [Round {round_num + 1}] 调用模型...")

        response = client.messages.create(
            model=MODEL,
            max_tokens=MAX_TOKENS,
            system=active_system_prompt,
            tools=TOOLS,
            messages=messages
        )

        # 处理响应 — 将 pydantic 对象转为 dict 以避免序列化问题
        assistant_content = response.content
        assistant_content_dicts = []
        tool_calls = []
        text_blocks = []
        for block in assistant_content:
            if block.type == "tool_use":
                assistant_content_dicts.append({
                    "type": "tool_use",
                    "id": block.id,
                    "name": block.name,
                    "input": block.input
                })
                tool_calls.append(block)
            elif block.type == "text":
                assistant_content_dicts.append({
                    "type": "text",
                    "text": block.text
                })
                text_blocks.append(block)

        messages.append({"role": "assistant", "content": assistant_content_dicts})

        # 收集文本输出
        for tb in text_blocks:
            final_text += tb.text + "\n"

        if not tool_calls:
            # 没有工具调用，Agent 完成
            print(f"  [完成] 共 {round_num + 1} 轮")
            break

        # 执行工具调用
        tool_results = []
        for tc in tool_calls:
            print(f"    → {tc.name}({json.dumps(tc.input, ensure_ascii=False)[:80]})")
            result = execute_tool(tc.name, tc.input)
            tool_results.append({
                "type": "tool_result",
                "tool_use_id": tc.id,
                "content": result
            })

        messages.append({"role": "user", "content": tool_results})

    return final_text.strip()


# ─── 命令行接口 ──────────────────────────────────────────────────────────────

def cmd_read(source: str, extra_prompt: str = "", domain: str = None, no_sync: bool = False):
    """读取并分析一篇论文。"""
    domain = domain or DEFAULT_DOMAIN
    print(f"\n{'='*60}")
    print(f"分析论文: {source} (领域: {domain})")
    print(f"{'='*60}\n")

    print("1. 提取论文文本...")
    pdf_path, paper_text = resolve_paper_source(source)
    print(f"   提取完成: {len(paper_text)} 字符\n")

    print("2. Agent 分析中...")
    prompt = extra_prompt or "请分析这篇论文，生成论文卡片，并更新知识库。"
    result = run_agent(prompt, paper_text, domain=domain)

    print(f"\n{'='*60}")
    print("分析结果:")
    print(f"{'='*60}\n")
    print(result)

    if not no_sync:
        _git_push(domain=domain)

    return result


def cmd_batch(directory: str, domain: str = None, no_sync: bool = False):
    """批量处理目录下的所有 PDF。"""
    pdf_files = sorted(glob.glob(os.path.join(directory, "*.pdf")))
    if not pdf_files:
        print(f"目录 {directory} 中没有 PDF 文件")
        return

    print(f"找到 {len(pdf_files)} 个 PDF 文件\n")
    for i, pdf_path in enumerate(pdf_files, 1):
        print(f"\n[{i}/{len(pdf_files)}] {os.path.basename(pdf_path)}")
        try:
            cmd_read(pdf_path, domain=domain, no_sync=True)  # 单篇不触发同步
        except Exception as e:
            print(f"  错误: {e}")
            continue

    if not no_sync:
        print(f"\n批量分析完成，开始推送...")
        _git_push(domain=domain)


def cmd_ask(question: str, domain: str = None):
    """基于知识库回答问题。"""
    print(f"\n问题: {question}\n")
    result = run_agent(f"请基于知识库回答以下问题:\n\n{question}", domain=domain)
    print(f"\n回答:\n{result}")
    return result


def cmd_survey(sources: list[str], name: str = None, domain: str = None):
    """调研相关论文：收集种子论文的引用和被引，生成待总结列表。"""
    domain = domain or DEFAULT_DOMAIN
    print(f"\n{'='*60}")
    print(f"论文调研 (领域: {domain})")
    print(f"种子论文: {', '.join(sources)}")
    print(f"{'='*60}\n")

    # 1. 收集相关论文
    print("1. 收集相关论文...")
    result = collect_related_papers(sources)
    seeds = result["seeds"]
    related = result["related"]

    # 2. 排序
    print(f"\n2. 整理结果 (共 {len(related)} 篇相关论文)...")
    sorted_papers = sort_related_papers(related)

    # 3. 生成调研名称
    if not name:
        # 从种子论文标题生成
        seed_titles = [s.get("title", s.get("arxiv_id", "unknown")) for s in seeds]
        # 简单取第一篇论文名的前几个词
        first_title = seed_titles[0].split()[:3]
        name = "_".join(first_title).lower().replace(":", "").replace(",", "")

    # 4. 生成调研文档
    surveys_dir = get_domain_dir(domain) / "surveys"
    print(f"\n3. 生成调研文档: surveys/{name}.md")
    doc_content = generate_survey_document(seeds, sorted_papers, name)

    # 5. 写入文件
    surveys_dir.mkdir(parents=True, exist_ok=True)
    doc_path = surveys_dir / f"{name}.md"
    doc_path.write_text(doc_content, encoding="utf-8")
    print(f"   已保存: {doc_path}")

    # 6. 更新索引
    update_surveys_index(name, seeds, len(sorted_papers), domain=domain)

    # 7. 输出摘要
    high_count = sum(1 for p in sorted_papers if len(p.get("relations", [])) > 1)
    print(f"\n{'='*60}")
    print(f"调研完成!")
    print(f"  种子论文: {len(seeds)} 篇")
    print(f"  相关论文: {len(sorted_papers)} 篇 (高相关: {high_count})")
    print(f"  文档路径: {doc_path}")
    print(f"{'='*60}\n")

    return doc_content


def _extract_paper_metadata(content: str, paper_id: str) -> dict:
    """从论文卡片中提取元数据和引用关系。"""
    meta = {"id": paper_id, "title": "", "year": "", "method_line": "", "refs": []}

    # 提取标题
    title_match = re.match(r'^#\s+(.+)', content)
    if title_match:
        meta["title"] = title_match.group(1)

    # 提取年份（从 paper_id 或标题中）
    year_match = re.search(r'(\d{4})', paper_id)
    if year_match:
        meta["year"] = year_match.group(1)

    # 提取方法线归属（支持加粗格式: **方法线归属**: xxx）
    method_match = re.search(r'\*{0,2}方法线归属\*{0,2}[：:]\s*\*{0,2}(.+?)(?:\*{2})?(?:\s*[（(]|$)', content, re.MULTILINE)
    if method_match:
        meta["method_line"] = method_match.group(1).strip().strip('*')

    # 提取对其他论文卡片的 markdown 链接引用
    card_refs = re.findall(r'(?:papers|methods)/(\w+)\.md', content)
    meta["refs"] = list(set(r for r in card_refs if r != paper_id))

    # 存储小写全文用于别名匹配
    meta["_content_lower"] = content.lower()

    return meta


# 已知论文名称 → paper_id 的别名映射
_PAPER_ALIASES = {
    "rt-2": "rt2_2023", "rt2": "rt2_2023",
    "diffusion policy": "diffusion_policy_2023",
    "octo": "octo_2024",
    "openvla": "openvla_2024",
    "π0": "pi0_2024", "pi0": "pi0_2024", "π₀": "pi0_2024",
    "π0.5": "pi05_2025", "pi0.5": "pi05_2025", "π₀.5": "pi05_2025",
}


def _build_citation_edges(papers: dict) -> list[tuple]:
    """构建引用边: (from_paper, to_paper, relation_type)。"""
    edges = set()
    known_ids = set(papers.keys())

    for pid, meta in papers.items():
        # 从 markdown 链接引用
        for ref in meta["refs"]:
            if ref in known_ids and ref != pid:
                edges.add((pid, ref, "references"))

        # 从文本中查找其他论文的名称引用
        # 读取论文卡片全文（已在 meta 外的 content 中）
        # 这里用已知别名在方法线归属和关系描述中搜索

    # 补充：从文本内容中通过别名匹配查找引用
    for pid, meta in papers.items():
        for alias, target_id in _PAPER_ALIASES.items():
            if target_id == pid or target_id not in known_ids:
                continue
            # 在方法线归属和关系描述区域搜索
            search_text = meta.get("_content_lower", "")
            if alias.lower() in search_text:
                edges.add((pid, target_id, "references"))

    # 过滤不合理的引用（论文不能引用比自己更新的论文）
    filtered = set()
    for src, dst, rel in edges:
        src_year = int(papers[src].get("year") or "9999")
        dst_year = int(papers[dst].get("year") or "0")
        if src_year >= dst_year:
            filtered.add((src, dst, rel))

    return list(filtered)


def _generate_mermaid_graph(papers: dict, edges: list) -> str:
    """生成包含 Mermaid 图谱的 Markdown 文档。"""
    lines = ["# 论文引用图谱", ""]

    # Mermaid 图
    lines.append("```mermaid")
    lines.append("graph TD")
    lines.append("")

    # 按方法线分组，定义节点
    method_groups = {}
    for pid, meta in papers.items():
        short_title = meta["title"].split("(")[0].strip()
        if len(short_title) > 35:
            short_title = short_title[:32] + "..."
        year = meta.get("year", "")
        method = meta.get("method_line", "")[:30]

        lines.append(f'    {pid}["{short_title}<br/>{year}"]')

        key = method or "其他"
        method_groups.setdefault(key, []).append(pid)

    lines.append("")

    # 添加边
    for src, dst, rel_type in edges:
        if rel_type == "references":
            lines.append(f"    {dst} --> {src}")
        else:
            lines.append(f"    {dst} -.-> {src}")

    # 添加方法线样式
    lines.append("")
    style_colors = ["#4CAF50", "#2196F3", "#FF9800", "#9C27B0", "#F44336"]
    for i, (method, pids) in enumerate(method_groups.items()):
        color = style_colors[i % len(style_colors)]
        class_name = f"method{i}"
        lines.append(f"    classDef {class_name} fill:{color},color:#fff,stroke:#333")
        lines.append(f"    class {','.join(pids)} {class_name}")

    lines.append("```")
    lines.append("")

    # 方法线分类表
    lines.append("## 方法线分类")
    lines.append("")
    lines.append("| 论文 | 年份 | 方法线 |")
    lines.append("|------|------|--------|")
    for pid, meta in sorted(papers.items(), key=lambda x: x[1].get("year", "")):
        title = meta["title"][:50]
        year = meta.get("year", "-")
        method = meta.get("method_line", "-")[:40]
        lines.append(f"| {title} | {year} | {method} |")

    lines.append("")

    # 时间线
    lines.append("## 时间线")
    lines.append("")
    for pid, meta in sorted(papers.items(), key=lambda x: x[1].get("year", "")):
        year = meta.get("year", "?")
        method = meta.get("method_line", "")
        refs_to = [e[1] for e in edges if e[0] == pid]
        ref_str = f" ← 基于 {', '.join(refs_to)}" if refs_to else ""
        lines.append(f"- **{year}** {meta['title'][:60]}{ref_str}")

    return "\n".join(lines)


def cmd_graph(domain: str = None, output: str = None):
    """生成论文引用图谱。"""
    domain = domain or DEFAULT_DOMAIN
    domain_dir = get_domain_dir(domain)
    papers_dir = domain_dir / "papers"

    print(f"\n{'='*60}")
    print(f"生成论文引用图谱 (领域: {domain})")
    print(f"{'='*60}\n")

    if not papers_dir.exists():
        print(f"论文目录不存在: {papers_dir}")
        return

    # 1. 解析所有论文卡片
    papers = {}
    for md_file in sorted(papers_dir.glob("*.md")):
        if md_file.name == "index.md":
            continue
        content = md_file.read_text(encoding="utf-8")
        paper_id = md_file.stem
        papers[paper_id] = _extract_paper_metadata(content, paper_id)
        print(f"  解析: {paper_id} ({papers[paper_id]['title'][:40]})")

    if not papers:
        print("没有找到论文卡片")
        return

    # 2. 构建引用边
    edges = _build_citation_edges(papers)
    print(f"\n  发现 {len(edges)} 条引用关系")

    # 3. 生成图谱文档
    graph_md = _generate_mermaid_graph(papers, edges)

    # 4. 写入文件
    output_path = Path(output) if output else domain_dir / "graph.md"
    output_path.write_text(graph_md, encoding="utf-8")
    print(f"\n  图谱已生成: {output_path}")
    print(f"  论文数: {len(papers)}, 引用关系数: {len(edges)}")


def cmd_report(topic: str, papers: list[str] = None, domain: str = None):
    """生成调研报告：基于知识库围绕一个主题做交叉分析。"""
    domain = domain or DEFAULT_DOMAIN
    print(f"\n{'='*60}")
    print(f"生成调研报告 (领域: {domain})")
    print(f"主题: {topic}")
    if papers:
        print(f"指定论文: {', '.join(papers)}")
    print(f"{'='*60}\n")

    # 构建 prompt
    prompt_parts = [f"请围绕以下调研主题撰写深度调研报告:\n\n主题: {topic}"]

    if papers:
        prompt_parts.append("\n指定参考的论文卡片:")
        for p in papers:
            prompt_parts.append(f"  - papers/{p}.md")

    prompt_parts.append(
        "\n\n请先阅读知识库中的相关内容，然后生成报告并保存到 reports/ 目录。"
        "\n报告文件名建议使用简短的英文名。"
        "\n完成后请更新 reports/index.md。"
    )

    prompt = "\n".join(prompt_parts)

    print("Agent 分析中...")
    result = run_agent(prompt, system_prompt=REPORT_SYSTEM_PROMPT, domain=domain)

    # 同时在本地更新 reports/index.md（Agent 可能已经做了，这里做兜底）
    # 不重复更新——检查 Agent 是否已写入
    reports_dir = get_domain_dir(domain) / "reports"
    index_path = reports_dir / "index.md"
    if index_path.exists():
        content = index_path.read_text(encoding="utf-8")
        if topic not in content:
            # Agent 没更新，手动补上
            report_name = re.sub(r'[^\w\s-]', '', topic).strip().replace(' ', '_').lower()
            update_reports_index(report_name, topic, domain=domain)

    print(f"\n{'='*60}")
    print("报告生成完成!")
    print(f"{'='*60}\n")
    print(result)
    return result


def main():
    parser = argparse.ArgumentParser(description="Paper Reader Agent — 论文速读工具")
    subparsers = parser.add_subparsers(dest="command", help="子命令")

    # read 命令
    p_read = subparsers.add_parser("read", help="分析一篇论文")
    p_read.add_argument("source", help="PDF 路径、arXiv URL 或 arXiv ID")
    p_read.add_argument("--prompt", default="", help="额外的分析要求")
    p_read.add_argument("--domain", default=DEFAULT_DOMAIN, help=f"领域 (默认: {DEFAULT_DOMAIN})")
    p_read.add_argument("--no-sync", action="store_true", help="跳过 git push")

    # batch 命令
    p_batch = subparsers.add_parser("batch", help="批量分析目录下的 PDF")
    p_batch.add_argument("directory", help="PDF 目录路径")
    p_batch.add_argument("--domain", default=DEFAULT_DOMAIN, help=f"领域 (默认: {DEFAULT_DOMAIN})")
    p_batch.add_argument("--no-sync", action="store_true", help="跳过 git push")

    # ask 命令
    p_ask = subparsers.add_parser("ask", help="基于知识库回答问题")
    p_ask.add_argument("question", help="问题")
    p_ask.add_argument("--domain", default=DEFAULT_DOMAIN, help=f"领域 (默认: {DEFAULT_DOMAIN})")

    # survey 命令
    p_survey = subparsers.add_parser("survey", help="调研相关论文，生成待总结列表")
    p_survey.add_argument("sources", nargs="+", help="种子论文 (arXiv ID、URL 或本地 PDF)")
    p_survey.add_argument("--name", default=None, help="调研主题名称 (用于文件命名)")
    p_survey.add_argument("--domain", default=DEFAULT_DOMAIN, help=f"领域 (默认: {DEFAULT_DOMAIN})")

    # report 命令
    p_report = subparsers.add_parser("report", help="生成调研报告（基于知识库的交叉分析）")
    p_report.add_argument("topic", help="调研主题/问题")
    p_report.add_argument("--papers", nargs="*", help="指定论文卡片名（可选，如 pi0_2024 openvla_2024）")
    p_report.add_argument("--domain", default=DEFAULT_DOMAIN, help=f"领域 (默认: {DEFAULT_DOMAIN})")

    # graph 命令
    p_graph = subparsers.add_parser("graph", help="生成论文引用图谱")
    p_graph.add_argument("--domain", default=DEFAULT_DOMAIN, help=f"领域 (默认: {DEFAULT_DOMAIN})")
    p_graph.add_argument("--output", default=None, help="输出路径（默认: knowledge_base/<domain>/graph.md）")

    args = parser.parse_args()

    if args.command == "read":
        cmd_read(args.source, args.prompt, domain=args.domain, no_sync=args.no_sync)
    elif args.command == "batch":
        cmd_batch(args.directory, domain=args.domain, no_sync=args.no_sync)
    elif args.command == "ask":
        cmd_ask(args.question, domain=args.domain)
    elif args.command == "survey":
        cmd_survey(args.sources, args.name, domain=args.domain)
    elif args.command == "report":
        cmd_report(args.topic, args.papers, domain=args.domain)
    elif args.command == "graph":
        cmd_graph(domain=args.domain, output=args.output)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
